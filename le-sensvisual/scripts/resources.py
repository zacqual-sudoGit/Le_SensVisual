#!/usr/bin/env python3
"""Resolve pinned optional resources without adding them to the skill or its context.

Resolution never accesses the network. Import a published companion (or preserved
complete package) explicitly. Only explicit engine setup downloads pinned assets.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOTS = ('le-sensvisual', 'visuasense')


def _manifest():
    return json.loads((ROOT / 'third-party/RESOURCES.json').read_text(encoding='utf-8'))


def _relative(value):
    """Accept portable relative file names, never drive paths or traversal."""
    if not isinstance(value, str) or not value or '\\' in value or '\x00' in value:
        raise ValueError('Resource paths must be non-empty portable relative paths')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in {'', '.', '..'} or ':' in p for p in value.split('/')):
        raise ValueError('Unsafe resource path: ' + value)
    return path.as_posix()


def cache_root():
    override = os.environ.get('VISUASENSE_CACHE')
    if override:
        base = Path(override).expanduser()
    elif os.name == 'nt':
        # Packaged Windows apps and restricted shells can virtualize LOCALAPPDATA
        # differently on every invocation. User home remains a stable cache root.
        base = Path.home() / '.cache/visuasense'
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library/Caches/visuasense'
    else:
        base = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'visuasense'
    base = base.resolve()
    if base == ROOT or base.is_relative_to(ROOT):
        raise ValueError('VISUASENSE_CACHE must be outside the skill folder')
    return base


def _group_root(group):
    root = cache_root()
    path = root / _relative(_manifest()['resourceSet']) / _relative(group)
    if not path.resolve().is_relative_to(root):
        raise RuntimeError('Resource group resolves outside the cache')
    return path


def _digest(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _check(path, expected):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Missing or non-regular resource: ' + str(path))
    if path.stat().st_size != expected['bytes'] or _digest(path) != expected['sha256']:
        raise RuntimeError('Resource does not match its pinned size/hash: ' + str(path))
    return path


def _contained_file(base, logical):
    logical = _relative(logical)
    path = base / logical
    current = base
    if current.is_symlink():
        raise RuntimeError('Resource containers must not be symlinks: ' + str(current))
    for part in PurePosixPath(logical).parts:
        current = current / part
        if current.is_symlink():
            raise RuntimeError('Resource paths must not contain symlinks: ' + str(current))
    if not path.resolve().is_relative_to(base.resolve()):
        raise RuntimeError('Resource path resolves outside its container: ' + str(path))
    return path


def _engine_record(logical):
    assets = json.loads((ROOT / 'third-party/ENGINE.json').read_text(encoding='utf-8'))['assets']
    for platform_id, entry in assets.items():
        name = 'impeccable.exe' if platform_id.startswith('windows-') else 'impeccable'
        if logical == f'runtime/engine/{platform_id}/{name}':
            return platform_id, entry
    return None


def resolve_resource(logical_path, required=True):
    """Return a verified shipped/cached file; absent optional files return None."""
    logical = _relative(logical_path)
    manifest = _manifest()
    group_id = None
    expected = None
    for candidate, group in manifest['groups'].items():
        if logical in group['members']:
            group_id, expected = candidate, group['members'][logical]
            break
    engine = _engine_record(logical)
    if expected is None and engine:
        group_id, expected = 'engine-' + engine[0], engine[1]
    if expected is None:
        raise ValueError('Resource is not declared in the pinned manifest: ' + logical)
    local = _contained_file(ROOT, logical)
    if local.exists() or local.is_symlink():
        return _check(local, expected)
    candidates = [_contained_file(_group_root(group_id), logical)]
    if engine and group_id != 'engine-' + engine[0]:
        candidates.append(_contained_file(_group_root('engine-' + engine[0]), logical))
    for candidate in candidates:
        if candidate.exists() or candidate.is_symlink():
            return _check(candidate, expected)
    if not required:
        return None
    archive = manifest['groups'].get(group_id, {}).get('archiveName')
    remedy = ('Import ' + archive + ' with resources.py import <archive>.') if archive else 'Run explicit setup --engine for this platform.'
    if engine:
        remedy += ' Engine setup can explicitly download the pinned platform binary.'
    raise FileNotFoundError(f'Optional resource is not present: {logical}. {remedy} No automatic download occurred.')


def resource_path(group_id, required=True):
    """Return a complete verified group root, shipped or externally cached."""
    group = _manifest()['groups'].get(group_id)
    if group is None:
        raise ValueError('Unknown resource group: ' + group_id)
    if all(_contained_file(ROOT, p).is_file() for p in group['members']):
        for logical, expected in group['members'].items():
            _check(_contained_file(ROOT, logical), expected)
        return ROOT
    cached = _group_root(group_id)
    if all(_contained_file(cached, p).is_file() for p in group['members']):
        for logical, expected in group['members'].items():
            _check(_contained_file(cached, logical), expected)
        return cached
    if required:
        raise FileNotFoundError('Import optional companion ' + group['archiveName'] + ' with resources.py import <archive>.')
    return None


def _promote(staging, destination):
    """Promote a fully checked private directory, preserving an interrupted prior copy."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink():
            raise RuntimeError('Cache destination must not be a symlink')
        backup = destination.with_name(destination.name + '.previous-' + uuid.uuid4().hex)
        destination.rename(backup)
    try:
        staging.rename(destination)
    except Exception:
        if backup and not destination.exists():
            backup.rename(destination)
        raise
    if backup:
        # Only the prior cache group under this explicitly resolved destination.
        if not backup.resolve().is_relative_to(cache_root()):
            raise RuntimeError('Prior cache path escaped the resource cache')
        shutil.rmtree(backup)


def import_companion(path):
    """Import every complete matching group from a ZIP or extracted skill folder.

    Companion ZIPs and extracted packages accept le-sensvisual/<logical-path>
    and legacy visuasense/<logical-path>. Complete older/offline packages are
    accepted when their resource bytes match these pins. Unrelated regular
    files are never extracted. Import is atomic for each resource group.
    """
    source = Path(path).expanduser().resolve()
    manifest = _manifest()
    archive = None
    entries = {}
    try:
        if source.is_dir():
            roots = [source / name for name in PACKAGE_ROOTS
                     if (source / name).is_dir() or (source / name).is_symlink()]
            if len(roots) > 1:
                raise ValueError('Companion contains both package roots; select one extracted skill folder')
            folder = roots[0] if roots else source
            for group in manifest['groups'].values():
                for logical in group['members']:
                    member = _contained_file(folder, logical)
                    if member.exists() or member.is_symlink():
                        if member.is_symlink():
                            raise ValueError('Companion must not contain symlinks: ' + logical)
                        entries[logical] = member
        else:
            archive = zipfile.ZipFile(source)
            seen = set()
            for info in archive.infolist():
                name = info.filename.rstrip('/')
                if not name:
                    continue
                _relative(name)
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise ValueError('Companion must not contain symlinks: ' + name)
                if stat.S_IFMT(info.external_attr >> 16) not in {0, stat.S_IFREG, stat.S_IFDIR}:
                    raise ValueError('Companion must contain only regular files/directories: ' + name)
                if info.is_dir():
                    continue
                logical = name
                for root in PACKAGE_ROOTS:
                    if name.startswith(root + '/'):
                        logical = name[len(root) + 1:]
                        break
                _relative(logical)
                if logical.casefold() in seen:
                    raise ValueError('Duplicate companion member: ' + logical)
                seen.add(logical.casefold())
                entries[logical] = info
        selected = [(key, group) for key, group in manifest['groups'].items() if set(group['members']).issubset(entries)]
        if not selected:
            raise ValueError('No complete pinned resource group found; import the unmodified companion ZIP or complete skill folder')
        imported = []
        for group_id, group in selected:
            destination = _group_root(group_id)
            destination.parent.mkdir(parents=True, exist_ok=True)
            staging = Path(tempfile.mkdtemp(prefix='.resource-', dir=destination.parent))
            try:
                for logical, expected in group['members'].items():
                    target = _contained_file(staging, logical)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    entry = entries[logical]
                    if archive:
                        if entry.file_size != expected['bytes']:
                            raise ValueError('Companion member size differs from pinned manifest: ' + logical)
                        with archive.open(entry) as reader, target.open('wb') as writer:
                            shutil.copyfileobj(reader, writer, length=1024 * 1024)
                    else:
                        _check(entry, expected)
                        shutil.copyfile(entry, target)
                    _check(target, expected)
                    if logical.startswith('runtime/engine/'):
                        target.chmod(0o755)
                _promote(staging, destination)
                imported.append({'group': group_id, 'directory': str(destination), 'files': len(group['members'])})
            finally:
                if staging.exists():
                    shutil.rmtree(staging)
        return {'imported': imported, 'scope': 'Verified local resources only; nothing executed or downloaded'}
    finally:
        if archive:
            archive.close()


def download_engine(platform_id):
    """Explicitly acquire only the real URL and hash pinned in ENGINE.json."""
    engine_manifest = json.loads((ROOT / 'third-party/ENGINE.json').read_text(encoding='utf-8'))
    if platform_id not in engine_manifest['assets']:
        raise ValueError('No pinned engine for platform: ' + platform_id)
    entry = engine_manifest['assets'][platform_id]
    if not entry['url'].startswith('https://github.com/pbakaus/impeccable/releases/download/'):
        raise ValueError('Unexpected engine download origin')
    name = 'impeccable.exe' if platform_id.startswith('windows-') else 'impeccable'
    logical = f'runtime/engine/{platform_id}/{name}'
    present = resolve_resource(logical, required=False)
    if present:
        return {'engine': str(present), 'status': 'already present; checksum verified; not executed'}
    destination = _group_root('engine-' + platform_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.engine-', dir=destination.parent))
    try:
        output = _contained_file(staging, logical)
        output.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(entry['url'], headers={'User-Agent': 'Le_SensVisual/' + _manifest()['version']})
        with urllib.request.urlopen(request, timeout=120) as response, output.open('wb') as writer:
            received = 0
            for chunk in iter(lambda: response.read(1024 * 1024), b''):
                received += len(chunk)
                if received > entry['bytes']:
                    raise RuntimeError('Engine response exceeds pinned size')
                writer.write(chunk)
        _check(output, entry)
        output.chmod(0o755)
        _promote(staging, destination)
        return {'engine': str(destination / logical), 'status': 'downloaded; checksum verified; not executed'}
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def describe_resources():
    manifest = _manifest()
    groups = []
    for group_id, group in manifest['groups'].items():
        # Inventory is deliberately cheap; actual use/import always verifies bytes.
        local = all(_contained_file(ROOT, p).is_file() for p in group['members'])
        cached = all(_contained_file(_group_root(group_id), p).is_file() for p in group['members'])
        groups.append({'id': group_id, 'archive': group['archiveName'], 'files': len(group['members']),
                       'bytes': sum(v['bytes'] for v in group['members'].values()),
                       'availability': 'shipped' if local else 'cached' if cached else 'not acquired',
                       'description': group['description']})
    return {'version': manifest['version'], 'cache': str(cache_root()), 'resources': groups,
            'note': 'Availability is inventory only. Import/use verifies pinned bytes. No implicit network or execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    importing = commands.add_parser('import', help='Import pinned resources from a ZIP/folder with a le-sensvisual or legacy visuasense root'); importing.add_argument('path')
    resolving = commands.add_parser('resolve'); resolving.add_argument('logical_path')
    downloading = commands.add_parser('download-engine'); downloading.add_argument('platform_id')
    args = parser.parse_args()
    if args.command == 'list':
        result = describe_resources()
    elif args.command == 'import':
        result = import_companion(args.path)
    elif args.command == 'resolve':
        result = {'path': str(resolve_resource(args.logical_path))}
    else:
        result = download_engine(args.platform_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print('Le_SensVisual resources: ' + str(error), file=sys.stderr)
        sys.exit(1)
