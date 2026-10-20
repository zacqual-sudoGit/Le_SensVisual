#!/usr/bin/env node
/* Cross-platform scaffold/render/inspect/PDF. Requires Playwright for browser operations. */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2), command=args.shift();
function option(name,fallback){const i=args.indexOf(`--${name}`);return i>=0?args[i+1]:fallback;}
const positional=[];
for(let i=0;i<args.length;i++){
 if(['--title','--width','--height','--slide'].includes(args[i])){if(args[i+1]===undefined)throw Error(`Missing value for ${args[i]}`);i++;}
 else if(['--full-page','--editable'].includes(args[i]))continue;
 else if(args[i].startsWith('--'))throw Error(`Unknown option ${args[i]}`);
 else positional.push(args[i]);
}
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function scaffold(mode,out){
 if(!['deck','editorial','interface'].includes(mode)||!out)throw Error('scaffold deck|editorial|interface <output.html>');
 const title=option('title','Untitled'),w=Number(option('width',1920)),h=Number(option('height',1080));
 if(!Number.isFinite(w)||!Number.isFinite(h)||w<100||h<100)throw Error('Invalid stage dimensions');
 const css=fs.readFileSync(path.join(root,'assets/authoring.css'),'utf8');
 let content=mode==='deck'?`<div class="deck-viewport"><main class="deck-stage" data-width="${w}" data-height="${h}" data-editing="${args.includes('--editable')}"><section class="slide active"><h1 data-editable>${esc(title)}</h1><p data-editable>Replace this shell with the resolved focal composition.</p></section><section class="slide"><h2 data-editable>Supporting explanation</h2><p data-editable>Construct the subject objects, relationships and calm reading field.</p></section></main></div>`:`<main class="editorial"><header><h1>${esc(title)}</h1></header><section aria-label="Main explanation"><!-- Build the resolved subject-specific composition here. --></section></main>`;
 const runtime=mode==='deck'?`<script>${fs.readFileSync(path.join(root,'assets/deck-runtime.js'),'utf8')}</script>`:'';
 const html=`<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><style>${css}\n:root{--stage-width:${w}px;--stage-height:${h}px}@page{size:${mode==='deck'?`${w}px ${h}px`:'A4'};margin:${mode==='deck'?'0':'0'}}</style></head><body>${content}${runtime}</body></html>`;
 fs.mkdirSync(path.dirname(path.resolve(out)),{recursive:true});fs.writeFileSync(out,html);console.log(JSON.stringify({file:path.resolve(out),mode,status:'shell; author the actual design'}));
}
function browserModule(){
 const locations=[root,process.cwd(),...(process.env.VISUASENSE_NODE_MODULES||'').split(path.delimiter).filter(Boolean)];
 for(const base of locations){const req=createRequire(path.join(path.resolve(base),'package.json'));for(const name of ['playwright','playwright-core'])try{return req(name);}catch{}}
 throw Error('Playwright unavailable. Use an existing browser tool or install playwright in your chosen runtime; see references/tools.md.');
}
async function browserTask(input,output){
 if(!input)throw Error(`${command} <input.html> [output]`);
 const file=path.resolve(input);if(!fs.statSync(file).isFile())throw Error('Input must be an HTML file');
 const base=fs.realpathSync(path.dirname(file));
 const mime={'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.woff2':'font/woff2','.json':'application/json'};
 const server=http.createServer((req,res)=>{
  try{const decoded=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const p=path.resolve(base,'.'+(decoded==='/'?'/'+path.basename(file):decoded));
   if(p!==base&&!p.startsWith(base+path.sep)){res.writeHead(403);res.end();return;}
   const real=fs.realpathSync(p);
   const relative=path.relative(base,real);
   if(relative==='..'||relative.startsWith('..'+path.sep)||path.isAbsolute(relative)||relative.split(path.sep).some(part=>part.startsWith('.'))){res.writeHead(403);res.end();return;}
   const content=fs.readFileSync(real);res.writeHead(200,{'Content-Type':mime[path.extname(real)]||'application/octet-stream'});res.end(content);
  }catch{res.writeHead(404);res.end('Not found');}
 });
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 let browser;
 try{
  const {chromium}=browserModule();
  const executable=process.env.VISUASENSE_BROWSER;
  browser=await chromium.launch({headless:true,...(executable?{executablePath:executable}:{})});
  const page=await browser.newPage({viewport:{width:Number(option('width',1440)),height:Number(option('height',1000))},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',err=>errors.push(err.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/`,{waitUntil:'load',timeout:30000});
  await page.evaluate(()=>Promise.race([document.fonts.ready,new Promise(resolve=>setTimeout(resolve,8000))]));
  const slide=Number(option('slide',1));
  await page.evaluate(i=>{
   if(window.presentation?.goToSlide)window.presentation.goToSlide(i-1);
   else document.querySelector('deck-stage')?.goTo?.(i-1);
  },slide);
  await page.waitForTimeout(400);
  if(command==='inspect'){
   const result=await page.evaluate(()=>{
    const visible=el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)>0&&r.width>0&&r.height>0&&!el.closest('[aria-hidden="true"]');};
    const nodes=[...document.body.querySelectorAll('*')].filter(visible);
    return {title:document.title,slides:document.querySelector('deck-stage')?.length??document.querySelectorAll('.slide').length,
     brokenImages:[...document.images].filter(im=>visible(im)&&(!im.complete||im.naturalWidth===0)).map(im=>im.getAttribute('src')),
     overflow:nodes.filter(el=>!['BODY','HTML','SVG','PATH','SCRIPT','STYLE'].includes(el.tagName)&&el.scrollWidth>el.clientWidth+2&&el.clientWidth>0).slice(0,50).map(el=>({tag:el.tagName,class:el.className?.baseVal??el.className,text:el.textContent?.trim().slice(0,70)})),
     fontsReady:document.fonts.status==='loaded',width:innerWidth,height:innerHeight};
   });
   result.pageErrors=errors;result.scope='Current viewport/slide only; no semantic TYY certification';
   const json=JSON.stringify(result,null,2);if(output){fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});fs.writeFileSync(output,json);}console.log(json);
   if(result.brokenImages.length||result.pageErrors.length)process.exitCode=2;
  }else{
   if(!output)throw Error('Output file required');fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});
   if(command==='pdf')await page.pdf({path:output,printBackground:true,preferCSSPageSize:true});
   else await page.screenshot({path:output,fullPage:args.includes('--full-page'),animations:'disabled'});
   console.log(JSON.stringify({file:path.resolve(output),command,slide,source:file,pageErrors:errors}));
   if(errors.length)process.exitCode=2;
  }
 }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
}
try{
 if(command==='scaffold')scaffold(positional[0],positional[1]);
 else if(['render','inspect','pdf'].includes(command))await browserTask(positional[0],positional[1]);
 else {console.log('Usage: artifact.mjs scaffold <deck|editorial|interface> <file> [--title text --width n --height n --editable]\n       artifact.mjs render|inspect|pdf <html> [output] [--width n --height n --slide n --full-page]');if(command&&command!=='--help')process.exitCode=1;}
}catch(error){console.error(error.message);process.exitCode=1;}
