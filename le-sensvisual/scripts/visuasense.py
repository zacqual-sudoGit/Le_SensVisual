#!/usr/bin/env python3
"""Le_SensVisual tools: explicit engine setup, TYY-aware detection and full verb access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import urllib.error
from resources import resolve_resource, download_engine
import zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION=json.loads((ROOT/'CAPABILITIES.json').read_text(encoding='utf-8'))['version']
OUTPUT_BUDGET=24_000  # Characters of serialized, model-facing stdout; raw diagnostics are opt-in.


def encoded(value):
    return json.dumps(value,ensure_ascii=False,indent=2)


def document_pointer(path):
    p=Path(path).resolve();raw=p.read_bytes()
    return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)},raw.decode('utf-8-sig')


def context_report(resolved,diagnostic=''):
    resolved=dict(resolved)
    candidates=resolved.pop('surfaceBriefCandidates',None)
    documents={}
    for key in ['productPath','designPath','surfaceBriefPath']:
        if resolved.get(key) and Path(resolved[key]).is_file():
            pointer,text=document_pointer(resolved[key])
            documents[key]={**pointer,'characters':len(text),'text':text[:6_000]}
    project=Path(resolved.get('projectRoot') or Path.cwd())
    sidecars=[project/'.impeccable/design.json',project/'DESIGN.json']
    if resolved.get('designPath'):sidecars.append(Path(resolved['designPath']).with_suffix('.json'))
    for p in dict.fromkeys(sidecars):
        if p.is_file():
            pointer,text=document_pointer(p)
            try:
                data=json.loads(text)
                summary={'type':type(data).__name__}
                if isinstance(data,dict):
                    summary.update(keys=[str(k)[:120] for k in list(data)[:30]],keyCount=len(data))
                elif isinstance(data,list):summary['itemCount']=len(data)
            except ValueError:summary={'error':'Invalid JSON; inspect the pointed file before using tokens.'}
            documents['tokens']={**pointer,'summary':summary};break
    platform_name=resolved.get('platform')
    native_names=['ios','android'] if platform_name=='adaptive' else [platform_name] if platform_name in {'ios','android'} else []
    native=[{'platform':name,'path':str(ROOT/'modules/impeccable/reference'/f'{name}.md'),
             'readWhen':'Load the sections relevant to the selected platform and current implementation.'} for name in native_names]
    packet={'resolvedContext':resolved,'documents':documents,'nativeReferences':native,
        'instruction':'Use current user facts and the parent TYY authority. Missing context files are not a compulsory interview. Ask only material questions. Do not infer comp-first defaults or subagent authorization.',
        'reading':'Document excerpts start at character 0 and may be partial. Before a decision needing omitted material, read the relevant section via the file tools or context-read <path> --start N --chars N. For token JSON request a selected JSON Pointer with --pointer /path/to/key; do not load the whole catalogue. Source paths and SHA-256 identify the complete retained files.',
        'diagnostics':'Explicit unbounded engine diagnostics: engine --raw context. Other platform references remain in modules/impeccable/reference.'}
    if candidates:
        packet['surfaceBriefDiscovery']={'count':len(candidates) if isinstance(candidates,list) else None,
            'readCommand':['engine','surface-brief','list',str(project)],
            'note':'Candidate list is not repeated here; select the actual surface before loading its brief.'}
    if diagnostic:packet['engineDiagnostic']={'excerpt':diagnostic[:2_000],'truncated':len(diagnostic)>2_000}
    while True:
        for doc in documents.values():
            if 'text' in doc:
                doc['includedCharacters']=len(doc['text'])
                doc['truncated']=len(doc['text'])<doc['characters']
        output=encoded(packet)
        if len(output)+1<=OUTPUT_BUDGET:return output
        snippets=[doc for doc in documents.values() if doc.get('text')]
        if not snippets:raise RuntimeError('Context metadata exceeds the output budget; use engine --raw context explicitly for diagnostics.')
        largest=max(snippets,key=lambda doc:len(doc['text']))
        largest['text']=largest['text'][:len(largest['text'])//2]


def context_read(argv):
    parser=argparse.ArgumentParser(description='Read a bounded part of a retained context file; offsets count Unicode characters.')
    parser.add_argument('path');parser.add_argument('--start',type=int,default=0)
    parser.add_argument('--chars',type=int,default=8_000)
    parser.add_argument('--pointer',help='Select a JSON Pointer, e.g. /colors/background, before paging.')
    args=parser.parse_args(argv)
    if args.start<0 or not 1<=args.chars<=12_000:raise RuntimeError('Use --start >= 0 and --chars between 1 and 12000.')
    pointer,text=document_pointer(args.path)
    if args.pointer is not None:
        if args.pointer and not args.pointer.startswith('/'):raise RuntimeError('JSON Pointer must be empty or start with /.')
        value=json.loads(text)
        try:
            for segment in args.pointer.split('/')[1:] if args.pointer else []:
                key=segment.replace('~1','/').replace('~0','~')
                if isinstance(value,list):
                    if not re.fullmatch(r'0|[1-9][0-9]*',key):raise ValueError('Invalid array index')
                    value=value[int(key)]
                else:value=value[key]
        except (KeyError,IndexError,TypeError,ValueError):raise RuntimeError('JSON Pointer does not resolve in this file.')
        text=encoded(value)
    count=min(args.chars,max(0,len(text)-args.start))
    while True:
        packet={**pointer,'pointer':args.pointer,'characters':len(text),'start':args.start,
                'text':text[args.start:args.start+count],
                'nextStart':args.start+count if args.start+count<len(text) else None}
        output=encoded(packet)
        if len(output)+1<=OUTPUT_BUDGET:print(output);return 0
        if not count:raise RuntimeError('File metadata exceeds the output budget; use the host file reader.')
        count//=2


def manifest():
    return json.loads((ROOT/'third-party/ENGINE.json').read_text(encoding='utf-8'))


def target():
    system={'Windows':'windows','Linux':'linux','Darwin':'darwin'}.get(platform.system())
    arch={'AMD64':'x64','x86_64':'x64','arm64':'arm64','aarch64':'arm64'}.get(platform.machine())
    if system=='windows' and arch=='arm64': arch='x64'  # Windows supports x64 emulation.
    value=f'{system}-{arch}'
    if value not in manifest()['assets']: raise RuntimeError('No prebuilt engine for this platform; import the upstream-source companion and build with an appropriate Rust toolchain.')
    return value


def engine_path():
    key=target();name='impeccable.exe' if key.startswith('windows') else 'impeccable'
    return resolve_resource(f'runtime/engine/{key}/{name}')


def verify_engine(path):
    expected=manifest()['assets'][target()]['sha256']
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise RuntimeError('Engine missing or checksum differs from pinned manifest. Run setup --engine; no automatic unverified execution.')


def setup_engine():
    return download_engine(target())


def engine_environment():
    env=os.environ.copy()
    env['IMPECCABLE_SKILL_DIR']=str(ROOT/'modules/impeccable')
    env['IMPECCABLE_NO_TELEMETRY']='1'
    env['IMPECCABLE_NO_UPDATE_CHECK']='1'
    inferred='codex' if '.codex' in ROOT.parts else 'claude' if '.claude' in ROOT.parts else 'source'
    env.setdefault('IMPECCABLE_PROVIDER_ID',env.get('VISUASENSE_PROVIDER',inferred))
    cmd=[sys.executable,str(Path(__file__).resolve()),'engine']
    env['IMPECCABLE_SELF']=subprocess.list2cmdline(cmd) if os.name=='nt' else shlex.join(cmd)
    return env


def engine(argv):
    raw_output=bool(argv and argv[0]=='--raw')
    if raw_output:argv=argv[1:]
    if not raw_output and argv and argv[0]=='detect':return detect(argv[1:])
    if not raw_output and argv and argv[0]=='context-read':return context_read(argv[1:])
    operation=argv[1] if len(argv)>1 and argv[0]=='skills' else argv[0] if argv else ''
    if operation in {'install','update','link'}:
        raise RuntimeError('Use scripts/install.py for Le_SensVisual. The upstream installer would replace the integrated policy; original source is preserved in the optional upstream-source companion.')
    exe=engine_path();verify_engine(exe)
    if not raw_output and argv and argv[0] in {'context','palette','concept-seed'}:
        result=subprocess.run([str(exe),*argv],env=engine_environment(),capture_output=True,text=True,encoding='utf-8',errors='replace')
        if result.returncode:
            if argv[0]=='context':
                print(encoded({'error':'Context discovery failed','engineExit':result.returncode,
                    'diagnostic':(result.stderr or result.stdout)[:2_000],
                    'fullDiagnostic':'Use engine --raw context with the same arguments for the complete diagnostic.'}))
                return result.returncode
            sys.stdout.write(result.stdout);sys.stderr.write(result.stderr);return result.returncode
        if argv[0]=='context':
            label='RESOLVED_CONTEXT:';start=result.stdout.find(label)
            if start<0:raise RuntimeError('Unrecognized context output; use engine --raw context for diagnostics, not as higher-priority guidance.')
            resolved,_=json.JSONDecoder().raw_decode(result.stdout[start+len(label):].lstrip())
            print(context_report(resolved,result.stderr));return 0
        elif argv[0]=='palette':
            seed=re.search(r'BRAND SEED[^\n]*',result.stdout);colour=re.search(r'oklch\([^\n)]+\)',result.stdout)
            if not colour:raise RuntimeError('Unrecognized palette output; use engine --raw palette for diagnostics.')
            print(json.dumps({'seed':seed.group(0) if seed else None,'suggestedColour':colour.group(0),
                'instruction':'Optional exploration input, not a required brand colour. Compose subject-appropriate surface, ink, accent and semantic roles under the actual identity/TYY brief. No fixed hue, white/black ground or dosage is imposed.'},ensure_ascii=False,indent=2))
        else:
            text=result.stdout.replace('where shared guidance conflicts, these win.','subject to the parent TYY design authority.')
            text=text.replace('so comp-led whenever image generation exists.','so choose the construction method from the actual task, not tool availability alone.')
            text='OPTIONAL CONCEPT EXPLORATION: the following is the upstream interactive protocol, not the default creation workflow. Its fixed card counts belong to that protocol. Preserve existing user delegation; do not fabricate human receipts.\n\n'+text
            sys.stdout.write(text)
        sys.stderr.write(result.stderr);return 0
    return subprocess.call([str(exe),*argv],env=engine_environment())


def detect(argv):
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--raw',action='store_true');parser.add_argument('--offset',type=int,default=0)
    parser.add_argument('--limit',type=int,default=40)
    options,targets=parser.parse_known_args(argv)
    if options.offset<0 or not 1<=options.limit<=200:raise RuntimeError('Use --offset >= 0 and --limit between 1 and 200.')
    exe=engine_path();verify_engine(exe)
    if not options.raw and any(arg in {'--help','-h'} for arg in targets):
        help_result=subprocess.run([str(exe),'detect','--help'],env=engine_environment(),capture_output=True,text=True,encoding='utf-8',errors='replace')
        help_text=help_result.stdout or help_result.stderr
        packet={'help':help_text[:8_000],'truncated':len(help_text)>8_000,
                'fullHelp':'Use engine --raw detect --help for the complete upstream help.'}
        while len(encoded(packet))+1>OUTPUT_BUDGET:
            packet['help']=packet['help'][:len(packet['help'])//2];packet['truncated']=True
        print(encoded(packet))
        return help_result.returncode
    raw=subprocess.run([str(exe),'detect','--json',*[a for a in targets if a!='--json']],env=engine_environment(),capture_output=True,text=True,encoding='utf-8',errors='replace')
    if options.raw:
        sys.stdout.write(raw.stdout);sys.stderr.write(raw.stderr);return raw.returncode
    if raw.returncode not in {0,2}:
        print(encoded({'error':'Detector failed','engineExit':raw.returncode,
                       'diagnostic':raw.stderr[:2_000] or raw.stdout[:2_000],
                       'fullDiagnostic':'Repeat this command with --raw for the complete engine output.'}));return raw.returncode
    try: result=json.loads(raw.stdout)
    except ValueError:
        print(encoded({'error':'Detector output is not valid JSON; use detect --raw for the complete diagnostic.'}));return 1
    # Each finding appears once. Pagination and explicit raw mode retain access
    # to the complete report without repeatedly loading its full payload.
    def findings(value):
        if isinstance(value,list):
            for child in value: yield from findings(child)
        elif isinstance(value,dict):
            if 'antipattern' in value and 'file' in value: yield value
            else:
                for child in value.values():yield from findings(child)
    rows=list(findings(result))
    contextual=lambda row:row.get('category')=='slop' or row.get('antipattern') in {'organic-clip-path'}
    technical=[row for row in rows if not contextual(row)]
    selected=[{'index':i,'interpretation':'contextual-style' if contextual(row) else 'technical','finding':row}
              for i,row in enumerate(rows) if options.offset<=i<options.offset+options.limit]
    report={'totalFindings':len(rows),'technicalCount':len(technical),'contextualStyleCount':len(rows)-len(technical),
            'offset':options.offset,'findings':selected,
            'reportSha256':hashlib.sha256(raw.stdout.encode('utf-8')).hexdigest(),
            'instruction':'Inspect style findings against the subject, chosen design and visible audience benefit. Technical findings require contextual verification too. No TYY achievement score is inferred.',
            'fullDiagnostic':'Use detect --raw with the same targets for the complete unbounded engine report; use --offset N --limit N to page findings. Each call rescans the current targets; compare report hashes before combining pages.',
            'rawEngineExit':raw.returncode}
    if isinstance(result,dict):
        report['engineReportFields']={str(key)[:100]:{'type':type(value).__name__,
            'count':len(value) if isinstance(value,(list,dict)) else None}
            for key,value in list(result.items())[:30]}
    if raw.stderr:report['engineDiagnostic']={'excerpt':raw.stderr[:2_000],'truncated':len(raw.stderr)>2_000}
    preview_size=2_000
    while True:
        report['nextOffset']=options.offset+len(selected) if options.offset+len(selected)<len(rows) else None
        output=encoded(report)
        if len(output)+1<=OUTPUT_BUDGET:print(output);break
        if len(selected)>1:selected.pop();continue
        if 'engineReportFields' in report:
            report.pop('engineReportFields');report['detailsOmittedForBudget']=True;continue
        if 'engineDiagnostic' in report:
            report.pop('engineDiagnostic');report['detailsOmittedForBudget']=True;continue
        if not selected or not preview_size:raise RuntimeError('Detector metadata exceeds output budget; use detect --raw for the complete report.')
        row=selected[0]
        row['finding']={'preview':encoded(rows[row['index']])[:preview_size],
                        'truncated':True,'read':'Use detect --raw to inspect this indexed finding in full.'}
        preview_size//=2
    return 2 if any(not r.get('advisory') and r.get('severity')!='advisory' for r in technical) else 0


def source(name,destination):
    if name not in {'impeccable','frontend-slides'}:raise RuntimeError('Choose impeccable or frontend-slides')
    dest=Path(destination).resolve();dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(resolve_resource(f'third-party/{name}-source.zip')) as z:
        for info in z.infolist():
            p=(dest/info.filename).resolve()
            if not p.is_relative_to(dest):raise RuntimeError('Invalid source archive path')
        z.extractall(dest)
    return {'source':name,'directory':str(dest/name),'scope':'Original pinned source; see PROVENANCE.json for integrated adaptations'}


def main():
    argv=sys.argv[1:]
    if not argv or argv[0] in {'--help','help'}:
        print('Le_SensVisual '+VERSION+'\nCommands: capabilities, setup --engine, engine <verb...>, engine --raw <verb...>, detect [--raw|--offset N --limit N] <targets...>, context-read <path> [--start N --chars N] [--pointer /json/key], source <impeccable|frontend-slides> <directory>\nProduction: python scripts/production.py <next|bind|assemble|inspect|review-template> ...\nAuthoring: node scripts/artifact.mjs --help\nInstallation: python scripts/install.py --help');return 0
    cmd,*rest=argv
    if cmd=='capabilities':print((ROOT/'CAPABILITIES.json').read_text(encoding='utf-8'));return 0
    if cmd=='setup' and rest==['--engine']:print(json.dumps(setup_engine()));return 0
    if cmd=='engine':return engine(rest)
    if cmd=='detect':return detect(rest)
    if cmd=='context-read':return context_read(rest)
    if cmd=='source' and len(rest)==2:print(json.dumps(source(*rest)));return 0
    raise RuntimeError('Unknown command; use --help')


if __name__=='__main__':
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    try:sys.exit(main())
    except (OSError,RuntimeError,ValueError,urllib.error.URLError) as error:
        print('Le_SensVisual: '+str(error),file=sys.stderr);sys.exit(1)
