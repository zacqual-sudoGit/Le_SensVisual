#!/usr/bin/env python3
"""Install Le_SensVisual with existing-copy backups; migrate legacy Codex/Claude skills."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from resources import import_companion

ROOT=Path(__file__).resolve().parents[1]
SKILL_NAME='le-sensvisual'
LEGACY_NAME='visuasense'
HOSTS={'codex':'.codex/skills','claude-code':'.claude/skills','cursor':'.cursor/skills',
 'gemini-cli':'.gemini/skills','copilot':'.github/skills','agents':'.agents/skills',
 'grok':'.grok/skills','kiro':'.kiro/skills','opencode':'.opencode/skills','pi':'.pi/skills',
 'omp':'.omp/skills','qoder':'.qoder/skills','trae':'.trae/skills','trae-cn':'.trae-cn/skills',
 'rovodev':'.rovodev/skills','vibe':'.vibe/skills','antigravity':'.agent/skills','hermes':'.hermes/skills'}


def _delivery_files():
    manifest_path=ROOT/'DELIVERY.json'
    if not manifest_path.is_file():
        raise ValueError('DELIVERY.json is required; use an unmodified Le_SensVisual release')
    data=json.loads(manifest_path.read_text(encoding='utf-8'))
    paths=data.get('files')
    if data.get('schemaVersion',data.get('schema_version'))!=1 or not isinstance(paths,list) or not paths:
        raise ValueError('Unrecognized delivery manifest')
    result=[];seen=set()
    for entry in paths:
        name=entry.get('path') if isinstance(entry,dict) else entry
        if not isinstance(name,str) or not name or '\\' in name or name.startswith('/') or any(p in {'','..','.'} or ':' in p for p in name.split('/')):
            raise ValueError('Unsafe delivery path: '+str(name))
        if name.casefold() in seen:
            raise ValueError('Duplicate delivery path: '+name)
        seen.add(name.casefold())
        path=ROOT/name
        current=ROOT
        for part in name.split('/'):
            current=current/part
            if current.is_symlink():raise ValueError('Delivery files must not contain symlinks: '+name)
        if not path.resolve().is_relative_to(ROOT) or not path.is_file():
            raise ValueError('Missing or invalid delivery file: '+name)
        result.append((name,path))
    if not {'skill.md','delivery.json','scripts/resources.py','third-party/resources.json'}.issubset(seen):
        raise ValueError('Delivery manifest omits required entry/loading files')
    return result


def _migrates_legacy(base,host):
    if host in {'codex','claude-code'}:
        return True
    if base.name=='skills' and base.parent.name in {'.codex','.claude'}:
        return True
    codex_home=os.environ.get('CODEX_HOME')
    return bool(codex_home and base==(Path(codex_home).expanduser()/'skills').resolve())


def _legacy_installation(base,host):
    legacy=base/LEGACY_NAME
    if not _migrates_legacy(base,host) or not (legacy.exists() or legacy.is_symlink()):
        return None
    marker=legacy/'SKILL.md'
    if legacy.is_symlink() or not legacy.is_dir() or marker.is_symlink() or not marker.is_file():
        raise ValueError('Legacy visuasense must be a real skill directory before migration: '+str(legacy))
    header=marker.read_text(encoding='utf-8-sig').split('---',2)
    if len(header)!=3 or header[0].strip() or not re.search(r'''(?m)^name:[ \t]*(?:visuasense|'visuasense'|"visuasense")[ \t]*$''',header[1]):
        raise ValueError('Legacy directory does not identify the visuasense skill; inspect it before migration: '+str(legacy))
    return legacy


def install(base,resources=None,host=None):
    # Only declared delivery files are installed. Acquired software, construction
    # companions and accidental caches never expand later installations.
    files=_delivery_files()
    base=Path(base).expanduser().resolve();dest=base/SKILL_NAME
    if dest==ROOT or dest.is_relative_to(ROOT) or ROOT.is_relative_to(dest):
        raise ValueError('Installation destination must be separate from the source package')
    if dest.is_symlink():
        raise ValueError('Choose a real installation directory, not a symlink')
    if dest.exists() and not dest.is_dir():
        raise ValueError('Installation destination must be a directory: '+str(dest))
    legacy=_legacy_installation(base,host)
    if legacy and ROOT.is_relative_to(legacy) and ROOT!=legacy:
        raise ValueError('Legacy migration must not move a parent of the source package')
    acquired=[import_companion(path) for path in (resources or [])]
    base.mkdir(parents=True,exist_ok=True)
    # Copy fully before moving an existing installation. Stage outside discovery.
    staging_parent=base.parent/'visuasense-backups'
    if staging_parent.is_symlink() or staging_parent.resolve().is_relative_to(base):
        raise ValueError('Installation backups must be outside skill discovery in a real directory')
    staging_parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='visuasense-stage-',dir=staging_parent))
    candidate=staging/SKILL_NAME
    backups=[]
    try:
        candidate.mkdir()
        for name,source in files:
            target=candidate/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        for previous in [dest,legacy]:
            if previous is None or not previous.exists():
                continue
            stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
            backup=staging_parent/(previous.name+'-'+stamp)
            previous.rename(backup)
            backups.append((previous,backup))
        candidate.rename(dest)
    except Exception as error:
        restore_errors=[]
        for previous,backup in reversed(backups):
            try:
                if previous.exists() or previous.is_symlink():
                    raise RuntimeError('Original path is occupied: '+str(previous))
                backup.rename(previous)
            except Exception as restore_error:
                restore_errors.append(str(restore_error))
        raise RuntimeError(f'Installation interrupted: {error}. Staged files: {staging}. Prior-copy backups: {[str(backup) for _,backup in backups]}. Restore errors: {restore_errors}; inspect these paths before retrying.') from error
    staging.rmdir()
    return {'installed':str(dest),'backup':next((str(backup) for previous,backup in backups if previous==dest),None),
            'legacy_backup':next((str(backup) for previous,backup in backups if previous==legacy),None),
            'files':len(files),'resources':acquired,
            'scope':'Manifest-declared native files only. Explicit resource imports use the separate cache. No host hooks, connectors or browser extension installed.'}


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--host',choices=HOSTS,help='Host skill directory; Codex/Claude Code also back up a legacy visuasense skill outside discovery');group.add_argument('--destination',help='Parent directory for le-sensvisual; recognized Codex/Claude Code skill roots also migrate legacy visuasense')
    p.add_argument('--project',help='Install under this project instead of user home')
    p.add_argument('--resources',action='append',default=[],help='Explicitly import a companion ZIP or extracted complete folder (le-sensvisual or legacy visuasense root) into the separate resource cache; may repeat')
    args=p.parse_args()
    base=Path(args.destination) if args.destination else Path(args.project).resolve()/HOSTS[args.host] if args.project else Path(os.environ['CODEX_HOME'])/'skills' if args.host=='codex' and os.environ.get('CODEX_HOME') else Path.home()/HOSTS[args.host]
    print(json.dumps(install(base,args.resources,host=args.host),ensure_ascii=False))
