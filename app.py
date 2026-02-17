"""
FlipSide — The dark side of small print.
Upload a document you didn't write. See what the other side intended.

Optimized for Claude Opus 4.6 extended thinking:
- Meta-prompting framework for multi-perspective document analysis
- 32K thinking budget (deep mode) for multi-pass cross-clause reasoning
- Drafter's Playbook: reveals the strategic architecture behind the document
- Phased SSE streaming with real-time phase detection
"""

import os
import re
import uuid
import json
import time
import threading
import queue as queue_module
import base64
from io import BytesIO

from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
import anthropic

from prompts import (
    build_card_scan_prompt,
    build_clause_id_prompt,
    build_single_card_system,
    build_green_summary_user,
    build_archaeology_prompt,
    build_scenario_prompt,
    build_walkaway_prompt,
    build_combinations_prompt,
    build_playbook_prompt,
    build_verdict_prompt,
    build_followup_prompt,
    build_counter_draft_prompt,
    build_timeline_prompt,
)

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['TEMPLATES_AUTO_RELOAD'] = True

documents = {}
_documents_lock = threading.Lock()
DOCUMENT_TTL = 30 * 60  # 30 minutes

def _evict_stale_documents():
    """Remove documents older than DOCUMENT_TTL."""
    now = time.time()
    with _documents_lock:
        stale = [k for k, v in documents.items() if now - v.get('_ts', 0) > DOCUMENT_TTL]
        for k in stale:
            del documents[k]

def store_document(doc_id, doc):
    """Store a document with a timestamp, evicting stale entries first."""
    _evict_stale_documents()
    doc['_ts'] = time.time()
    # Set events BEFORE storing so /analyze can't see doc without them
    doc['_prescan_event'] = threading.Event()
    doc['_precards_event'] = threading.Event()
    with _documents_lock:
        documents[doc_id] = doc
    # Pre-scan + pre-generate cards during upload
    threading.Thread(
        target=_prescan_document, args=(doc_id,), daemon=True
    ).start()


def _prescan_document(doc_id):
    """Background: stream clause identification + start card workers immediately.
    Streams Phase 1 so card workers launch as each CLAUSE: line arrives (~3s each),
    overlapping identification with card generation."""
    doc = documents.get(doc_id)
    if not doc or not doc.get('text'):
        if doc:
            doc['_prescan'] = None
            doc.get('_prescan_event', threading.Event()).set()
            doc.get('_precards_event', threading.Event()).set()
        return
    try:
        import anthropic as _anthropic
        client = _anthropic.Anthropic()
        fast_model = os.environ.get('FLIPSIDE_FAST_MODEL', 'claude-haiku-4-5-20251001')
        user_msg = (
            "Analyze the following document from the drafter's "
            "strategic perspective.\n\n"
            "---BEGIN DOCUMENT---\n\n"
            f"{doc['text']}\n\n"
            "---END DOCUMENT---"
        )

        # Pre-build card system prompt (shared across all parallel workers)
        card_system = build_single_card_system(doc['text'])
        card_results = {}
        card_events = {}
        card_queue = queue_module.Queue()
        clause_preview_queue = queue_module.Queue()
        card_stream_queue = queue_module.Queue()  # streaming chunks
        doc['_card_events'] = card_events
        doc['_card_results'] = card_results
        doc['_card_queue'] = card_queue
        doc['_clause_preview_queue'] = clause_preview_queue
        doc['_card_stream_queue'] = card_stream_queue

        def card_worker(idx, user_content):
            max_retries = 3
            try:
                for attempt in range(max_retries):
                    try:
                        full_text = ''
                        with client.messages.stream(
                            model=fast_model,
                            max_tokens=3000,
                            system=[{
                                'type': 'text',
                                'text': card_system,
                                'cache_control': {'type': 'ephemeral'},
                            }],
                            messages=[{'role': 'user', 'content': user_content}],
                        ) as stream:
                            for chunk in stream.text_stream:
                                full_text += chunk
                                card_stream_queue.put(('chunk', idx, chunk))
                        card_stream_queue.put(('done', idx))
                        card_results[idx] = full_text
                        card_queue.put((idx, full_text))
                        return  # success
                    except Exception as e:
                        is_overloaded = 'overload' in str(e).lower() or '529' in str(e) or '429' in str(e)
                        if is_overloaded and attempt < max_retries - 1:
                            wait = (attempt + 1) * 5  # 5s, 10s
                            print(f'[precard] {doc_id[:8]} card {idx}: Overloaded, retry {attempt+1} in {wait}s')
                            time.sleep(wait)
                            continue
                        print(f'[precard] {doc_id[:8]} card {idx}: Error: {e}')
                        card_results[idx] = ''
                        card_stream_queue.put(('done', idx))
                        card_queue.put((idx, ''))
                        return
            finally:
                card_events[idx].set()

        # ── Phase 1: STREAMING identification scan ──
        # Card workers start as each CLAUSE: line arrives, overlapping with scan
        t0 = time.time()
        scan_text = 'CLAUSE:'  # Prefilled assistant turn
        clauses = []
        clause_idx = 0
        line_buffer = 'CLAUSE:'  # Prefilled assistant turn
        not_applicable = False

        with client.messages.stream(
            model=fast_model,
            max_tokens=2000,
            system=[{
                'type': 'text',
                'text': build_clause_id_prompt(),
                'cache_control': {'type': 'ephemeral'},
            }],
            messages=[
                {'role': 'user', 'content': user_msg},
                {'role': 'assistant', 'content': 'CLAUSE:'},
            ],
        ) as stream:
            for chunk in stream.text_stream:
                scan_text += chunk
                line_buffer += chunk

                # Process complete lines as they arrive
                while '\n' in line_buffer:
                    line, line_buffer = line_buffer.split('\n', 1)
                    stripped = line.strip()

                    if '**Not Applicable**' in stripped:
                        not_applicable = True

                    if stripped.startswith('CLAUSE:'):
                        clause = _parse_clause_line(stripped)
                        if clause:
                            clauses.append(clause)
                            i = clause_idx
                            card_events[i] = threading.Event()
                            card_user_msg = (
                                f"Generate a complete flip card for this specific clause:\n\n"
                                f"Title: {clause['title']}\n"
                                f"Section Reference: {clause.get('section', 'Not specified')}\n"
                                f"Prescan Risk: {clause.get('risk', 'RED')}\n"
                                f"Prescan Trick: {clause.get('trick', '')}\n\n"
                                f"Find this clause in the document and output the COMPLETE flip card. "
                                f"Make your own independent risk assessment — the prescan hints above are guidance only."
                            )
                            threading.Thread(
                                target=card_worker, args=(i, card_user_msg), daemon=True
                            ).start()
                            clause_idx += 1
                            # Push preview for frontend loading screen
                            clause_preview_queue.put({
                                'index': i,
                                'title': clause['title'],
                                'section': clause.get('section', ''),
                            })
                            print(f'[prescan] {doc_id[:8]} clause {i}: '
                                  f'{clause["title"][:40]} — card worker started at '
                                  f'{round(time.time() - t0, 1)}s')

        # Process final line (if no trailing newline)
        if line_buffer.strip().startswith('CLAUSE:'):
            clause = _parse_clause_line(line_buffer.strip())
            if clause:
                clauses.append(clause)
                i = clause_idx
                card_events[i] = threading.Event()
                card_user_msg = (
                    f"Generate a complete flip card for this specific clause:\n\n"
                    f"Title: {clause['title']}\n"
                    f"Section Reference: {clause.get('section', 'Not specified')}\n"
                    f"Prescan Risk: {clause.get('risk', 'RED')}\n"
                    f"Prescan Trick: {clause.get('trick', '')}\n\n"
                    f"Find this clause in the document and output the COMPLETE flip card. "
                    f"Make your own independent risk assessment — the prescan hints above are guidance only."
                )
                threading.Thread(
                    target=card_worker, args=(i, card_user_msg), daemon=True
                ).start()
                clause_idx += 1

        # Parse profile and green text from full scan
        profile_text, _, green_text = parse_identification_output(scan_text)
        scan_seconds = round(time.time() - t0, 1)

        # Green summary card disabled — frontend skips green cards entirely
        total_cards = len(clauses)

        doc['_card_total'] = total_cards
        doc['_prescan'] = {
            'scan_text': scan_text,
            'profile_text': profile_text,
            'clauses': clauses,
            'green_text': green_text,
            'seconds': scan_seconds,
        }
        print(f'[prescan] {doc_id[:8]}: {len(clauses)} clauses in {scan_seconds}s '
              f'(streaming, {clause_idx} workers already running)')
        doc.get('_prescan_event', threading.Event()).set()

        # Wait for all cards (for fast-path / _precards compatibility)
        if clauses and not not_applicable:
            for idx in range(total_cards):
                card_events[idx].wait(timeout=30)

            cards_seconds = round(time.time() - t0 - scan_seconds, 1)
            doc['_precards'] = {
                'cards': [card_results.get(i, '') for i in range(total_cards)],
                'seconds': cards_seconds,
            }
            print(f'[precard] {doc_id[:8]}: {total_cards} cards in {cards_seconds}s '
                  f'(total {round(scan_seconds + cards_seconds, 1)}s)')
        else:
            doc['_precards'] = None

    except Exception as e:
        print(f'[prescan] {doc_id[:8]}: Error: {e}')
        # Preserve any partial prescan data; default to None if absent
        if not doc.get('_prescan'):
            doc['_prescan'] = None
    finally:
        doc.get('_prescan_event', threading.Event()).set()
        doc.get('_precards_event', threading.Event()).set()


def _build_claims_summary(prescan, precards):
    """Build a concise summary of all flagged claims for the Opus verdict prompt.
    Parses pre-generated card texts to extract key findings per clause."""
    if not prescan or not precards:
        return ''
    clauses = prescan.get('clauses', [])
    cards = precards.get('cards', [])
    if not clauses or not cards:
        return ''

    lines = [
        '## PRE-ANALYZED FLAGGED CLAIMS',
        'The card scan identified these flagged clauses. Reference them in your verdict — '
        'ensure [FLAGGED_CLAIMS] covers ALL of them with consumer impact.\n',
    ]
    for i, card_text in enumerate(cards):
        if not card_text or 'Fair Clauses Summary' in card_text:
            continue
        # Extract title from ### heading
        title_match = re.search(r'^###\s+(.+)', card_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f'Clause {i + 1}'
        # Extract risk/score/trick from [RED] · Score: 85/100 · Trick: ...
        risk_match = re.search(
            r'\[(RED|YELLOW|GREEN)\]\s*[·•]\s*Score:\s*(\d+)/100\s*[·•]\s*Trick:\s*(.+)',
            card_text)
        if risk_match:
            risk, score, trick = risk_match.group(1), risk_match.group(2), risk_match.group(3).strip()
        elif i < len(clauses):
            risk, score, trick = clauses[i]['risk'], clauses[i]['score'], clauses[i]['trick']
        else:
            risk, score, trick = '?', '?', 'Unknown'
        # Extract REVEAL, bottom line, FIGURE
        reveal_m = re.search(r'\[REVEAL\]:\s*(.+)', card_text)
        bl_m = re.search(r'\*\*Bottom line:\*\*\s*(.+)', card_text)
        fig_m = re.search(r'\[FIGURE\]:\s*(.+)', card_text)
        reveal = reveal_m.group(1).strip() if reveal_m else ''
        bottom_line = bl_m.group(1).strip() if bl_m else ''
        figure = fig_m.group(1).strip() if fig_m else ''

        lines.append(f'Claim {i + 1}: {title}')
        lines.append(f'  Risk: {risk} | Score: {score}/100 | Trick: {trick}')
        if reveal:
            lines.append(f'  Finding: {reveal}')
        if figure:
            lines.append(f'  Impact: {figure}')
        if bottom_line:
            lines.append(f'  Bottom line: {bottom_line}')
        lines.append('')

    return '\n'.join(lines)


MODEL = os.environ.get('FLIPSIDE_MODEL', 'claude-opus-4-6')
FAST_MODEL = os.environ.get('FLIPSIDE_FAST_MODEL', 'claude-haiku-4-5-20251001')

# Module-level client for utility functions (text cleaning etc.)
_client = None
def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client

PHASE_MARKERS = [
    ('Document Profile', 'profile'),
    ('Clause-by-Clause', 'clauses'),
    ('Cross-Clause', 'interactions'),
    ("Drafter's Playbook", 'playbook'),
    ('Overall Assessment', 'summary'),
]

# ---------------------------------------------------------------------------
# Sample documents (loaded from data/samples.json)
# ---------------------------------------------------------------------------

_samples_path = os.path.join(os.path.dirname(__file__), 'data', 'samples.json')
with open(_samples_path, 'r') as _f:
    SAMPLE_DOCUMENTS = json.load(_f)

# Load sample thumbnails from static directory
SAMPLE_THUMBNAILS = {}
_thumb_dir = os.path.join(os.path.dirname(__file__), 'static')
for _key in SAMPLE_DOCUMENTS:
    _path = os.path.join(_thumb_dir, f'thumb_{_key}.jpg')
    if os.path.exists(_path):
        with open(_path, 'rb') as _f:
            SAMPLE_THUMBNAILS[_key] = base64.b64encode(_f.read()).decode()


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

MAX_VISION_PAGES = 10
VISION_DPI = 150
MAX_IMAGE_DIMENSION = 4000   # px – well under Anthropic's 8000px hard limit
MAX_IMAGE_BYTES = 4 * 1024 * 1024  # 4 MB – under the 5 MB API limit


def _has_garbled_text(text):
    """Fast local check: does this text likely contain reversed segments?

    Counts common function words in original vs reversed version of each line.
    If any line scores better reversed, the text needs cleaning.
    """
    COMMON = {
        'de', 'het', 'van', 'en', 'een', 'voor', 'in', 'te', 'op', 'aan',
        'met', 'bij', 'uit', 'naar', 'dat', 'die', 'niet', 'ook', 'maar',
        'per', 'door', 'tot', 'je', 'zijn', 'kan', 'was',
        'the', 'and', 'for', 'of', 'to', 'is', 'with', 'on', 'at', 'by',
        'not', 'but', 'or', 'this', 'that', 'you', 'your', 'all', 'can',
        'le', 'la', 'les', 'des', 'du', 'un', 'une', 'et', 'est', 'dans',
        'pour', 'par', 'sur', 'avec', 'que', 'qui', 'ce',
        'der', 'die', 'das', 'und', 'ist', 'ein', 'von', 'auf', 'mit',
    }
    def hits(words):
        return sum(1 for w in words
                   if re.sub(r'[^a-zA-Z]', '', w).lower() in COMMON)

    for line in text.split('\n'):
        words = line.split()
        if len(words) < 4:
            continue
        rev_words = line[::-1].split()
        if hits(rev_words) > hits(words) + 1:
            return True
    return False


def clean_extracted_text(text):
    """Use Haiku 4.5 to fix garbled/reversed text from PDF extraction.

    Only calls Haiku when the fast local check detects garbled segments.
    Clean text passes through with zero delay.
    """
    if not text or len(text) < 50:
        return text

    if not _has_garbled_text(text):
        return text  # Clean text — no API call needed

    try:
        result = get_client().messages.create(
            model=FAST_MODEL,
            max_tokens=min(len(text) // 3 + 500, 8192),
            messages=[{'role': 'user', 'content': text}],
            system=(
                'You are a text cleaning tool. The input is extracted from a PDF and may contain '
                'garbled, reversed, or duplicated text segments from complex layouts. '
                'Fix any reversed text (characters in wrong order), remove obvious duplicates, '
                'and clean up extraction artifacts. '
                'Return ONLY the cleaned text — no commentary, no explanations. '
                'If the text looks fine, return it unchanged.'
            ),
        )
        cleaned = result.content[0].text.strip()
        # Sanity check: cleaned text shouldn't be drastically different in length
        if cleaned and 0.3 < len(cleaned) / len(text) < 2.0:
            return cleaned
    except Exception as e:
        print(f'[clean_extracted_text] Haiku cleanup failed, using raw text: {e}')
    return text


def extract_pdf(file_storage):
    import pdfplumber
    from PIL import Image
    pdf_bytes = file_storage.read()
    text_parts = []
    page_images = []
    ocr_used = False
    use_ocr_for_all = None  # None = undecided, True/False after first page test

    def text_quality(t):
        """Score text: fraction of tokens that look like real words."""
        words = t.split()
        if not words:
            return 0
        good = sum(1 for w in words if 2 <= len(w) <= 20 and sum(c.isalpha() for c in w) / max(len(w), 1) > 0.7)
        return good / len(words)

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            pil_img = None
            if i < MAX_VISION_PAGES:
                try:
                    img = page.to_image(resolution=VISION_DPI)
                    pil_img = img.original
                    # Constrain dimensions to stay under API limit
                    if max(pil_img.size) > MAX_IMAGE_DIMENSION:
                        pil_img.thumbnail(
                            (MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION),
                            Image.LANCZOS,
                        )
                    # Encode as JPEG to keep file size bounded
                    buf = BytesIO()
                    pil_img.convert('RGB').save(buf, format='JPEG', quality=80)
                    # If still too large, reduce quality
                    if buf.tell() > MAX_IMAGE_BYTES:
                        buf = BytesIO()
                        pil_img.convert('RGB').save(buf, format='JPEG', quality=50)
                    page_images.append(base64.b64encode(buf.getvalue()).decode())
                except Exception as e:
                    print(f'[extract_pdf] Page image rendering failed: {e}')
                    page_images.append(None)  # Placeholder to keep indices aligned
            # OCR: test on first page, then apply decision to all pages
            if use_ocr_for_all is None and pil_img:
                # First page with an image — test OCR vs embedded text
                try:
                    import pytesseract
                    ocr_text = pytesseract.image_to_string(pil_img)
                    ocr_score = text_quality(ocr_text) if ocr_text else 0
                    orig_score = text_quality(page_text) if page_text else 0
                    use_ocr_for_all = ocr_score > orig_score + 0.05
                    print(f'[extract_pdf] Page 1 quality test: embedded={orig_score:.2f}, OCR={ocr_score:.2f} → {"OCR" if use_ocr_for_all else "embedded"} for all pages')
                    if use_ocr_for_all:
                        page_text = ocr_text
                        ocr_used = True
                except Exception as e:
                    print(f'[extract_pdf] OCR test failed: {e}')
                    use_ocr_for_all = False
            elif use_ocr_for_all:
                # OCR won on first page — OCR this page too
                try:
                    import pytesseract
                    ocr_img = pil_img or page.to_image(resolution=VISION_DPI).original
                    ocr_text = pytesseract.image_to_string(ocr_img)
                    if ocr_text and len(ocr_text.strip()) > len((page_text or '').strip()):
                        page_text = ocr_text
                except Exception as e:
                    print(f'[extract_pdf] OCR failed for page {i+1}: {e}')
            if page_text:
                text_parts.append(page_text)
    if ocr_used:
        print('[extract_pdf] OCR was used for scanned pages')
    # Tag each page so the sidebar can render page dividers
    # and later clauses from page 3+ are matchable
    tagged = []
    for i, part in enumerate(text_parts):
        tagged.append(f'\n\n— Page {i + 1} —\n\n{part}')
    raw_text = ''.join(tagged).strip()
    return clean_extracted_text(raw_text), page_images, ocr_used


def extract_docx(file_storage):
    from docx import Document
    doc = Document(BytesIO(file_storage.read()))
    return '\n\n'.join(p.text for p in doc.paragraphs if p.text.strip())


def extract_image(file_storage):
    """Extract text from a photo/image using Haiku Vision.

    Returns (text, [image_base64]) — text for the pipeline, image for Opus vision.
    """
    from PIL import Image

    img_bytes = file_storage.read()
    img = Image.open(BytesIO(img_bytes))

    # Convert to RGB (handles RGBA PNGs, palette images, etc.)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize if needed (same constraints as PDF page images)
    if max(img.size) > MAX_IMAGE_DIMENSION:
        img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)

    # Encode as JPEG
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=80)
    if buf.tell() > MAX_IMAGE_BYTES:
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=50)

    image_b64 = base64.b64encode(buf.getvalue()).decode()

    # Use Haiku Vision to transcribe the text
    try:
        result = get_client().messages.create(
            model=FAST_MODEL,
            max_tokens=4096,
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/jpeg',
                            'data': image_b64,
                        },
                    },
                    {
                        'type': 'text',
                        'text': (
                            'Transcribe ALL text from this image exactly as written. '
                            'Preserve layout, headings, numbering, bullet points, and paragraph breaks. '
                            'Output only the transcribed text, no commentary or descriptions.'
                        ),
                    },
                ],
            }],
        )
        text = result.content[0].text.strip()
    except Exception as e:
        print(f'[extract_image] Haiku Vision extraction failed: {e}')
        text = ''

    return text, [image_b64]


# ---------------------------------------------------------------------------
# Prompt — optimized for Opus 4.6 extended thinking
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    resp = app.make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-store'
    return resp


@app.route('/jury')
def jury():
    return render_template('jury.html')


@app.route('/upload', methods=['POST'])
def upload():
    try:
        text = ''
        filename = ''
        page_images = []
        ocr_used = False

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

            if ext == 'pdf':
                text, page_images, ocr_used = extract_pdf(file)
            elif ext == 'docx':
                text = extract_docx(file)
            elif ext in ('txt', 'text', 'md'):
                text = file.read().decode('utf-8', errors='replace')
            elif ext in ('jpg', 'jpeg', 'png', 'webp') or (
                file.content_type and file.content_type.startswith('image/')
            ):
                text, page_images = extract_image(file)
            else:
                return jsonify({'error': f'Unsupported file type: .{ext}'}), 400

        elif request.form.get('text', '').strip():
            text = request.form['text']
            filename = 'pasted text'
        else:
            return jsonify({'error': 'No file or text provided.'}), 400

        if not text.strip():
            return jsonify({'error': 'Could not extract text from document.'}), 400

        doc_id = str(uuid.uuid4())

        store_document(doc_id, {
            'text': text,
            'filename': filename,
            'page_images': page_images,
        })

        # Generate a small thumbnail from the first page image
        thumbnail = None
        if page_images:
            try:
                from PIL import Image
                img_bytes = base64.b64decode(page_images[0])
                img = Image.open(BytesIO(img_bytes))
                img.thumbnail((200, 280))
                buf = BytesIO()
                img.save(buf, format='JPEG', quality=50)
                thumbnail = base64.b64encode(buf.getvalue()).decode()
            except Exception:
                pass

        resp = {
            'doc_id': doc_id,
            'filename': filename,
            'text_length': len(text),
            'preview': text[:300],
            'full_text': text,
            'thumbnail': thumbnail,
        }
        if ocr_used:
            resp['ocr_used'] = True
        return jsonify(resp)

    except Exception as e:
        print(f'[upload] Error: {e}')
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


@app.route('/sample', methods=['POST'])
def sample():
    data = request.get_json(silent=True) or {}
    sample_type = data.get('type', 'lease')

    doc = SAMPLE_DOCUMENTS.get(sample_type, SAMPLE_DOCUMENTS['lease'])
    text = doc['text']
    filename = doc['filename']

    doc_id = str(uuid.uuid4())
    doc_store = {
        'text': text,
        'filename': filename,
    }
    if 'doc_context' in doc:
        doc_store['_doc_context'] = doc['doc_context']
    store_document(doc_id, doc_store)

    return jsonify({
        'doc_id': doc_id,
        'filename': filename,
        'text_length': len(text),
        'preview': text[:300],
        'full_text': text,
        'thumbnail': SAMPLE_THUMBNAILS.get(sample_type),
    })


def parse_identification_output(text):
    """Parse Phase 1 identification scan into profile, clauses, and green text."""
    lines = text.strip().split('\n')

    profile_lines = []
    clauses = []
    green_text = ''
    in_profile = False
    profile_ended = False

    for line in lines:
        stripped = line.strip()

        # Start of profile section
        if '## Document Profile' in stripped or (not profile_ended and '**Document Type**' in stripped):
            in_profile = True

        # End of profile section
        if in_profile and (stripped.startswith('CLAUSE:') or stripped.startswith('GREEN_CLAUSES:')
                           or stripped.startswith('**Not Applicable**')):
            in_profile = False
            profile_ended = True

        if in_profile:
            profile_lines.append(line)
            continue

        # Clause lines
        if stripped.startswith('CLAUSE:'):
            clause = _parse_clause_line(stripped)
            if clause:
                clauses.append(clause)

        # Green clauses
        if stripped.startswith('GREEN_CLAUSES:') or stripped.startswith('GREEN:'):
            green_text = stripped.split(':', 1)[1].strip() if ':' in stripped else ''

        # Not Applicable — add to profile
        if '**Not Applicable**' in stripped:
            profile_lines.append(line)

    profile_text = '\n'.join(profile_lines).strip()

    # Ensure profile has header
    if profile_text and '## Document Profile' not in profile_text:
        profile_text = '## Document Profile\n' + profile_text

    return profile_text, clauses, green_text


def _parse_clause_line(line):
    """Parse a single CLAUSE: line into a dict.
    Format: CLAUSE: Title (Section) | RISK: RED | TRICK: Moving Target
    Also handles minimal format without pipe-delimited fields."""
    try:
        content = line[len('CLAUSE:'):].strip()

        # Check for pipe-delimited format
        if '|' in content:
            parts = [p.strip() for p in content.split('|')]
            title_part = parts[0]
        else:
            title_part = content
            parts = [title_part]

        result = {'title': '', 'section': '', 'risk': 'RED', 'trick': ''}

        paren_match = re.search(r'\(([^)]+)\)\s*$', title_part)
        if paren_match:
            result['section'] = paren_match.group(1)
            result['title'] = title_part[:paren_match.start()].strip()
        else:
            result['title'] = title_part

        # Extract RISK and TRICK from pipe-delimited fields
        for part in parts[1:]:
            if part.startswith('RISK:'):
                result['risk'] = part[5:].strip()
            elif part.startswith('TRICK:'):
                result['trick'] = part[6:].strip()

        return result if result['title'] else None
    except Exception as e:
        print(f'[parse_clause] Error: {e} — line: {line[:100]}')
        return None




@app.route('/analyze/<doc_id>')
def analyze(doc_id):
    if doc_id not in documents:
        return jsonify({'error': 'Document not found.'}), 404

    doc = documents[doc_id]

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def process_stream_event(event, state):
        """Process a streaming event. Returns list of SSE chunks."""
        chunks = []
        if event.type == 'content_block_start':
            block = event.content_block
            state['current_block'] = block.type
            if block.type == 'tool_use':
                state['current_tool_name'] = block.name
                state['current_tool_input_json'] = ''
                chunks.append(sse('tool_start', json.dumps({'name': block.name})))
            else:
                chunks.append(sse(f'{block.type}_start'))
        elif event.type == 'content_block_delta':
            if event.delta.type == 'thinking_delta':
                chunks.append(sse('thinking', event.delta.thinking))
            elif event.delta.type == 'text_delta':
                text = event.delta.text
                state['phase_buffer'] += text
                if len(state['phase_buffer']) > 300:
                    state['phase_buffer'] = state['phase_buffer'][-150:]
                for marker, phase_name in PHASE_MARKERS:
                    if (marker in state['phase_buffer']
                            and phase_name not in state['detected_phases']):
                        state['detected_phases'].add(phase_name)
                        chunks.append(sse('phase', phase_name))
                chunks.append(sse('text', text))
            elif event.delta.type == 'input_json_delta':
                state['current_tool_input_json'] += event.delta.partial_json
        elif event.type == 'content_block_stop':
            if state['current_block'] == 'tool_use':
                tool_name = state.get('current_tool_name', '')
                try:
                    tool_input = json.loads(state['current_tool_input_json'])
                except json.JSONDecodeError:
                    tool_input = {}
                state['tool_results'].append({'name': tool_name, 'data': tool_input})
                chunks.append(sse('tool_result', json.dumps({'name': tool_name, 'data': tool_input})))
                state['current_tool_name'] = None
                state['current_tool_input_json'] = ''
            elif state['current_block']:
                chunks.append(sse(f'{state["current_block"]}_done'))
            state['current_block'] = None
        return chunks

    def run_parallel(client, user_msg):
        """7-thread parallel analysis: 1 Opus verdict + 5 Opus deep-dive threads + 1 Haiku card pipeline."""
        q = queue_module.Queue()
        timings = {}
        cancel = threading.Event()  # Signal to cancel Opus threads (e.g. doc not applicable)

        def worker(label, system_prompt, max_out,
                   model=MODEL, use_thinking=True, user_content=None, tools=None):
            t0 = time.time()
            max_retries = 3
            for attempt in range(max_retries):
                stream = None
                try:
                    msg_content = user_content if user_content is not None else user_msg
                    create_kwargs = {
                        'model': model,
                        'max_tokens': max_out,
                        'system': [{'type': 'text', 'text': system_prompt, 'cache_control': {'type': 'ephemeral'}}],
                        'messages': [{'role': 'user', 'content': msg_content}],
                        'stream': True,
                    }
                    if use_thinking:
                        create_kwargs['thinking'] = {'type': 'adaptive'}
                    if tools:
                        create_kwargs['tools'] = tools
                    stream = client.messages.create(**create_kwargs)
                    for event in stream:
                        if cancel.is_set():
                            break
                        q.put((label, event))
                    break  # success
                except anthropic.APIError as e:
                    is_overloaded = e.status_code in (429, 529) or 'overload' in str(e).lower()
                    if is_overloaded and attempt < max_retries - 1:
                        wait = (attempt + 1) * 5
                        print(f'[worker] {label}: Overloaded, retry {attempt+1} in {wait}s')
                        time.sleep(wait)
                        continue
                    q.put(('error', f'{label}: {e.message}'))
                    break
                except Exception as e:
                    is_overloaded = 'overload' in str(e).lower() or '529' in str(e)
                    if is_overloaded and attempt < max_retries - 1:
                        wait = (attempt + 1) * 5
                        print(f'[worker] {label}: Overloaded, retry {attempt+1} in {wait}s')
                        time.sleep(wait)
                        continue
                    q.put(('error', f'{label}: {str(e)}'))
                    break
                finally:
                    if stream:
                        stream.close()
            timings[label] = round(time.time() - t0, 1)
            q.put((f'{label}_done', None))

        # Build vision content for deep analysis if page images exist
        page_images = [img for img in doc.get('page_images', []) if img]
        deep_user_content = None
        if page_images:
            deep_user_content = [{'type': 'text', 'text': user_msg}]
            for i, img_b64 in enumerate(page_images):
                deep_user_content.append({'type': 'text', 'text': f'[Page {i + 1} visual layout:]'})
                deep_user_content.append({
                    'type': 'image',
                    'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': img_b64},
                })

        has_images = bool(page_images)

        yield sse('phase', 'thinking')

        # ── Non-blocking check: are pre-generated cards ready? ──
        precards_event = doc.get('_precards_event')
        claims_summary = ''
        prescan_na = False
        if precards_event and precards_event.is_set():
            ps = doc.get('_prescan')
            pc = doc.get('_precards')
            if ps and '**Not Applicable**' in ps.get('scan_text', ''):
                prescan_na = True
            elif ps and ps.get('clauses') and pc and pc.get('cards'):
                claims_summary = _build_claims_summary(ps, pc)

        # ── Not applicable: skip Opus threads entirely (saves ~$2) ──
        if prescan_na:
            ps = doc.get('_prescan')
            p_text = ps.get('profile_text', '') if ps else ''
            scan_sec = ps.get('seconds', 0) if ps else 0
            if p_text:
                yield sse('text', p_text + '\n')
            yield sse('quick_done', json.dumps({
                'seconds': scan_sec, 'model': FAST_MODEL}))
            yield sse('handoff', json.dumps({
                'tricks_found': 0, 'summary': '', 'clause_count': 0,
                'not_applicable': True}))
            yield sse('done', json.dumps({
                'quick_seconds': scan_sec, 'deep_seconds': 0, 'model': MODEL}))
            return

        # ── Start Opus verdict at t=0 — enriched with card data if available ──
        verdict_max = 32000  # Enough for adaptive thinking + all 11 tags (FLAGGED_CLAIMS can be long)
        opus_user = deep_user_content
        if claims_summary:
            if isinstance(opus_user, list):
                # Image mode: replace first text block with enriched version
                opus_user = [{'type': 'text', 'text': user_msg + '\n\n' + claims_summary}] + opus_user[1:]
            else:
                opus_user = (opus_user or user_msg) + '\n\n' + claims_summary
            print(f'[verdict] Opus enriched with {len(claims_summary)} chars of card context')
        t_opus = threading.Thread(
            target=worker,
            args=('overall', build_verdict_prompt(has_images=has_images),
                  verdict_max, MODEL, True),
            kwargs={'user_content': opus_user},
            daemon=True,
        )
        t_opus.start()

        # ── 5 parallel Opus deep-dive threads — all fire at t=0 ──
        deep_dive_threads = {
            'archaeology': (build_archaeology_prompt(has_images=has_images), 32000),
            'scenario':    (build_scenario_prompt(), 32000),
            'walkaway':    (build_walkaway_prompt(), 32000),
            'combinations':(build_combinations_prompt(), 32000),
            'playbook':    (build_playbook_prompt(), 32000),
        }
        for dd_label, (dd_prompt, dd_max) in deep_dive_threads.items():
            threading.Thread(
                target=worker,
                args=(dd_label, dd_prompt, dd_max, MODEL, True),
                kwargs={'user_content': deep_user_content or user_msg},
                daemon=True,
            ).start()

        # ── Document context: metadata for loading screen ──
        pre_ctx = doc.get('_doc_context')
        if pre_ctx:
            # Pre-computed (sample documents) — emit immediately, no API call
            filtered = {k: v for k, v in pre_ctx.items()
                        if v and v.lower() not in ('not specified', 'unknown', 'n/a')}
            if filtered:
                q.put(('doc_context', filtered))
        else:
            # Real uploads — lightweight Haiku extraction
            def _doc_context_worker():
                try:
                    full = doc['text']
                    text_preview = full[:3000]
                    if len(full) > 5000:
                        text_preview += '\n\n[...]\n\n' + full[-1500:]
                    resp = client.messages.create(
                        model=FAST_MODEL,
                        max_tokens=300,
                        messages=[{
                            'role': 'user',
                            'content': (
                                'Extract factual metadata from this document excerpt. '
                                'Respond ONLY with these fields, one per line. '
                                'If unknown, write "Unknown".\n\n'
                                'TYPE: [document type, e.g. "Residential Lease", "Gym Membership", "Insurance Policy"]\n'
                                'DRAFTER: [organization/company name that drafted this]\n'
                                'OTHER_PARTY: [who signs/receives this, e.g. "Tenant", "Member", "Policyholder"]\n'
                                'JURISDICTION: [country or state from governing law clause, registered address, or company HQ — e.g. "California, USA", "England & Wales"]\n'
                                'DATE: [document date or effective date if stated]\n'
                                'DURATION: [contract duration if stated, e.g. "12 months", "24 months"]\n'
                                'KEY_AMOUNT: [main financial figure, e.g. "$1,450/month", "$350 adoption fee"]\n\n'
                                f'DOCUMENT:\n{text_preview}'
                            ),
                        }],
                    )
                    result = {}
                    for line in resp.content[0].text.strip().split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            key = key.strip().upper().replace(' ', '_')
                            val = val.strip()
                            if val and val.lower() != 'unknown' and val != 'N/A':
                                result[key] = val
                    if result:
                        q.put(('doc_context', result))
                except Exception as e:
                    print(f'[doc_context] Error: {e}')

            threading.Thread(target=_doc_context_worker, daemon=True).start()

        # ── FAST PATH: pre-generated cards already available (non-blocking) ──
        if precards_event and precards_event.is_set():
            prescan = doc.get('_prescan')
            precards = doc.get('_precards')
            if (prescan and prescan.get('clauses') and precards
                    and precards.get('cards')
                    and '**Not Applicable**' not in prescan.get('scan_text', '')):
                # Cards pre-generated during upload — emit instantly!
                print(f'[scan] Using pre-generated cards ({len(precards["cards"])} cards, '
                      f'ready during upload)')
                profile_text = prescan['profile_text']
                if profile_text:
                    yield sse('text', profile_text + '\n\n---\n\n')
                for card_text in precards['cards']:
                    card_text = card_text.strip().strip('-').strip()
                    if card_text:
                        yield sse('text', card_text + '\n\n---\n\n')
                clause_count = sum(
                    1 for c in precards['cards']
                    if c and 'Fair Clauses Summary' not in c)
                yield sse('quick_done', json.dumps({
                    'seconds': 0.1, 'model': FAST_MODEL}))
                yield sse('handoff', json.dumps({
                    'tricks_found': 0, 'summary': '',
                    'clause_count': clause_count,
                    'not_applicable': False,
                }))
                # Only wait for Opus verdict
                yield from _run_parallel_cards(q, timings, cancel, 0)
                return

        # ── STREAMING PATH: cards not ready, run pipeline in background ──
        # Opus events flow to the browser from t=0 while cards build.
        def _card_pipeline():
            """Background thread: streams card chunks to SSE as they generate.
            First card streams token-by-token (~4-5s), others flush when done."""
            try:
                t_pipeline_start = time.time()
                _prescan_ev = doc.get('_prescan_event')
                _stream_q = doc.get('_card_stream_queue')
                _card_queue = doc.get('_card_queue')
                _preview_queue = doc.get('_clause_preview_queue')

                _profile_sent = False
                _started_sent = False
                _streaming_idx = None      # card currently streaming to frontend
                _card_buffers = {}         # {idx: accumulated_text} for buffered cards
                _done_cards = set()        # card indices that finished generating
                _emitted_cards = set()     # card indices already sent to frontend
                _held_msgs = []            # hold card stream msgs until profile is sent

                def _process_card_msg(msg):
                    """Process a single card stream message."""
                    nonlocal _streaming_idx, _started_sent
                    msg_type, idx = msg[0], msg[1]

                    if msg_type == 'chunk':
                        chunk = msg[2]
                        if not _started_sent:
                            q.put(('cards_started', 20))
                            _started_sent = True
                        if _streaming_idx is None:
                            _streaming_idx = idx
                        if idx == _streaming_idx:
                            q.put(('card_text', chunk))
                        else:
                            _card_buffers.setdefault(idx, '')
                            _card_buffers[idx] += chunk

                    elif msg_type == 'done':
                        _done_cards.add(idx)
                        if idx == _streaming_idx:
                            q.put(('card_text', '\n\n---\n\n'))
                            _emitted_cards.add(idx)
                            _streaming_idx = None
                            _flush_buffered()

                def _flush_buffered():
                    """Emit any buffered complete cards and pick next to stream."""
                    nonlocal _streaming_idx
                    # Flush complete buffered cards
                    for buf_idx in sorted(_card_buffers.keys()):
                        if buf_idx in _done_cards and buf_idx not in _emitted_cards:
                            ct = _card_buffers[buf_idx].strip().strip('-').strip()
                            if ct:
                                q.put(('card_text', ct + '\n\n---\n\n'))
                            _emitted_cards.add(buf_idx)
                    # Pick next incomplete card to stream (if any)
                    for buf_idx in sorted(_card_buffers.keys()):
                        if buf_idx not in _done_cards and buf_idx not in _emitted_cards:
                            _streaming_idx = buf_idx
                            # Flush already-buffered chunks for this card
                            if _card_buffers.get(buf_idx):
                                q.put(('card_text', _card_buffers[buf_idx]))
                            return
                    _streaming_idx = None

                while True:
                    prescan_done = _prescan_ev and _prescan_ev.is_set()

                    # Forward clause previews
                    if _preview_queue:
                        while not _preview_queue.empty():
                            try:
                                q.put(('clause_preview', _preview_queue.get_nowait()))
                            except queue_module.Empty:
                                break

                    # Read streaming chunks from card workers
                    if _stream_q:
                        try:
                            msg = _stream_q.get(timeout=0.05)

                            # Hold card messages until profile is sent
                            # (frontend expects profile as first text segment)
                            if not _profile_sent:
                                _held_msgs.append(msg)
                            else:
                                # Process this message (and any held ones)
                                msgs_to_process = _held_msgs + [msg] if _held_msgs else [msg]
                                _held_msgs = []
                                for m in msgs_to_process:
                                    _process_card_msg(m)

                        except queue_module.Empty:
                            pass

                    # Once prescan is done, handle profile + check completion
                    if prescan_done:
                        _prescan = doc.get('_prescan')

                        # Not applicable?
                        if _prescan and '**Not Applicable**' in _prescan.get('scan_text', ''):
                            q.put(('cards_not_applicable', {
                                'profile_text': _prescan.get('profile_text', ''),
                                'scan_text': _prescan.get('scan_text', ''),
                                'scan_seconds': _prescan.get('seconds', 0),
                            }))
                            return

                        # Send profile once
                        if not _profile_sent:
                            _profile_sent = True
                            _profile = _prescan.get('profile_text', '') if _prescan else ''
                            timings['scan'] = _prescan.get('seconds', 0) if _prescan else 0
                            if _profile:
                                q.put(('cards_profile', _profile))
                            # Flush held card messages now that profile is out
                            for m in _held_msgs:
                                _process_card_msg(m)
                            _held_msgs = []

                        # No prescan or failed — blocking scan fallback
                        if not _prescan or not _prescan.get('clauses'):
                            if len(_emitted_cards) > 0 or len(_done_cards) > 0:
                                # Some cards arrived — signal completion
                                q.put(('cards_all_done', len(_emitted_cards) or len(_done_cards)))
                                return
                            t0_scan = time.time()
                            try:
                                scan_response = client.messages.create(
                                    model=FAST_MODEL,
                                    max_tokens=2000,
                                    system=[{
                                        'type': 'text',
                                        'text': build_clause_id_prompt(),
                                        'cache_control': {'type': 'ephemeral'},
                                    }],
                                    messages=[
                                        {'role': 'user', 'content': user_msg},
                                        {'role': 'assistant', 'content': 'CLAUSE:'},
                                    ],
                                )
                                _scan_text = 'CLAUSE:' + scan_response.content[0].text
                                timings['scan'] = round(time.time() - t0_scan, 1)
                                _profile_fb, _clauses, _green = parse_identification_output(_scan_text)

                                if '**Not Applicable**' in _scan_text or not _clauses:
                                    q.put(('cards_not_applicable', {
                                        'profile_text': _profile_fb,
                                        'scan_text': _scan_text,
                                        'scan_seconds': timings.get('scan', 0),
                                    }))
                                    return

                                # Start Phase 2 card workers (uses streaming worker())
                                if _profile_fb:
                                    q.put(('cards_profile', _profile_fb))
                                _card_sys = build_single_card_system(doc['text'])
                                _total = len(_clauses) + (1 if _green else 0)
                                print(f'[pipeline] Starting {_total} card workers (blocking scan path)')
                                for i, ci in enumerate(_clauses):
                                    cu = (
                                        f"Generate a complete flip card for this specific clause:\n\n"
                                        f"Title: {ci['title']}\n"
                                        f"Section Reference: {ci.get('section', 'Not specified')}\n"
                                        f"Prescan Risk: {ci.get('risk', 'RED')}\n"
                                        f"Prescan Trick: {ci.get('trick', '')}\n\n"
                                        f"Find this clause in the document and output the COMPLETE flip card. "
                                        f"Make your own independent risk assessment — the prescan hints above are guidance only."
                                    )
                                    threading.Thread(
                                        target=worker,
                                        args=(f'card_{i}', _card_sys, 3000, FAST_MODEL, False),
                                        kwargs={'user_content': cu},
                                        daemon=True,
                                    ).start()
                                if _green:
                                    threading.Thread(
                                        target=worker,
                                        args=(f'card_{len(_clauses)}', _card_sys, 2000, FAST_MODEL, False),
                                        kwargs={'user_content': build_green_summary_user(_green)},
                                        daemon=True,
                                    ).start()
                                q.put(('cards_started', _total))
                                return
                            except Exception as e:
                                print(f'[pipeline] Phase 1 failed: {e}, falling back to single-pass')
                                quick_max = max(16000, min(32000, len(doc['text']) // 2))
                                threading.Thread(
                                    target=worker,
                                    args=('quick', build_card_scan_prompt(), quick_max,
                                          FAST_MODEL, False),
                                    daemon=True,
                                ).start()
                                q.put(('cards_fallback', None))
                                return

                        # Prescan succeeded — check if all cards streamed
                        _card_total = doc.get('_card_total', 0)
                        if _card_total > 0 and len(_done_cards) >= _card_total:
                            # All cards generated — flush any remaining
                            if _streaming_idx is not None and _streaming_idx in _done_cards:
                                q.put(('card_text', '\n\n---\n\n'))
                                _emitted_cards.add(_streaming_idx)
                                _streaming_idx = None
                            _flush_buffered()
                            q.put(('cards_all_done', _card_total))
                            print(f'[pipeline] All {_card_total} cards streamed')
                            return

                        # Cards still pending — if no stream queue, start fresh workers
                        if not _stream_q and not _card_queue:
                            _clauses = _prescan['clauses']
                            _green = _prescan['green_text']
                            _card_sys = build_single_card_system(doc['text'])
                            _total = len(_clauses) + (1 if _green else 0)
                            print(f'[pipeline] Starting {_total} card workers (prescan path)')
                            for i, ci in enumerate(_clauses):
                                cu = (
                                    f"Generate a complete flip card for this specific clause:\n\n"
                                    f"Title: {ci['title']}\n"
                                    f"Section Reference: {ci.get('section', 'Not specified')}\n"
                                    f"Prescan Risk: {ci.get('risk', 'RED')}\n"
                                    f"Prescan Trick: {ci.get('trick', '')}\n\n"
                                    f"Find this clause in the document and output the COMPLETE flip card. "
                                    f"Make your own independent risk assessment — the prescan hints above are guidance only."
                                )
                                threading.Thread(
                                    target=worker,
                                    args=(f'card_{i}', _card_sys, 3000, FAST_MODEL, False),
                                    kwargs={'user_content': cu},
                                    daemon=True,
                                ).start()
                            if _green:
                                threading.Thread(
                                    target=worker,
                                    args=(f'card_{len(_clauses)}', _card_sys, 2000, FAST_MODEL, False),
                                    kwargs={'user_content': build_green_summary_user(_green)},
                                    daemon=True,
                                ).start()
                            q.put(('cards_started', _total))
                            return

                        # Keep polling
                        continue

                    # Prescan not done yet — keep polling
                    if not _stream_q and not _card_queue:
                        time.sleep(0.05)
                        _stream_q = doc.get('_card_stream_queue')
                        _card_queue = doc.get('_card_queue')
                        continue

                    # Safety: 60s total timeout
                    if time.time() - t_pipeline_start > 60:
                        print(f'[pipeline] Timed out after 60s, {len(_emitted_cards)} cards streamed')
                        if len(_emitted_cards) > 0 or len(_done_cards) > 0:
                            _flush_buffered()
                            q.put(('cards_all_done', len(_emitted_cards)))
                        return

            except Exception as e:
                print(f'[card_pipeline] Error: {e}')
                q.put(('error', f'card_pipeline: {str(e)}'))

        threading.Thread(target=_card_pipeline, daemon=True).start()

        # Enter event loop immediately — Opus events flow from t=0
        yield from _run_parallel_streaming(q, timings, cancel)

    def _run_parallel_cards(q, timings, cancel, total_cards):
        """Event loop for parallel per-clause card generation + Opus verdict.
        Cards are buffered and emitted in order as they complete."""

        OPUS_SOURCES = {'overall', 'archaeology', 'scenario', 'walkaway', 'combinations', 'playbook'}

        start_time = time.time()
        card_texts = {}
        card_done_flags = {}
        next_card_to_emit = 0
        cards_all_done = (total_cards == 0)  # Pre-generated cards: already emitted
        done_flags = {s: False for s in OPUS_SOURCES}
        thread_texts = {s: '' for s in OPUS_SOURCES}

        def all_done():
            return cards_all_done and all(done_flags.values())

        while not all_done():
            # ── Wall-clock timeout ──
            if time.time() - start_time > 300:
                cancel.set()
                yield sse('error', 'Analysis timed out after 5 minutes')
                yield sse('done', json.dumps({
                    'quick_seconds': timings.get('scan', 0),
                    'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
                    'model': MODEL}))
                return

            try:
                source, event = q.get(timeout=1.0)
            except queue_module.Empty:
                continue

            # ── Document context (lightweight metadata) ──
            if source == 'doc_context':
                yield sse('doc_context', json.dumps(event))
                continue

            # ── Error handling ──
            if source == 'error':
                error_msg = str(event)
                error_source = error_msg.split(':')[0] if ':' in error_msg else ''
                yield sse('error', error_msg)
                if error_source == 'card_pipeline':
                    for ci in range(max(total_cards, 0)):
                        card_done_flags[ci] = True
                        card_texts.setdefault(ci, '')
                    cards_all_done = True
                    # Emit quick_done + handoff so frontend transitions
                    yield sse('quick_done', json.dumps({
                        'seconds': time.time() - start_time, 'model': FAST_MODEL}))
                    yield sse('handoff', json.dumps({
                        'tricks_found': 0, 'summary': '',
                        'clause_count': 0, 'not_applicable': False}))
                elif error_source.startswith('card_'):
                    try:
                        idx = int(error_source.split('_')[1])
                        card_done_flags[idx] = True
                        card_texts.setdefault(idx, '')
                    except (IndexError, ValueError):
                        pass
                elif error_source in OPUS_SOURCES:
                    done_flags[error_source] = True
                continue

            # ── Card streaming events: accumulate text per card ──
            if source.startswith('card_') and not source.endswith('_done'):
                idx = int(source.split('_')[1])
                card_texts.setdefault(idx, '')
                if hasattr(event, 'type') and event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        card_texts[idx] += delta.text
                continue

            # ── Card done: buffer and emit in order ──
            if source.startswith('card_') and source.endswith('_done'):
                idx_str = source[5:-5]  # 'card_0_done' → '0'
                idx = int(idx_str)
                card_done_flags[idx] = True

                # Emit all consecutive completed cards from buffer
                while next_card_to_emit < total_cards and card_done_flags.get(next_card_to_emit):
                    card_text = card_texts.get(next_card_to_emit, '').strip()
                    if card_text:
                        # Strip any leading/trailing --- the model might add
                        card_text = card_text.strip('-').strip()
                        yield sse('text', card_text + '\n\n---\n\n')
                    next_card_to_emit += 1

                # All cards done?
                if next_card_to_emit >= total_cards:
                    cards_all_done = True
                    card_times = [timings.get(f'card_{i}', 0) for i in range(total_cards)]
                    max_card_time = max(card_times) if card_times else 0
                    # Report wall-clock time from analysis start (not cumulative)
                    total_quick = round(time.time() - start_time, 1)

                    yield sse('quick_done', json.dumps({
                        'seconds': total_quick, 'model': FAST_MODEL}))

                    # Count RED/YELLOW clauses (exclude green summary)
                    clause_count = sum(
                        1 for i in range(total_cards)
                        if card_texts.get(i, '')
                        and 'Fair Clauses Summary' not in card_texts.get(i, ''))

                    yield sse('handoff', json.dumps({
                        'tricks_found': 0,
                        'summary': '',
                        'clause_count': clause_count,
                        'not_applicable': False,
                    }))
                continue

            # ── Opus source done ──
            if source.endswith('_done') and source[:-5] in OPUS_SOURCES:
                opus_label = source[:-5]
                done_flags[opus_label] = True
                yield sse(f'{opus_label}_done', json.dumps({
                    'seconds': timings.get(opus_label, 0)}))
                continue

            # ── Opus stream events ──
            if source in OPUS_SOURCES:
                if not hasattr(event, 'type'):
                    continue
                if event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        thread_texts[source] += delta.text
                        yield sse(f'{source}_text', delta.text)
                    elif hasattr(delta, 'type') and delta.type == 'thinking_delta':
                        yield sse(f'{source}_thinking', delta.thinking)

        # ── Save verdict + deep dives for follow-up agent ──
        doc['_verdict_text'] = thread_texts.get('overall', '')
        doc['_deep_dive_texts'] = {k: v for k, v in thread_texts.items() if k != 'overall'}

        # ── Final done event ──
        yield sse('done', json.dumps({
            'quick_seconds': timings.get('scan', 0),
            'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
            'model': MODEL}))

    def _run_parallel_streaming(q, timings, cancel):
        """Non-blocking event loop: Opus events stream immediately while
        the card pipeline runs in a background thread.  Handles pipeline
        control events (cards_instant, cards_started, cards_not_applicable,
        cards_fallback, cards_profile) alongside normal card/Opus events."""

        OPUS_SOURCES = {'overall', 'archaeology', 'scenario', 'walkaway', 'combinations', 'playbook'}

        start_time = time.time()
        card_texts = {}
        card_done_flags = {}
        next_card_to_emit = 0
        total_cards = -1  # Unknown until pipeline reports
        cards_all_done = False
        done_flags = {s: False for s in OPUS_SOURCES}
        thread_texts = {s: '' for s in OPUS_SOURCES}
        fallback_mode = False
        state_quick = None
        quick_text = ''
        quick_done_flag = False

        def all_done():
            if fallback_mode:
                return quick_done_flag and all(done_flags.values())
            return cards_all_done and all(done_flags.values())

        while not all_done():
            if time.time() - start_time > 300:
                cancel.set()
                yield sse('error', 'Analysis timed out after 5 minutes')
                yield sse('done', json.dumps({
                    'quick_seconds': timings.get('scan', 0),
                    'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
                    'model': MODEL}))
                return

            try:
                source, event = q.get(timeout=1.0)
            except queue_module.Empty:
                continue

            # ── Pipeline: pre-built cards arrived ──
            if source == 'cards_instant':
                profile_text = event.get('profile_text', '')
                cards = event.get('cards', [])
                if profile_text:
                    yield sse('text', profile_text + '\n\n---\n\n')
                for ct in cards:
                    ct = ct.strip().strip('-').strip()
                    if ct:
                        yield sse('text', ct + '\n\n---\n\n')
                clause_count = sum(1 for c in cards if c and 'Fair Clauses Summary' not in c)
                yield sse('quick_done', json.dumps({'seconds': 0.1, 'model': FAST_MODEL}))
                yield sse('handoff', json.dumps({
                    'tricks_found': 0, 'summary': '',
                    'clause_count': clause_count, 'not_applicable': False}))
                cards_all_done = True
                total_cards = 0
                continue

            # ── Pipeline: clause preview during loading ──
            if source == 'clause_preview':
                yield sse('clause_preview', json.dumps(event))
                continue

            # ── Pipeline: document context metadata ──
            if source == 'doc_context':
                yield sse('doc_context', json.dumps(event))
                continue

            # ── Pipeline: document profile text ──
            if source == 'cards_profile':
                yield sse('text', str(event) + '\n\n---\n\n')
                continue

            # ── Pipeline: Phase 2 card workers started (fallback path) ──
            if source == 'cards_started':
                total_cards = event
                if total_cards == 0:
                    cards_all_done = True
                else:
                    # Re-check: cards may have arrived before total was known
                    cards_received = sum(1 for v in card_done_flags.values() if v)
                    if cards_received >= total_cards:
                        cards_all_done = True
                        total_quick = round(time.time() - start_time, 1)
                        yield sse('quick_done', json.dumps({
                            'seconds': total_quick, 'model': FAST_MODEL}))
                        clause_count = sum(
                            1 for v in card_texts.values()
                            if v and 'Fair Clauses Summary' not in v)
                        yield sse('handoff', json.dumps({
                            'tricks_found': 0, 'summary': '',
                            'clause_count': clause_count,
                            'not_applicable': False}))
                continue

            # ── Pipeline: streaming card text chunk ──
            if source == 'card_text':
                yield sse('text', str(event))
                continue

            # ── Pipeline: all cards streamed ──
            if source == 'cards_all_done':
                cards_all_done = True
                total_cards = event
                total_quick = round(time.time() - start_time, 1)
                yield sse('quick_done', json.dumps({
                    'seconds': total_quick, 'model': FAST_MODEL}))
                yield sse('handoff', json.dumps({
                    'tricks_found': 0, 'summary': '',
                    'clause_count': max(total_cards - 1, 0),
                    'not_applicable': False}))
                continue

            # ── Pipeline: individual pre-built card ready (legacy/fallback) ──
            if source == 'card_ready':
                idx, card_text = event
                card_done_flags[idx] = True
                card_texts[idx] = card_text

                # Emit immediately — don't wait for ordering
                ct = card_text.strip().strip('-').strip()
                if ct:
                    yield sse('text', ct + '\n\n---\n\n')

                # All cards done?
                cards_received = sum(1 for v in card_done_flags.values() if v)
                if total_cards > 0 and cards_received >= total_cards:
                    cards_all_done = True
                    total_quick = round(time.time() - start_time, 1)
                    yield sse('quick_done', json.dumps({
                        'seconds': total_quick, 'model': FAST_MODEL}))
                    clause_count = sum(
                        1 for v in card_texts.values()
                        if v and 'Fair Clauses Summary' not in v)
                    yield sse('handoff', json.dumps({
                        'tricks_found': 0, 'summary': '',
                        'clause_count': clause_count,
                        'not_applicable': False}))
                continue

            # ── Pipeline: document not applicable ──
            if source == 'cards_not_applicable':
                p_text = event.get('profile_text', '')
                scan_sec = event.get('scan_seconds', 0)
                if p_text:
                    yield sse('text', p_text + '\n')
                cancel.set()
                yield sse('quick_done', json.dumps({
                    'seconds': scan_sec, 'model': FAST_MODEL}))
                yield sse('handoff', json.dumps({
                    'tricks_found': 0, 'summary': '', 'clause_count': 0,
                    'not_applicable': '**Not Applicable**' in event.get('scan_text', '')}))
                yield sse('done', json.dumps({
                    'quick_seconds': scan_sec, 'deep_seconds': 0, 'model': MODEL}))
                return

            # ── Pipeline: fallback to single-pass Haiku ──
            if source == 'cards_fallback':
                fallback_mode = True
                state_quick = _make_stream_state()
                continue

            # ── Error handling ──
            if source == 'error':
                error_msg = str(event)
                error_source = error_msg.split(':')[0] if ':' in error_msg else ''
                yield sse('error', error_msg)
                if error_source == 'card_pipeline':
                    for ci in range(max(total_cards, 0)):
                        card_done_flags[ci] = True
                        card_texts.setdefault(ci, '')
                    cards_all_done = True
                    yield sse('quick_done', json.dumps({
                        'seconds': time.time() - start_time, 'model': FAST_MODEL}))
                    yield sse('handoff', json.dumps({
                        'tricks_found': 0, 'summary': '',
                        'clause_count': 0, 'not_applicable': False}))
                elif error_source.startswith('card_'):
                    try:
                        idx = int(error_source.split('_')[1])
                        card_done_flags[idx] = True
                        card_texts.setdefault(idx, '')
                    except (IndexError, ValueError):
                        pass
                elif error_source in OPUS_SOURCES:
                    done_flags[error_source] = True
                elif error_source == 'quick':
                    cancel.set()
                    yield sse('done', json.dumps({
                        'quick_seconds': 0, 'deep_seconds': 0, 'model': MODEL}))
                    return
                continue

            # ── Fallback: Haiku single-pass streaming ──
            if fallback_mode and source == 'quick':
                if hasattr(event, 'type') and event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        quick_text += delta.text
                for chunk in process_stream_event(event, state_quick):
                    yield chunk
                continue

            if fallback_mode and source == 'quick_done':
                quick_done_flag = True
                qt = timings.get('quick', 0)
                yield sse('quick_done', json.dumps({'seconds': qt, 'model': FAST_MODEL}))
                doc_na = '**Not Applicable**' in quick_text
                cc = max(0, len(re.findall(r'\n---\n', quick_text)) - 1)
                yield sse('handoff', json.dumps({
                    'tricks_found': 0, 'summary': '', 'clause_count': cc,
                    'not_applicable': doc_na}))
                if doc_na:
                    cancel.set()
                    yield sse('done', json.dumps({
                        'quick_seconds': qt, 'deep_seconds': 0, 'model': MODEL}))
                    return
                continue

            # ── Card streaming events: accumulate text per card ──
            if source.startswith('card_') and not source.endswith('_done'):
                idx = int(source.split('_')[1])
                card_texts.setdefault(idx, '')
                if hasattr(event, 'type') and event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        card_texts[idx] += delta.text
                continue

            # ── Card done: buffer and emit in order ──
            if source.startswith('card_') and source.endswith('_done'):
                idx = int(source[5:-5])
                card_done_flags[idx] = True

                # Emit consecutive completed cards from buffer
                while total_cards > 0 and next_card_to_emit < total_cards and card_done_flags.get(next_card_to_emit):
                    ct = card_texts.get(next_card_to_emit, '').strip()
                    if ct:
                        ct = ct.strip('-').strip()
                        yield sse('text', ct + '\n\n---\n\n')
                    next_card_to_emit += 1

                # All cards done?
                if total_cards > 0 and next_card_to_emit >= total_cards:
                    cards_all_done = True
                    total_quick = round(time.time() - start_time, 1)
                    yield sse('quick_done', json.dumps({
                        'seconds': total_quick, 'model': FAST_MODEL}))
                    clause_count = sum(
                        1 for i in range(total_cards)
                        if card_texts.get(i, '') and 'Fair Clauses Summary' not in card_texts.get(i, ''))
                    yield sse('handoff', json.dumps({
                        'tricks_found': 0, 'summary': '',
                        'clause_count': clause_count, 'not_applicable': False}))
                continue

            # ── Opus source done ──
            if source.endswith('_done') and source[:-5] in OPUS_SOURCES:
                opus_label = source[:-5]
                done_flags[opus_label] = True
                yield sse(f'{opus_label}_done', json.dumps({
                    'seconds': timings.get(opus_label, 0)}))
                continue

            # ── Opus stream events ──
            if source in OPUS_SOURCES:
                if not hasattr(event, 'type'):
                    continue
                if event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        thread_texts[source] += delta.text
                        yield sse(f'{source}_text', delta.text)
                    elif hasattr(delta, 'type') and delta.type == 'thinking_delta':
                        yield sse(f'{source}_thinking', delta.thinking)

        # ── Save verdict + deep dives for follow-up agent ──
        doc['_verdict_text'] = thread_texts.get('overall', '')
        doc['_deep_dive_texts'] = {k: v for k, v in thread_texts.items() if k != 'overall'}

        # ── Final done event ──
        yield sse('done', json.dumps({
            'quick_seconds': timings.get('scan', timings.get('quick', 0)),
            'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
            'model': MODEL}))

    def _make_stream_state():
        """Create a fresh state dict for stream event processing."""
        return {
            'current_block': None,
            'phase_buffer': '',
            'detected_phases': set(),
            'current_tool_name': None,
            'current_tool_input_json': '',
            'tool_results': [],
        }

    def generate():
        try:
            client = anthropic.Anthropic(
                timeout=180.0  # 3 min per call
            )
            user_msg = (
                "Analyze the following document from the drafter's "
                "strategic perspective.\n\n"
                "---BEGIN DOCUMENT---\n\n"
                f"{doc['text']}\n\n"
                "---END DOCUMENT---"
            )
            yield from run_parallel(client, user_msg)

        except anthropic.AuthenticationError:
            yield sse('error',
                      'Invalid API key. Check your ANTHROPIC_API_KEY.')
        except anthropic.APIError as e:
            yield sse('error', f'Anthropic API error: {e.message}')
        except Exception as e:
            print(f'[stream] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')
        finally:
            # Keep document + analysis results for follow-up & deep dives
            if doc_id in documents:
                documents[doc_id]['analyzed'] = True

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


# ── On-demand deep dive endpoint ──────────────────────────────────
DEEP_DIVE_PROMPTS = {
    'scenario': (build_scenario_prompt, 32000),
    'walkaway': (build_walkaway_prompt, 32000),
    'combinations': (build_combinations_prompt, 32000),
    'playbook': (build_playbook_prompt, 32000),
}


@app.route('/deepdive/<doc_id>/<dive_type>')
def deepdive(doc_id, dive_type):
    if doc_id not in documents:
        return jsonify({'error': 'Document not found.'}), 404
    if dive_type not in DEEP_DIVE_PROMPTS:
        return jsonify({'error': f'Unknown dive type: {dive_type}'}), 400

    doc = documents[doc_id]
    prompt_fn, max_tokens = DEEP_DIVE_PROMPTS[dive_type]

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def generate():
        try:
            client = anthropic.Anthropic()
            user_msg = (
                "---BEGIN DOCUMENT---\n\n"
                f"{doc['text']}\n\n"
                "---END DOCUMENT---"
            )
            yield sse('phase', 'thinking')
            t0 = time.time()
            stream = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                thinking={'type': 'adaptive'},
                system=[{
                    'type': 'text',
                    'text': prompt_fn(),
                    'cache_control': {'type': 'ephemeral'},
                }],
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True,
            )
            try:
                for event in stream:
                    if event.type == 'content_block_delta':
                        if event.delta.type == 'thinking_delta':
                            yield sse('thinking', event.delta.thinking)
                        elif event.delta.type == 'text_delta':
                            yield sse('text', event.delta.text)
                    elif event.type == 'message_stop':
                        elapsed = round(time.time() - t0, 1)
                        yield sse('done', json.dumps({'seconds': elapsed}))
            finally:
                stream.close()
        except anthropic.APIError as e:
            yield sse('error', f'API error: {e.message}')
        except Exception as e:
            print(f'[deepdive] {dive_type} error: {e}')
            yield sse('error', 'An internal error occurred.')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


# ── Tool definitions for follow-up agent ──────────────────────────
ASK_TOOLS = [
    {
        "name": "search_document",
        "description": "Search the uploaded document for paragraphs matching a query. Returns matching excerpts with surrounding context. Use this to find specific clauses, terms, or language relevant to the user's question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term — a keyword, phrase, or topic to find in the document"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_clause_analysis",
        "description": "Retrieve FlipSide's flip card analysis for a specific clause by number. Returns the full card: risk score, trick classification, reassurance (front), reveal (back), figure, example, and bottom line.",
        "input_schema": {
            "type": "object",
            "properties": {
                "clause_number": {
                    "type": "integer",
                    "description": "The clause number (1-based) to retrieve analysis for"
                }
            },
            "required": ["clause_number"]
        }
    },
    {
        "name": "get_verdict_summary",
        "description": "Retrieve FlipSide's overall expert verdict — tier, main risk, power ratio, jurisdiction, and key findings. Use this to understand the big picture before diving into specifics.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def _execute_tool(tool_name, tool_input, doc):
    """Execute a tool call and return the result string."""
    if tool_name == 'search_document':
        query = tool_input.get('query', '').lower()
        words = [w for w in query.split() if len(w) > 2]
        text = doc.get('text', '')
        paragraphs = text.split('\n\n')
        # Score paragraphs by number of matching words
        scored = []
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            # Exact phrase match scores highest
            if query in para_lower:
                score = len(words) + 1
            else:
                score = sum(1 for w in words if w in para_lower)
            if score > 0:
                scored.append((score, i, para))
        scored.sort(key=lambda x: -x[0])
        matches = []
        for score, i, para in scored[:5]:
            start = max(0, i - 1)
            end = min(len(paragraphs), i + 2)
            context = '\n\n'.join(paragraphs[start:end])
            matches.append(context)
        if matches:
            return f"Found {len(matches)} matching section(s):\n\n" + \
                   "\n\n---\n\n".join(matches)
        return f"No sections found matching '{tool_input.get('query', '')}'."

    elif tool_name == 'get_clause_analysis':
        clause_num = tool_input.get('clause_number', 0)
        precards = doc.get('_precards') or {}
        cards = precards.get('cards') or []
        if 1 <= clause_num <= len(cards):
            return cards[clause_num - 1]
        return f"Clause {clause_num} not found. This document has {len(cards)} clauses."

    elif tool_name == 'get_verdict_summary':
        verdict = doc.get('_verdict_text', '')
        if verdict:
            return verdict
        return "Verdict not available yet — analysis may still be in progress."

    return f"Unknown tool: {tool_name}"


@app.route('/ask/<doc_id>', methods=['POST'])
def ask(doc_id):
    if doc_id not in documents:
        return jsonify({'error': 'Document not found. Please re-upload.'}), 404

    doc = documents[doc_id]
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def generate():
        try:
            client = anthropic.Anthropic()
            system_prompt = build_followup_prompt()
            messages = [{'role': 'user', 'content': question}]
            max_rounds = 6  # Safety limit on tool-use loops

            yield sse('phase', 'thinking')

            for _round in range(max_rounds):
                # ── Call Opus with tools ──
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=16000,
                    thinking={'type': 'adaptive'},
                    system=[{
                        'type': 'text',
                        'text': system_prompt,
                        'cache_control': {'type': 'ephemeral'},
                    }],
                    tools=ASK_TOOLS,
                    messages=messages,
                )

                # ── Process response blocks ──
                tool_calls = []
                for block in response.content:
                    if block.type == 'thinking':
                        yield sse('thinking', block.thinking)
                    elif block.type == 'text':
                        yield sse('text', block.text)
                    elif block.type == 'tool_use':
                        tool_calls.append(block)
                        yield sse('tool_call', json.dumps({
                            'tool': block.name,
                            'input': block.input
                        }))

                # ── If no tool calls, we're done ──
                if response.stop_reason == 'end_turn' or not tool_calls:
                    yield sse('done')
                    return

                # ── Execute tools and continue ──
                tool_results = []
                for tc in tool_calls:
                    result = _execute_tool(tc.name, tc.input, doc)
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tc.id,
                        'content': result
                    })
                    # Tell frontend what we found
                    summary = result[:200] + '...' if len(result) > 200 else result
                    yield sse('tool_result', json.dumps({
                        'tool': tc.name,
                        'summary': summary
                    }))

                # ── Add assistant response + tool results to conversation ──
                messages.append({'role': 'assistant', 'content': response.content})
                messages.append({'role': 'user', 'content': tool_results})

            # Exhausted rounds
            yield sse('done')

        except anthropic.APIError as e:
            yield sse('error', f'API error: {e.message}')
        except Exception as e:
            print(f'[ask] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@app.route('/timeline/<doc_id>', methods=['GET', 'POST'])
def timeline(doc_id):
    """Generate worst-case timeline — on-demand after analysis."""
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found. Please re-upload.'}), 404

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def generate():
        try:
            client = anthropic.Anthropic()
            user_msg = (
                "Here is the document:\n\n"
                "---BEGIN DOCUMENT---\n\n"
                f"{doc['text']}\n\n"
                "---END DOCUMENT---\n\n"
                "Generate a worst-case timeline showing how one common trigger cascades through this contract."
            )
            yield sse('phase', 'thinking')
            stream = client.messages.create(
                model=MODEL,
                max_tokens=16000,
                thinking={'type': 'adaptive'},
                system=[{
                    'type': 'text',
                    'text': build_timeline_prompt(),
                    'cache_control': {'type': 'ephemeral'},
                }],
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True,
            )
            try:
                for event in stream:
                    if event.type == 'content_block_delta':
                        if event.delta.type == 'thinking_delta':
                            yield sse('thinking', event.delta.thinking)
                        elif event.delta.type == 'text_delta':
                            yield sse('text', event.delta.text)
                    elif event.type == 'message_stop':
                        yield sse('done')
            finally:
                stream.close()
        except anthropic.APIError as e:
            yield sse('error', f'API error: {e.message}')
        except Exception as e:
            print(f'[stream] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@app.route('/counter-draft/<doc_id>', methods=['GET', 'POST'])
def counter_draft(doc_id):
    """Generate fair rewrites of problematic clauses — on-demand after analysis."""
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found. Please re-upload.'}), 404

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def generate():
        try:
            client = anthropic.Anthropic()
            user_msg = (
                "Here is the document:\n\n"
                "---BEGIN DOCUMENT---\n\n"
                f"{doc['text']}\n\n"
                "---END DOCUMENT---\n\n"
                "Generate a counter-draft with fair rewrites for all problematic clauses."
            )
            yield sse('phase', 'thinking')
            stream = client.messages.create(
                model=MODEL,
                max_tokens=32000,
                thinking={'type': 'adaptive'},
                system=[{
                    'type': 'text',
                    'text': build_counter_draft_prompt(),
                    'cache_control': {'type': 'ephemeral'},
                }],
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True,
            )
            try:
                for event in stream:
                    if event.type == 'content_block_delta':
                        if event.delta.type == 'thinking_delta':
                            yield sse('thinking', event.delta.thinking)
                        elif event.delta.type == 'text_delta':
                            yield sse('text', event.delta.text)
                    elif event.type == 'message_stop':
                        yield sse('done')
            finally:
                stream.close()
        except anthropic.APIError as e:
            yield sse('error', f'API error: {e.message}')
        except Exception as e:
            print(f'[stream] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@app.route('/fetch-url', methods=['POST'])
def fetch_url():
    """Fetch a public URL and extract text content."""
    try:
        data = request.get_json(silent=True) or {}
        url = data.get('url', '').strip()
        if not url:
            return jsonify({'error': 'No URL provided.'}), 400
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Block private/internal URLs (SSRF prevention)
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ''
        if hostname in ('localhost', '127.0.0.1', '0.0.0.0', '::1') or \
           hostname.startswith(('10.', '172.16.', '172.17.', '172.18.', '172.19.',
                                '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
                                '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
                                '172.30.', '172.31.', '192.168.', '169.254.')):
            return jsonify({'error': 'Internal URLs are not allowed.'}), 400

        import requests as req
        from bs4 import BeautifulSoup

        resp = req.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; FlipSide/1.0)'
        })
        resp.raise_for_status()

        # SSRF: re-check final URL after redirects
        final_host = urlparse(resp.url).hostname or ''
        if final_host in ('localhost', '127.0.0.1', '0.0.0.0', '::1') or \
           final_host.startswith(('10.', '172.16.', '172.17.', '172.18.', '172.19.',
                                  '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
                                  '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
                                  '172.30.', '172.31.', '192.168.', '169.254.')):
            return jsonify({'error': 'Internal URLs are not allowed.'}), 400

        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()

        text = soup.get_text(separator='\n', strip=True)
        text = re.sub(r'\n{3,}', '\n\n', text)

        if len(text) < 50:
            return jsonify({'error': 'Could not extract meaningful text from this URL.'}), 400

        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag and title_tag.string else url[:80]

        doc_id = str(uuid.uuid4())
        store_document(doc_id, {
            'text': text,
            'filename': title[:100],
        })

        return jsonify({
            'doc_id': doc_id,
            'filename': title[:100],
            'text_length': len(text),
            'preview': text[:500],
            'full_text': text,
        })
    except Exception as e:
        print(f'[fetch-url] Error: {e}')
        return jsonify({'error': f'Could not fetch URL: {str(e)}'}), 400


if __name__ == '__main__':
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        print('\n' + '=' * 60)
        print('  WARNING: ANTHROPIC_API_KEY is not set.')
        print('  Set it in your environment or create a .env file.')
        print('=' * 60 + '\n')

    port = int(os.environ.get('FLIPSIDE_PORT', 5001))
    print('\n  FlipSide — The dark side of small print.')
    print(f'  Powered by Claude Opus 4.6 + Haiku 4.5 (fast cards).')
    print(f'  http://127.0.0.1:{port}\n')
    app.run(debug=True, port=port)
