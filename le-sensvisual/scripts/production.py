#!/usr/bin/env python3
"""Portable TYY production bookkeeping. Python 3.10+; no network or model calls.

This tracks selected contributions, real files and delivery evidence. It cannot
judge visual meaning or make a host invoke its tools. See references/execution.md.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import posixpath
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile

LENSES = ('world', 'atmosphere', 'reading', 'integration', 'composition',
          'relationships', 'objects', 'evidence', 'colour', 'specificity', 'closure')
TYPES = {'text', 'shape', 'line', 'polygon', 'image', 'table', 'chart'}
COMMON_KEYS = {'id', 'type', 'box', 'opacity', 'description'}
TEXT_KEYS = {'font_family', 'font_size', 'color', 'align', 'padding'}
OBJECT_KEYS = {
    'text': TEXT_KEYS | {'text', 'bold', 'italic', 'vertical', 'line_spacing'},
    'image': {'asset', 'fit'},
    'shape': {'geometry', 'fill', 'stroke', 'stroke_width', 'radius'},
    'polygon': {'points', 'fill', 'stroke', 'stroke_width'},
    'line': {'points', 'stroke', 'stroke_width', 'arrow'},
    'table': TEXT_KEYS | {'rows', 'header_fill', 'fill'},
    'chart': {'font_family', 'font_size', 'color', 'kind', 'categories', 'series'}
}
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'
ID = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,79}$')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, prefix='.visuasense-', suffix='.json', delete=False) as f:
        temporary = Path(f.name)
        f.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    try:
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def resolve(plan_file, value):
    p = Path(value).expanduser()
    return p.resolve() if p.is_absolute() else (Path(plan_file).resolve().parent / p).resolve()


def output_path(plan_file, value):
    path = resolve(plan_file, value)
    if not path.is_relative_to(Path(plan_file).resolve().parent):
        raise ValueError('Helper outputs must stay inside the production record directory; choose a job folder for this work')
    return path


def fingerprint(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False,
                                    allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def pages_for(plan, output):
    if not output.get('pages'):
        return plan['pages']
    by_id = {p['id']: p for p in plan['pages']}
    return [by_id[pid] for pid in output['pages']]


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def required_text(value, location, errors):
    if not isinstance(value, str) or not value.strip():
        errors.append(location + ': supply concrete text')


def identified(rows, location, errors):
    if not isinstance(rows, list):
        errors.append(location + ': expected an array')
        return {}
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not ID.fullmatch(str(row.get('id', ''))):
            errors.append(location + ': each entry needs a simple unique id')
            continue
        if row['id'] in result:
            errors.append(location + ': duplicate id ' + row['id'])
        result[row['id']] = row
    return result


def validate(plan):
    errors = []
    if not isinstance(plan, dict) or plan.get('schema_version') != 1:
        return ['Expected a production JSON object with schema_version 1']
    for key in ('brief', 'audience'):
        required_text(plan.get(key), key, errors)
    design = plan.get('design')
    if not isinstance(design, dict):
        errors.append('design: expected the resolved TYY decisions')
        design = {}
    for key in ('world', 'meaning', 'relationships', 'composition', 'harmony'):
        required_text(design.get(key), 'design.' + key, errors)
    assets = identified(plan.get('assets', []), 'assets', errors)
    outputs = identified(plan.get('outputs'), 'outputs', errors)
    pages = identified(plan.get('pages'), 'pages', errors)
    if not outputs or not pages:
        errors.append('At least one actual page and requested output are needed')
    output_paths = set()
    for out in outputs.values():
        for key in ('format', 'path'):
            required_text(out.get(key), 'output ' + out['id'] + '.' + key, errors)
        if out.get('path') in output_paths:
            errors.append('Outputs must not overwrite each other: ' + str(out.get('path')))
        output_paths.add(out.get('path'))
        if 'pages' in out and (not isinstance(out['pages'], list) or not out['pages'] or len(set(out['pages'])) != len(out['pages']) or any(pid not in pages for pid in out['pages'])):
            errors.append('output ' + out['id'] + ': pages must be distinct actual page ids in delivery order')
    for asset in assets.values():
        if asset.get('origin') not in {'generated', 'sourced', 'provided'}:
            errors.append('asset ' + asset['id'] + ': origin must be generated, sourced or provided')
        required_text(asset.get('description'), 'asset ' + asset['id'] + '.description', errors)
        if asset.get('origin') == 'generated' or not asset.get('path'):
            required_text(asset.get('request'), 'asset ' + asset['id'] + '.request', errors)
    for page in pages.values():
        label = 'page ' + page['id']
        required_text(page.get('job'), label + '.job', errors)
        size = page.get('size')
        if not isinstance(size, list) or len(size) != 2 or not all(number(v) and v > 0 for v in size):
            errors.append(label + ': size must be [positive width, positive height]')
        objects = identified(page.get('objects'), label + '.objects', errors)
        contributions = identified(page.get('contributions'), label + '.contributions', errors)
        if not objects or not contributions:
            errors.append(label + ': specify visible objects and their selected contributions')
        for contribution in contributions.values():
            for key in ('benefit', 'expression'):
                required_text(contribution.get(key), label + '.' + contribution['id'] + '.' + key, errors)
            refs = contribution.get('objects')
            if not isinstance(refs, list) or not refs or any(ref not in objects for ref in refs):
                errors.append(label + '.' + contribution['id'] + ': objects must reference actual object ids')
        for obj in objects.values():
            loc = label + '.' + obj['id']
            kind = obj.get('type')
            unknown = set(obj) - COMMON_KEYS - OBJECT_KEYS.get(kind, set())
            if unknown:
                errors.append(loc + ': adapter does not implement ' + ', '.join(sorted(unknown)) + '; use a capable writer, do not discard the design requirement')
            if kind not in TYPES:
                errors.append(loc + ': unsupported object type; use a capable host writer instead of discarding it')
            box = obj.get('box')
            if not isinstance(box, list) or len(box) != 4 or not all(number(v) for v in box) or box[2] <= 0 or box[3] <= 0:
                errors.append(loc + ': box must be [x,y,positive width,positive height]')
            elif isinstance(size, list) and len(size) == 2 and all(number(v) for v in size) and (box[0] >= size[0] or box[1] >= size[1] or box[0] + box[2] <= 0 or box[1] + box[3] <= 0):
                errors.append(loc + ': object lies entirely outside its canvas')
            for key in ('font_size', 'line_spacing', 'stroke_width', 'padding', 'radius'):
                if key in obj and (not number(obj[key]) or obj[key] < 0 or (key in {'font_size', 'line_spacing'} and obj[key] == 0)):
                    errors.append(loc + '.' + key + ': use a finite positive size or nonnegative spacing/stroke')
            for key in ('fill', 'stroke', 'color', 'header_fill'):
                if key in obj and obj[key] is not None and obj[key] != 'none' and (not isinstance(obj[key], str) or not re.fullmatch(r'#?[0-9A-Fa-f]{6}', obj[key])):
                    errors.append(loc + '.' + key + ': expected a six-digit RGB colour or none')
            if obj.get('align', 'left') not in {'left', 'center', 'right'} or obj.get('vertical', 'top') not in {'top', 'middle', 'bottom'}:
                errors.append(loc + ': unsupported text alignment')
            opacity = obj.get('opacity', 1)
            if not number(opacity) or not 0 < opacity <= 1:
                errors.append(loc + ': opacity must be greater than 0 and at most 1')
            elif opacity != 1 and kind not in {'image', 'shape', 'polygon'}:
                errors.append(loc + ': fading this object type needs another capable writer; this adapter fades images and filled shapes')
            if kind not in {'shape', 'polygon'} and any(obj.get(k) == 'none' for k in ('color', 'header_fill', 'fill', 'stroke') if k in obj):
                errors.append(loc + ': this object needs actual RGB ink/fill; transparent fill/stroke is supported for shapes/polygons')
            if kind == 'image' and obj.get('asset') not in assets:
                errors.append(loc + ': image references an unknown asset')
            if kind == 'image' and obj.get('fit', 'contain') not in {'contain', 'cover', 'stretch'}:
                errors.append(loc + ': fit must be contain, cover or explicit stretch')
            if kind == 'text':
                required_text(obj.get('text'), loc + '.text', errors)
            if kind in {'line', 'polygon'}:
                pts = obj.get('points', [])
                if not isinstance(pts, list) or len(pts) < (3 if kind == 'polygon' else 2) or any(not isinstance(p, list) or len(p) != 2 or not all(number(v) for v in p) for p in pts):
                    errors.append(loc + ': supply actual [x,y] points in page coordinates')
            if kind == 'shape' and obj.get('geometry', 'rect') not in {'rect', 'round_rect', 'ellipse', 'triangle', 'chevron'}:
                errors.append(loc + ': unsupported shape geometry; preserve it through a suitable writer')
            if kind == 'table':
                rows = obj.get('rows', [])
                if not isinstance(rows, list) or not rows or not isinstance(rows[0], list) or not rows[0] or any(not isinstance(r, list) or len(r) != len(rows[0]) for r in rows):
                    errors.append(loc + ': rows must be a nonempty rectangular array')
            if kind == 'chart':
                categories, series = obj.get('categories', []), obj.get('series', [])
                if obj.get('kind') not in {'bar', 'column', 'line'}:
                    errors.append(loc + ': this adapter supports bar, column and line; use a suitable host writer for other charts')
                if not isinstance(categories, list) or not categories or not isinstance(series, list) or not series:
                    errors.append(loc + ': chart needs actual categories and series')
                elif any(not isinstance(s, dict) or not isinstance(s.get('values'), list) or len(s['values']) != len(categories) or not all(number(v) for v in s['values']) for s in series):
                    errors.append(loc + ': each series needs finite values matching the categories')
        covered = {ref for c in contributions.values() for ref in (c.get('objects') if isinstance(c.get('objects'), list) else [])}
        for obj in objects.values():
            if obj.get('type') == 'image' and obj['id'] not in covered:
                errors.append(label + '.' + obj['id'] + ': connect this artwork to a selected contribution')
    return errors


def load(plan_file):
    plan = read_json(plan_file)
    errors = validate(plan)
    if errors:
        raise ValueError('\n'.join(errors))
    # Resolve aliases before any write. Artifacts, receipts and reviews must not
    # overwrite the record, a bound asset, or another managed file.
    reserved = {Path(plan_file).resolve()}
    reserved.update(resolve(plan_file, a['path']) for a in plan.get('assets', []) if a.get('path'))
    targets = set()
    for out in plan['outputs']:
        artifact = output_path(plan_file, out['path'])
        paths = [artifact, receipt_path(artifact)]
        if out.get('review'):
            paths.append(output_path(plan_file, out['review']))
        for path in paths:
            if path in reserved or path in targets:
                raise ValueError('Managed file paths collide: ' + str(path))
            targets.add(path)
    return plan


def asset_issues(plan, plan_file, pages=None):
    issues, requests = [], []
    pages = plan['pages'] if pages is None else pages
    used = {o['asset'] for p in pages for o in p['objects'] if o['type'] == 'image'}
    for asset in plan.get('assets', []):
        if asset['id'] not in used:
            continue
        if not asset.get('path'):
            issues.append('Asset not bound: ' + asset['id'])
            uses = [{'page': p['id'], 'page_job': p['job'], 'object': o['id'],
                     'box': o['box'], 'fit': o.get('fit', 'contain'),
                     'contributions': [c for c in p['contributions'] if o['id'] in c['objects']]}
                    for p in pages for o in p['objects'] if o.get('asset') == asset['id']]
            requests.append({**{k: v for k, v in asset.items() if k != 'sha256'},
                             'uses': uses})
            continue
        path = resolve(plan_file, asset['path'])
        if not path.is_file():
            issues.append('Asset file missing: ' + asset['id'])
        elif not asset.get('sha256') or sha(path) != asset['sha256']:
            issues.append('Asset changed/unfingerprinted: ' + asset['id'] + '; bind the actual chosen file')
    return issues, requests


def writer_input(plan_file, output_id):
    """Return resolved design/placements for a host writer; reject unbound artwork.

    Read-only preparation, not authoring, generation or permission to deliver.
    The caller consumes these returned pages/assets rather than a parallel plan.
    """
    plan = load(plan_file)
    output = next((o for o in plan['outputs'] if o['id'] == output_id), None)
    if output is None:
        raise ValueError('Unknown output id')
    pages = pages_for(plan, output)
    issues, _ = asset_issues(plan, plan_file, pages)
    if issues:
        raise ValueError('Artwork is not ready for this output. Continue next/bind/ingest:\n' + '\n'.join(issues))
    used = {o['asset'] for page in pages for o in page['objects'] if o['type'] == 'image'}
    assets = {a['id']: {**a, 'path': str(resolve(plan_file, a['path']))}
              for a in plan.get('assets', []) if a['id'] in used}
    # JSON copies prevent object-name decoration from changing the source plan.
    placements = json.loads(json.dumps(pages, allow_nan=False))
    for page in placements:
        for obj in page['objects']:
            obj['native_id'] = object_name(page['id'], obj['id'])
    return {
        'stage': 'ready_for_assembly',
        'plan_file': str(Path(plan_file).resolve()), 'plan_sha256': fingerprint(plan),
        'brief': plan['brief'], 'audience': plan['audience'], 'design': plan['design'],
        'output': {**output, 'path': str(output_path(plan_file, output['path']))},
        'assets': assets, 'pages': placements,
        **{key: plan[key] for key in ('font_family', 'pptx_width_inches') if key in plan},
        'limits': 'Prepared input only. Consume these assets/placements, inspect the exported artifact, and review actual TYY contribution. This does not call image tools, run a writer, or establish visual quality.'
    }


def bind(plan_file, asset_id, source, provenance, tool_ref=None):
    plan = load(plan_file)
    asset = next((a for a in plan.get('assets', []) if a['id'] == asset_id), None)
    if asset is None:
        raise ValueError('Unknown planned asset: ' + asset_id)
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ValueError('bind expects an accessible image file. For a returned data URL/base64 object, use ingest with the complete result JSON.')
    dest = output_path(plan_file, 'assets/' + asset_id + source.suffix.lower())
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source != dest:
        # Do not overwrite a different asset version; keep it recoverable.
        if dest.exists() and sha(dest) != sha(source):
            dest = dest.with_name(asset_id + '-' + sha(source)[:12] + source.suffix.lower())
        managed = {Path(plan_file).resolve()}
        for out in plan['outputs']:
            target = output_path(plan_file, out['path'])
            managed.update((target, receipt_path(target)))
            if out.get('review'):
                managed.add(output_path(plan_file, out['review']))
        if dest in managed:
            raise ValueError('Asset destination collides with a managed production file')
        if not dest.exists():
            shutil.copy2(source, dest)
    asset.update(path=dest.relative_to(Path(plan_file).resolve().parent).as_posix(),
                 sha256=sha(dest), provenance=provenance)
    if tool_ref:
        asset['tool_ref'] = tool_ref
    write_json(plan_file, plan)
    return {'bound': asset_id, 'path': asset['path'], 'sha256': asset['sha256']}


MAX_IMAGE_BYTES = 64 * 1024 * 1024
MAX_RESULT_BYTES = 96 * 1024 * 1024


def image_candidates(result):
    """Read explicit image envelopes, not arbitrary text/metadata strings."""
    found = []

    def visit(value, location='result', string_source=False):
        if isinstance(value, (bytes, bytearray, memoryview)):
            found.append({'bytes': bytes(value), 'location': location})
        elif isinstance(value, (str, Path)):
            if string_source:
                found.append({'source': str(value), 'location': location})
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, location + '[' + str(index) + ']', string_source)
        elif isinstance(value, dict):
            if isinstance(value.get('b64_json'), str):
                found.append({'base64': value['b64_json'], 'mime': value.get('mimeType') or value.get('mime_type'), 'location': location})
            elif isinstance(value.get('data'), str) and (value.get('type') == 'image' or str(value.get('mimeType') or value.get('mime_type', '')).startswith('image/')):
                found.append({'base64': value['data'], 'mime': value.get('mimeType') or value.get('mime_type'), 'location': location})
            else:
                for key in ('image_url', 'url', 'path', 'file_path', 'local_path'):
                    if key in value:
                        visit(value[key], location + '.' + key, True)
                for key in ('content', 'images', 'data', 'result', 'output', 'candidates', 'parts', 'inlineData', 'inline_data'):
                    if key in value and isinstance(value[key], (dict, list)):
                        visit(value[key], location + '.' + key)

    visit(result, string_source=True)
    return found


def image_bytes(result, select=None, base_dir=None):
    """Normalise a returned local path, data URL or explicit base64 envelope.

    No network calls. Signature recognition is not a render/decoder validation.
    """
    candidates = image_candidates(result)
    if not candidates:
        raise ValueError('No supported image payload found. Supply the actual image_url/data URL, accessible image path, b64_json or image content block; an opaque attachment id needs the host\'s supported file export first.')
    if select is None:
        if len(candidates) != 1:
            raise ValueError('Multiple image payloads returned; select the intended one with --select (zero based): ' + ', '.join(str(i) + '=' + c['location'] for i, c in enumerate(candidates)))
        select = 0
    if not isinstance(select, int) or select < 0 or select >= len(candidates):
        raise ValueError('Selected image index is outside the returned payloads')
    chosen = candidates[select]
    encoded = chosen.get('base64')
    mime = chosen.get('mime')
    if 'bytes' in chosen:
        data = chosen['bytes']
    elif encoded is None:
        value = chosen['source']
        if value.startswith('data:'):
            match = re.fullmatch(r'data:(image/[A-Za-z0-9.+-]+);base64,(.*)', value, re.DOTALL)
            if not match:
                raise ValueError('Expected a complete base64 image data URL; keep the original result rather than a printed/truncated excerpt')
            mime, encoded = match.groups()
        else:
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', value) or value.startswith(('blob:', 'attachment:', 'sandbox:')):
                raise ValueError('This result is a URL/attachment reference. Use the host\'s supported download/export to obtain its file, then bind that file. This helper does not fetch URLs or access private app endpoints.')
            path = Path(value).expanduser()
            if not path.is_absolute():
                path = Path(base_dir or Path.cwd()) / path
            path = path.resolve()
            if not path.is_file():
                raise ValueError('Returned image path is not accessible to this runtime: ' + str(path))
            if path.stat().st_size > MAX_IMAGE_BYTES:
                raise ValueError('Image exceeds this helper\'s 64 MiB limit; use an available host file-binding route')
            data = path.read_bytes()
    if encoded is not None:
        if len(encoded) > MAX_RESULT_BYTES:
            raise ValueError('Encoded image exceeds this helper\'s size limit')
        try:
            data = base64.b64decode(re.sub(r'\s+', '', encoded), validate=True)
        except ValueError as error:
            raise ValueError('Incomplete or invalid base64 image; transfer the untruncated tool result, not its chat preview') from error
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError('Image payload is empty or exceeds 64 MiB')
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        actual, extension = 'image/png', '.png'
    elif data.startswith(b'\xff\xd8\xff'):
        actual, extension = 'image/jpeg', '.jpg'
    elif data.startswith((b'GIF87a', b'GIF89a')):
        actual, extension = 'image/gif', '.gif'
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        actual, extension = 'image/webp', '.webp'
    elif data.startswith(b'BM'):
        actual, extension = 'image/bmp', '.bmp'
    elif data.startswith((b'II\x2a\x00', b'MM\x00\x2a')):
        actual, extension = 'image/tiff', '.tiff'
    else:
        raise ValueError('Payload lacks a supported raster image signature (PNG/JPEG/GIF/WebP/BMP/TIFF). Existing SVG/source assets can use the normal bind/host-writer route.')
    aliases = {'image/jpg': 'image/jpeg', 'image/x-ms-bmp': 'image/bmp', 'image/x-tiff': 'image/tiff'}
    if mime and aliases.get(str(mime).lower(), str(mime).lower()) != actual:
        raise ValueError('Declared image MIME type does not match its bytes')
    return data, extension, actual, chosen['location']


def read_image_result(source):
    """Read JSON from a file or stdin without printing image data."""
    if source == '-':
        text = sys.stdin.read(MAX_RESULT_BYTES + 1)
        base_dir = Path.cwd()
    else:
        path = Path(source).expanduser().resolve()
        if path.stat().st_size > MAX_RESULT_BYTES:
            raise ValueError('Image result JSON exceeds 96 MiB')
        text = path.read_text(encoding='utf-8-sig')
        base_dir = path.parent
    if len(text.encode('utf-8')) > MAX_RESULT_BYTES:
        raise ValueError('Image result JSON exceeds 96 MiB')
    return json.loads(text), base_dir


def save_image_result(result, destination, select=None, base_dir=None):
    """Save real image bytes for any file-based writer; no plan is required."""
    data, extension, mime, location = image_bytes(result, select, base_dir)
    path = Path(destination).expanduser().resolve()
    if not path.suffix:
        path = path.with_suffix(extension)
    equivalents = {'.jpeg': '.jpg', '.tif': '.tiff'}
    if equivalents.get(path.suffix.lower(), path.suffix.lower()) != extension:
        raise ValueError('Destination extension must match returned image bytes: ' + extension)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Destination already holds a different asset; choose a new path to retain the previous version')
    else:
        # Exclusive creation protects other files. Remove our incomplete file on
        # a write failure; never replace an existing source or production file.
        created = False
        try:
            with path.open('xb') as handle:
                created = True
                handle.write(data)
        except OSError:
            if created:
                path.unlink(missing_ok=True)
            raise
    return {'path': str(path), 'bytes': len(data), 'mime': mime,
            'sha256': sha(path), 'selected_payload': location,
            'check_scope': 'Recognised signature and saved bytes; actual decoding/render, visible meaning and placement still need inspection'}


def ingest_image_result(plan_file, asset_id, result, provenance, tool_ref=None, select=None, base_dir=None):
    """Normalise a host image result, then reuse the existing file binder."""
    plan = load(plan_file)
    if not any(a['id'] == asset_id for a in plan.get('assets', [])):
        raise ValueError('Unknown planned asset: ' + asset_id)
    data, extension, _, _ = image_bytes(result, select, base_dir)
    # The temporary stays inside this job and is removed after bind has copied
    # and fingerprinted it. bind retains prior asset versions and updates the map.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=Path(plan_file).resolve().parent,
                                         prefix='.visuasense-image-', suffix=extension, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        return bind(plan_file, asset_id, temporary, provenance, tool_ref)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def object_name(page_id, object_id):
    return 'vs::' + page_id + '::' + object_id


def xml_names(root):
    return {n.get('name') for n in root.findall('.//p:cNvPr', NS)}


def zip_target(source, target):
    return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(source), target))


def pptx_inspection(plan, artifact, plan_file, output):
    issues, evidence = [], []
    with ZipFile(artifact) as z:
        pres = ET.fromstring(z.read('ppt/presentation.xml'))
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels')).findall(REL)}
        ordered = [zip_target('ppt/presentation.xml', rels[n.get('{' + NS['r'] + '}id')]) for n in pres.findall('p:sldIdLst/p:sldId', NS)]
        selected_pages = pages_for(plan, output)
        if len(ordered) != len(selected_pages):
            issues.append('Delivered slide count differs from the production record')
        assets = {a['id']: a for a in plan.get('assets', [])}
        for page, name in zip(selected_pages, ordered):
            root = ET.fromstring(z.read(name))
            names = xml_names(root)
            relpath = posixpath.join(posixpath.dirname(name), '_rels', posixpath.basename(name) + '.rels')
            image_rels = {r.get('Id'): r for r in ET.fromstring(z.read(relpath)).findall(REL)} if relpath in z.namelist() else {}
            for obj in page['objects']:
                expected = object_name(page['id'], obj['id'])
                if expected not in names:
                    issues.append('Missing native object identity: ' + expected)
                    continue
                candidates = [n for n in list(root.find('p:cSld/p:spTree', NS)) if n.find('.//p:cNvPr', NS) is not None and n.find('.//p:cNvPr', NS).get('name') == expected]
                if len(candidates) != 1:
                    issues.append('Ambiguous object identity: ' + expected)
                    continue
                node = candidates[0]
                if obj['type'] == 'text':
                    wanted = re.sub(r'\s+', '', obj['text'])
                    # Native text content; visual line wrapping is reviewed separately.
                    actual = re.sub(r'\s+', '', ''.join(t.text or '' for t in node.findall('.//a:t', NS)))
                    if wanted != actual:
                        issues.append('Native copy differs: ' + expected)
                if obj['type'] == 'image':
                    blip = node.find('.//a:blip', NS)
                    rid = blip.get('{' + NS['r'] + '}embed') if blip is not None else None
                    rel = image_rels.get(rid)
                    if rel is None or rel.get('TargetMode') == 'External':
                        issues.append('Picture is missing or not embedded: ' + expected)
                    else:
                        target = zip_target(name, rel.get('Target', ''))
                        digest = hashlib.sha256(z.read(target)).hexdigest()
                        if digest != assets[obj['asset']]['sha256']:
                            issues.append('Embedded asset differs: ' + expected)
                    transform = node.find('.//a:xfrm', NS)
                    extent = transform.find('a:ext', NS) if transform is not None else None
                    if extent is None or int(extent.get('cx', 0)) <= 0 or int(extent.get('cy', 0)) <= 0:
                        issues.append('Picture has no positive native dimensions: ' + expected)
                if obj['type'] == 'table' and node.find('.//a:tbl', NS) is None:
                    issues.append('Expected native table: ' + expected)
                if obj['type'] == 'chart' and not any(e.tag.endswith('}chart') for e in node.iter()):
                    issues.append('Expected native chart: ' + expected)
            evidence.append({'page': page['id'], 'native_objects': len(names), 'pictures': len(root.findall('.//p:pic', NS))})
    return issues, evidence, ['PPTX identities, copy and picture bytes checked; full geometry, chart/table contents, rendered visibility and editing behaviour require actual host review.']


class HtmlInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.objects, self.images, self.texts, self.stack = {}, {}, {}, []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        key = data.get('data-vs-id')
        if key:
            self.objects[key] = self.objects.get(key, 0) + 1
            if tag == 'img':
                self.images[key] = data.get('src', '')
        if tag not in {'img', 'meta', 'link', 'br', 'hr', 'input', 'source'}:
            self.stack.append((tag, key or (self.stack[-1][1] if self.stack else None)))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        key = self.stack[-1][1] if self.stack else None
        if key:
            self.texts.setdefault(key, []).append(text)


def html_inspection(plan, artifact, plan_file, output):
    parser = HtmlInventory()
    parser.feed(Path(artifact).read_text(encoding='utf-8'))
    issues, evidence = [], []
    assets = {a['id']: a for a in plan.get('assets', [])}
    for page in pages_for(plan, output):
        for obj in page['objects']:
            key = object_name(page['id'], obj['id'])
            if parser.objects.get(key) != 1:
                issues.append('Missing/duplicate HTML object: ' + key)
            if obj['type'] == 'text' and re.sub(r'\s+', '', obj['text']) != re.sub(r'\s+', '', ''.join(parser.texts.get(key, []))):
                issues.append('HTML copy differs: ' + key)
            if obj['type'] == 'image':
                src = parser.images.get(key, '')
                if not src.startswith('data:') or ';base64,' not in src:
                    issues.append('Expected an embedded local image: ' + key)
                else:
                    digest = hashlib.sha256(base64.b64decode(src.split(';base64,', 1)[1], validate=True)).hexdigest()
                    if digest != assets[obj['asset']]['sha256']:
                        issues.append('Embedded HTML asset differs: ' + key)
        evidence.append({'page': page['id'], 'planned_objects': len(page['objects'])})
    return issues, evidence, ['HTML source bindings checked; browser-rendered visibility, copy fit and interactive behaviour require actual visual/runtime review.']


def receipt_path(artifact):
    return Path(str(artifact) + '.visuasense.json')


def inspect_output(plan, plan_file, out):
    artifact = output_path(plan_file, out['path'])
    if not artifact.is_file():
        return {'output': out['id'], 'issues': ['Artifact missing'], 'scope': 'No artifact inspected'}
    issues, _ = asset_issues(plan, plan_file, pages_for(plan, out))
    evidence, limits = [], []
    if not issues:
        if out['format'].lower() == 'pptx':
            more, evidence, limits = pptx_inspection(plan, artifact, plan_file, out)
            issues.extend(more)
        elif out['format'].lower() == 'html':
            more, evidence, limits = html_inspection(plan, artifact, plan_file, out)
            issues.extend(more)
        else:
            limits.append('No built-in structural inspector for this format. Actual source/asset/editing operations need host-supported inspection; file existence/hash alone do not verify them.')
    return {'output': out['id'], 'plan_sha256': fingerprint(plan), 'artifact_sha256': sha(artifact),
            'issues': issues, 'evidence': evidence, 'limits': limits,
            'scope': 'Mechanical bindings only; not a TYY quality judgment, rendered visibility or complete OOXML validation'}


def review_template(plan, plan_file, out, captures):
    artifact = output_path(plan_file, out['path'])
    if not artifact.is_file():
        raise ValueError('Create and inspect the actual requested artifact before preparing its review')
    selected = {p['id'] for p in pages_for(plan, out)}
    records = []
    for item in captures:
        pid, separator, path = item.partition('=')
        if not separator or pid not in selected:
            raise ValueError('Capture arguments must be page-id=actual-preview-path')
        source = resolve(plan_file, path)
        if not source.is_file():
            raise ValueError('Actual capture file missing: ' + path)
        records.append({'page': pid, 'path': path, 'sha256': sha(source)})
    if {r['page'] for r in records} != selected or len(records) != len(selected):
        raise ValueError('Provide one actual capture per delivered page')
    return {'status': 'unreviewed', 'reviewer': 'producer_self_review',
            'plan_sha256': fingerprint(plan), 'artifact_sha256': sha(artifact),
            'captures': records,
            'design_intent': {'assessment': 'unverified', 'evidence': '',
                              'missed_material_opportunities': []},
            'lenses': {key: {'assessment': None, 'evidence': '', 'remaining_cost': ''} for key in LENSES},
            'unresolved': ['Visual review pending'], 'delivery_limits': [],
            'notice': 'This is a file-bound review scaffold, not an executed visual review. Inspect the actual delivered renders, fill the evidence/limitations and unresolved issues, then set status to completed.'}


def review_issues(plan, plan_file, out, receipt):
    path = out.get('review')
    if not path or not resolve(plan_file, path).is_file():
        return ['Rendered visual review record missing']
    review = read_json(resolve(plan_file, path))
    errors = []
    if review.get('status') != 'completed':
        errors.append('Rendered visual review has not been completed')
    if review.get('artifact_sha256') != receipt.get('artifact_sha256') or review.get('plan_sha256') != fingerprint(plan):
        errors.append('Visual review is stale for this artifact/plan')
    if review.get('reviewer') not in {'producer_self_review', 'independent_reviewer'}:
        errors.append('Declare actual reviewer relationship; do not invent independence')
    intent = review.get('design_intent')
    if not isinstance(intent, dict):
        errors.append('Review the central TYY intent and opportunities omitted from the plan')
    else:
        if intent.get('assessment') != 'achieved':
            errors.append('Central TYY intent remains unmet or unverified')
        required_text(intent.get('evidence'), 'design_intent.evidence', errors)
        missed = intent.get('missed_material_opportunities')
        if not isinstance(missed, list):
            errors.append('Explicitly review missed material visual opportunities, including unplanned ones')
        elif missed:
            errors.append('Material visual opportunities remain unresolved: ' + str(missed))
    captures = review.get('captures', [])
    if not isinstance(captures, list) or not all(isinstance(c, dict) for c in captures) or {c.get('page') for c in captures} != {p['id'] for p in pages_for(plan, out)}:
        errors.append('Capture records must cover the actual delivered pages')
    else:
        for capture in captures:
            file = resolve(plan_file, capture.get('path', ''))
            if not file.is_file() or not capture.get('sha256') or sha(file) != capture['sha256']:
                errors.append('Capture missing/changed: ' + str(capture.get('page')))
    lenses = review.get('lenses', {})
    for lens in LENSES:
        item = lenses.get(lens, {})
        if item.get('assessment') not in {'strong', 'partial', 'absent', 'not_applicable'} or not item.get('evidence'):
            errors.append('Record visible evidence or justified n/a for TYY lens: ' + lens)
        elif item['assessment'] == 'absent':
            errors.append('Review reports an absent applicable TYY contribution: ' + lens)
        elif item['assessment'] == 'partial':
            required_text(item.get('remaining_cost'), lens + '.remaining_cost', errors)
    if not isinstance(review.get('unresolved'), list):
        errors.append('Review must explicitly record unresolved material issues')
    else:
        errors.extend(str(issue) for issue in review['unresolved'])
    if receipt.get('limits') and not review.get('delivery_limits'):
        errors.append('Record delivery-inspection limits honestly in the visual review')
    return errors


def status(plan, plan_file):
    issues, requests = asset_issues(plan, plan_file)
    if issues:
        return {'stage': 'produce_assets', 'issues': issues, 'shared_design': plan['design'], 'asset_requests': requests,
                'next': 'Produce the selected visuals through available tools and retain each full result. Bind an accessible file or ingest its actual result JSON; then continue assembly in this task.'}
    outputs = []
    for out in plan['outputs']:
        artifact = output_path(plan_file, out['path'])
        if not artifact.is_file():
            outputs.append({'output': out['id'], 'stage': 'assemble', 'next': 'Compose the bound artwork and planned information in their assigned regions, preserving the selected world, reading fields and shared identity.'})
            continue
        rp = receipt_path(artifact)
        if not rp.is_file():
            outputs.append({'output': out['id'], 'stage': 'inspect_delivery'})
            continue
        receipt = read_json(rp)
        if receipt.get('plan_sha256') != fingerprint(plan) or receipt.get('artifact_sha256') != sha(artifact):
            outputs.append({'output': out['id'], 'stage': 'inspect_delivery', 'issues': ['Mechanical receipt stale']})
            continue
        current = inspect_output(plan, plan_file, out)
        errors = current.get('issues', []) + review_issues(plan, plan_file, out, current)
        outputs.append({'output': out['id'], 'stage': 'repair_or_review' if errors else 'ready_with_declared_limits' if current.get('limits') else 'ready_for_delivery',
                        'issues': errors, 'limits': current.get('limits', [])})
    return {'outputs': outputs, 'semantic_review': 'Model/reviewer attestation bound to files; code does not certify understanding or visual quality.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('next', 'writer-input', 'inspect', 'assemble', 'review-template'):
        p = sub.add_parser(name)
        p.add_argument('plan')
        if name != 'next':
            p.add_argument('--output', required=True, help='Output id from the record')
        if name == 'assemble':
            p.add_argument('--replace', action='store_true', help='Replace an existing generated artifact, preserving the previous file')
        if name == 'review-template':
            p.add_argument('--capture', action='append', required=True, help='page-id=actual-render-path; repeat for all delivered pages')
    p = sub.add_parser('bind')
    p.add_argument('plan'); p.add_argument('asset'); p.add_argument('file')
    p.add_argument('--provenance', required=True); p.add_argument('--tool-ref')
    p = sub.add_parser('ingest', help='Save a returned image payload and bind it to its planned contribution')
    p.add_argument('plan'); p.add_argument('asset')
    p.add_argument('--result', required=True, help='Actual result JSON file or - for stdin; never a truncated preview')
    p.add_argument('--select', type=int, help='Choose one payload when the result contains several images (zero based)')
    p.add_argument('--provenance', required=True); p.add_argument('--tool-ref')
    p = sub.add_parser('save-image', help='Save returned image bytes for a host writer without a production record')
    p.add_argument('--result', required=True, help='Actual result JSON file or - for stdin')
    p.add_argument('--to', required=True, help='New local image path; its extension must match the bytes, or omit the extension')
    p.add_argument('--select', type=int)
    args = parser.parse_args()
    if args.command == 'bind':
        result = bind(args.plan, args.asset, args.file, args.provenance, args.tool_ref)
    elif args.command in {'ingest', 'save-image'}:
        value, base_dir = read_image_result(args.result)
        if args.command == 'ingest':
            result = ingest_image_result(args.plan, args.asset, value, args.provenance,
                                         args.tool_ref, args.select, base_dir)
        else:
            result = save_image_result(value, args.to, args.select, base_dir)
    else:
        plan = load(args.plan)
        if args.command == 'next':
            result = status(plan, args.plan)
        elif args.command == 'writer-input':
            result = writer_input(args.plan, args.output)
        else:
            out = next((o for o in plan['outputs'] if o['id'] == args.output), None)
            if out is None:
                raise ValueError('Unknown output id')
            if args.command == 'review-template':
                result = review_template(plan, args.plan, out, args.capture)
                print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
                return 0
            if args.command == 'assemble':
                errors, _ = asset_issues(plan, args.plan, pages_for(plan, out))
                if errors:
                    raise ValueError('\n'.join(errors))
                destination = output_path(args.plan, out['path'])
                if destination == Path(args.plan).resolve() or any(destination == resolve(args.plan, a['path']) for a in plan.get('assets', []) if a.get('path')):
                    raise ValueError('Output would overwrite the plan or a source asset')
                if destination.exists():
                    if not args.replace:
                        raise ValueError('Output already exists; --replace preserves its previous bytes before replacing it')
                    backup = destination.with_name(destination.name + '.previous-' + sha(destination)[:12])
                    if not backup.exists():
                        shutil.copy2(destination, backup)
                destination.parent.mkdir(parents=True, exist_ok=True)
                if out['format'].lower() == 'pptx':
                    from production_pptx import assemble
                elif out['format'].lower() == 'html':
                    from production_html import assemble
                else:
                    raise ValueError('Use the host writer for this requested format, retain the same design record, then inspect with honest scope limits')
                assemble({**plan, 'pages': pages_for(plan, out)}, args.plan, destination)
            result = inspect_output(plan, args.plan, out)
            if output_path(args.plan, out['path']).is_file():
                write_json(receipt_path(output_path(args.plan, out['path'])), result)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    pending = result.get('issues') or (args.command == 'next' and (
        not result.get('outputs') or any(
            item.get('stage') not in {'ready_for_delivery', 'ready_with_declared_limits'}
            for item in result['outputs'])))
    return 2 if pending else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError, BadZipFile, ET.ParseError) as error:
        print('Le_SensVisual production: ' + str(error), file=sys.stderr)
        sys.exit(1)
