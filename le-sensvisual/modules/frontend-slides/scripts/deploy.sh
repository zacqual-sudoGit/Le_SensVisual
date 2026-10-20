#!/usr/bin/env bash
# Optional Vercel publisher. Run only for an explicitly authorized public deploy.
# Usage: bash deploy.sh <prepared-public-folder|presentation.html>
# Requires Bash, Python 3, Node/npx and an authenticated Vercel account.
set -euo pipefail
if [[ $# -ne 1 ]]; then
    echo 'Usage: bash deploy.sh <prepared-public-folder|presentation.html>' >&2
    exit 1
fi
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
command -v npx >/dev/null || { echo 'Node/npx is required.' >&2; exit 1; }
INPUT="$1"
TEMP_ROOT=$(mktemp -d -t visuasense-deploy.XXXXXXXX)
# Only this exact mktemp-created directory is removed, never a user input path.
trap 'rm -rf -- "$TEMP_ROOT"' EXIT
DEPLOY_DIR="$TEMP_ROOT/presentation"
python3 - "$INPUT" "$DEPLOY_DIR" <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import unquote, urlsplit

source=Path(sys.argv[1]).resolve(strict=True)
destination=Path(sys.argv[2]).resolve()
destination.mkdir()
blocked={'.git','.env','.aws','.codex','.claude','.gemini','node_modules','__pycache__'}

def permitted(path):
    return not any(p in blocked or (p.startswith('.') and p != '.well-known') for p in path.parts)

if source.is_dir():
    # Folder mode is for an intentionally prepared public build, not a repo root.
    if not (source/'index.html').is_file():
        raise ValueError('The public build folder needs index.html')
    for path in source.rglob('*'):
        relative=path.relative_to(source)
        if not permitted(relative):continue
        resolved=path.resolve(strict=True)
        if not resolved.is_relative_to(source):
            raise ValueError(f'Asset escapes public folder: {relative}')
        if path.is_file():
            target=destination/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(resolved,target)
elif source.is_file() and source.suffix.lower()=='.html':
    base=source.parent
    seen=set()
    css_url=re.compile(r'''url\(\s*["']?([^\s)'";]+)''',re.I)
    css_import=re.compile(r'''@import\s+["']([^"']+)''',re.I)
    class References(HTMLParser):
        def __init__(self):
            super().__init__();self.items=[]
        def handle_starttag(self,tag,attrs):
            for key,value in attrs:
                if value and key in ('src','href','poster'):self.items.append(value)
                if value and key=='srcset' and not value.lstrip().startswith('data:'):
                    self.items.extend(part.strip().split()[0] for part in value.split(',') if part.strip())
    def include(path, target=None):
        resolved=path.resolve(strict=True)
        if not resolved.is_relative_to(base) or not permitted(resolved.relative_to(base)):
            raise ValueError(f'Asset outside permitted presentation folder: {path}')
        if resolved in seen:return
        seen.add(resolved)
        if not resolved.is_file():raise ValueError(f'Expected an asset file: {path}')
        target=target or destination/path.relative_to(base)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(resolved,target)
        if resolved.suffix.lower() not in ('.css','.html','.htm'):return
        text=resolved.read_text(encoding='utf-8-sig')
        refs=list(css_url.findall(text))+list(css_import.findall(text))
        if resolved.suffix.lower() in ('.html','.htm'):
            parser=References();parser.feed(text);refs+=parser.items
        for ref in refs:
            url=urlsplit(ref)
            if url.scheme or url.netloc or not url.path:continue
            if url.path.startswith('/'):
                raise ValueError('Root-relative assets need a prepared public build folder')
            include(resolved.parent/unquote(url.path))
    include(source,destination/'index.html')
else:
    raise ValueError('Choose a prepared public folder or HTML file')
print('Prepared static files. Review JS/import dependencies separately; use a built public folder for bundled apps.')
PY
if command -v vercel >/dev/null; then
    VERCEL=(vercel)
else
    # npx may download the Vercel CLI; no global installation or hidden login.
    VERCEL=(npx --yes vercel)
fi
if ! "${VERCEL[@]}" whoami; then
    echo 'Sign in using the Vercel CLI in your normal terminal, then rerun.' >&2
    exit 1
fi
"${VERCEL[@]}" deploy "$DEPLOY_DIR" --yes --prod
# The CLI reports the actual deployment result/URL; availability and costs follow
# the hosting account's current terms. No permanent/free claim is made here.
