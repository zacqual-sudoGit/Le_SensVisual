/* Le_SensVisual deck runtime. Native text editing does not edit raster lettering. */
(() => {
  'use strict';
  const stage = document.querySelector('.deck-stage');
  const slides = [...document.querySelectorAll('.slide')];
  if (!stage || !slides.length) return;
  const width = Number(stage.dataset.width) || 1920;
  const height = Number(stage.dataset.height) || 1080;
  const editable = [...document.querySelectorAll('[data-editable]')];
  const canEdit = stage.dataset.editing === 'true' && editable.length > 0;
  // A revised source deck must not silently inherit edits from an older revision.
  const revision = JSON.stringify(editable.map(el => [el.dataset.editId, el.textContent]));
  const key = `visuasense:${document.documentElement.dataset.deckId || location.pathname}:${revision}`;
  editable.forEach((el, i) => { el.dataset.editId ||= `text-${i}`; });
  let edits = {};
  try { if (canEdit) edits = JSON.parse(localStorage.getItem(key) || '{}'); } catch { /* storage optional */ }
  editable.forEach(el => {
    if (Object.hasOwn(edits, el.dataset.editId)) el.textContent = String(edits[el.dataset.editId]);
  });
  const controls = document.createElement('nav');
  controls.className = 'deck-controls'; controls.setAttribute('aria-label', 'Presentation controls');
  controls.innerHTML = '<button data-action="previous" aria-label="Previous slide">←</button><output aria-live="polite"></output><button data-action="next" aria-label="Next slide">→</button><button data-action="edit" aria-pressed="false">Edit text</button><button data-action="save">Download HTML</button><span class="edit-status" aria-live="polite"></span>';
  if (!canEdit) controls.querySelector('[data-action="edit"]').remove();
  document.body.append(controls);
  let index = 0, editing = false, lastWheel = 0, pointer = null;
  const field = target => target instanceof Element && !!target.closest('input,textarea,select,[contenteditable="true"],[contenteditable="plaintext-only"]');
  function scale() {
    const factor = Math.min(innerWidth / width, innerHeight / height);
    stage.style.width = `${width}px`; stage.style.height = `${height}px`;
    stage.style.transform = `translate(${(innerWidth-width*factor)/2}px, ${(innerHeight-height*factor)/2}px) scale(${factor})`;
  }
  function goToSlide(value) {
    index = Math.max(0, Math.min(slides.length-1, Number(value) || 0));
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i===index); slide.classList.toggle('visible', i===index);
      slide.setAttribute('aria-hidden', String(i!==index)); slide.inert = i!==index;
    });
    controls.querySelector('output').textContent = `${index+1} / ${slides.length}`;
    controls.querySelector('[data-action="previous"]').disabled = index===0;
    controls.querySelector('[data-action="next"]').disabled = index===slides.length-1;
    document.documentElement.style.setProperty('--deck-progress', String((index+1)/slides.length));
  }
  function toggleEdit() {
    if (!canEdit) return;
    editing = !editing;
    editable.forEach(el => {
      if (editing) el.setAttribute('contenteditable', 'plaintext-only');
      else el.removeAttribute('contenteditable');
    });
    document.body.classList.toggle('editing', editing);
    controls.querySelector('[data-action="edit"]').setAttribute('aria-pressed', String(editing));
  }
  editable.forEach(el => el.addEventListener('input', () => {
    edits[el.dataset.editId] = el.textContent;
    try { localStorage.setItem(key, JSON.stringify(edits)); controls.querySelector('.edit-status').textContent='Saved in this browser'; }
    catch { controls.querySelector('.edit-status').textContent='Download to keep changes'; }
  }));
  function download() {
    const clone = document.documentElement.cloneNode(true);
    clone.querySelectorAll('.deck-controls').forEach(el => el.remove());
    clone.querySelectorAll('[contenteditable]').forEach(el => el.removeAttribute('contenteditable'));
    clone.querySelector('body').classList.remove('editing');
    clone.querySelector('.deck-stage').style.transform='';
    clone.querySelectorAll('.slide').forEach((el,i) => {
      el.classList.toggle('active',i===0);el.classList.toggle('visible',i===0);el.removeAttribute('inert');el.removeAttribute('aria-hidden');
    });
    const url = URL.createObjectURL(new Blob(['<!doctype html>\n'+clone.outerHTML], {type:'text/html;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download=(document.title||'presentation').replace(/[^\w.-]+/g,'-')+'.html';a.click();
    setTimeout(()=>URL.revokeObjectURL(url),2000);
  }
  controls.addEventListener('click', event => {
    const action=event.target.closest('button')?.dataset.action;
    if(action==='previous')goToSlide(index-1);if(action==='next')goToSlide(index+1);
    if(action==='edit')toggleEdit();if(action==='save')download();
  });
  document.addEventListener('keydown', event => {
    if ((event.ctrlKey||event.metaKey) && event.key.toLowerCase()==='s') {event.preventDefault();download();return;}
    if(field(event.target))return;
    if(canEdit && event.key.toLowerCase()==='e'){event.preventDefault();toggleEdit();return;}
    if(editing || event.altKey || event.ctrlKey || event.metaKey)return;
    const steps={ArrowRight:1,ArrowDown:1,PageDown:1,' ':1,ArrowLeft:-1,ArrowUp:-1,PageUp:-1};
    if(event.key in steps){event.preventDefault();goToSlide(index+steps[event.key]);}
    else if(event.key==='Home'){event.preventDefault();goToSlide(0);}
    else if(event.key==='End'){event.preventDefault();goToSlide(slides.length-1);}
  });
  stage.addEventListener('wheel', event => {
    if(editing || field(event.target) || Math.abs(event.deltaY)<12)return;
    event.preventDefault();
    if(performance.now()-lastWheel>450){goToSlide(index+Math.sign(event.deltaY));lastWheel=performance.now();}
  },{passive:false});
  stage.addEventListener('pointerdown', event => {
    if(event.pointerType==='touch'&&!editing&&!field(event.target))pointer={id:event.pointerId,x:event.clientX,y:event.clientY};
  });
  stage.addEventListener('pointerup', event => {
    if(!pointer||pointer.id!==event.pointerId)return;
    const dx=event.clientX-pointer.x,dy=event.clientY-pointer.y;pointer=null;
    if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5)goToSlide(index-Math.sign(dx));
  });
  stage.addEventListener('pointercancel',()=>{pointer=null;});
  addEventListener('blur',()=>{pointer=null;});addEventListener('resize',scale);
  window.presentation={goToSlide,showSlide:goToSlide,toggleEdit,download,get currentSlide(){return index;},get editing(){return editing;}};
  scale();goToSlide(0);
})();
