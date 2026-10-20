"""Dependency-free HTML/SVG adapter for resolved page objects and real artwork.

No layout inference, image generation, external fetch or browser operation.
The output preserves design coordinates; use actual browser review for fit/visibility.
"""
import base64
import html
import json
import math
from pathlib import Path
import tempfile

from production import object_name, resolve

IMAGE_MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
              '.jpe': 'image/jpeg', '.jfif': 'image/jpeg', '.gif': 'image/gif',
              '.svg': 'image/svg+xml', '.webp': 'image/webp', '.bmp': 'image/bmp',
              '.tif': 'image/tiff', '.tiff': 'image/tiff'}


def esc(value):
    return html.escape(str(value), quote=True)


def colour(value, fallback='24362D'):
    if value == 'none':
        return 'none'
    value = str(value or fallback).lstrip('#')
    if len(value) != 6 or any(c not in '0123456789abcdefABCDEF' for c in value):
        raise ValueError('Use six-digit RGB colours in the production record')
    return '#' + value


def font(value):
    # Font files are not silently fetched. Actual font availability needs review.
    return json.dumps(str(value), ensure_ascii=False)


def chart_svg(obj):
    w, h = obj['box'][2:]
    if w < 160 or h < 120:
        raise ValueError('Chart region is too small for this adapter; resolve its reading scale or use a suitable host writer')
    left, top, right, bottom = 48, 15, w - 18, h - 50
    values = [v for s in obj['series'] for v in s['values']]
    lo, hi = min(0, min(values)), max(0, max(values))
    if hi == lo:
        hi = lo + 1
    n, count = len(obj['categories']), len(obj['series'])
    ink = colour(obj.get('color'))
    parts = []

    def label(x, y, text, anchor='middle', size=14):
        parts.append(f'<text x="{x}" y="{y}" fill="{ink}" font-size="{size}" text-anchor="{anchor}">{esc(text)}</text>')

    def yvalue(v):
        return bottom - (v - lo) / (hi - lo) * (bottom - top)

    def xvalue(v):
        return left + (v - lo) / (hi - lo) * (right - left)

    if obj['kind'] == 'bar':
        band = (bottom - top) / n
        baseline = xvalue(0)
        parts.append(f'<path d="M{baseline},{top} V{bottom}" stroke="{ink}" fill="none"/>')
        for i, cat in enumerate(obj['categories']):
            label(left - 6, top + (i + .5) * band, cat, 'end', obj.get('font_size', 14))
            for j, series in enumerate(obj['series']):
                value = series['values'][i]
                x = min(baseline, xvalue(value))
                y = top + i * band + band * .12 + j * band * .76 / count
                width = abs(xvalue(value) - baseline)
                parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{band * .7 / count}" fill="{colour(series.get("color"), "176B68")}"/>')
        for value in (lo, hi):
            label(xvalue(value), bottom + 20, f'{value:g}')
    else:
        band = (right - left) / n
        baseline = yvalue(0)
        parts.append(f'<path d="M{left},{top} V{bottom} M{left},{baseline} H{right}" stroke="{ink}" fill="none"/>')
        label(left - 6, yvalue(lo), f'{lo:g}', 'end')
        label(left - 6, yvalue(hi) + 8, f'{hi:g}', 'end')
        for i, cat in enumerate(obj['categories']):
            label(left + (i + .5) * band, bottom + 20, cat, size=obj.get('font_size', 14))
        for j, series in enumerate(obj['series']):
            stroke = colour(series.get('color'), '176B68')
            if obj['kind'] == 'line':
                points = ' '.join(f'{left + (i + .5) * band},{yvalue(v)}' for i, v in enumerate(series['values']))
                parts.append(f'<polyline points="{points}" fill="none" stroke="{stroke}" stroke-width="2"/>')
            else:
                for i, value in enumerate(series['values']):
                    x = left + i * band + band * .12 + j * band * .76 / count
                    y = min(baseline, yvalue(value))
                    parts.append(f'<rect x="{x}" y="{y}" width="{band * .7 / count}" height="{abs(yvalue(value) - baseline)}" fill="{stroke}"/>')
    for j, series in enumerate(obj['series']):
        x = left + j * max(1, (right - left) / count)
        parts.append(f'<rect x="{x}" y="{h - 15}" width="10" height="10" fill="{colour(series.get("color"), "176B68")}"/>')
        label(x + 15, h - 5, series.get('name', ''), 'start', 12)
    return ''.join(parts)


def assemble(plan, plan_file, destination):
    assets = {a['id']: a for a in plan.get('assets', [])}
    pages, print_rules = [], []
    for page in plan['pages']:
        width, height = page['size']
        objects = []
        for obj in page['objects']:
            x, y, w, h = obj['box']
            identity = esc(object_name(page['id'], obj['id']))
            style = f'left:{x}px;top:{y}px;width:{w}px;height:{h}px;opacity:{obj.get("opacity",1)};'
            attrs = f'data-vs-id="{identity}" data-vs-type="{esc(obj["type"])}"'
            typ = obj['type']
            if typ == 'image':
                source = resolve(plan_file, assets[obj['asset']]['path'])
                mime = IMAGE_MIME.get(source.suffix.lower())
                if mime is None:
                    raise ValueError('Unsupported image MIME type for ' + str(source))
                data = base64.b64encode(source.read_bytes()).decode('ascii')
                fit = {'contain': 'contain', 'cover': 'cover', 'stretch': 'fill'}[obj.get('fit', 'contain')]
                objects.append(f'<img class="o" {attrs} style="{esc(style + "object-fit:" + fit)}" alt="{esc(assets[obj["asset"]]["description"])}" src="data:{mime};base64,{data}">')
            elif typ == 'text':
                text_style = style + f'font-family:{font(obj.get("font_family",plan.get("font_family","Arial")))};font-size:{obj.get("font_size",24)}px;line-height:{obj.get("line_spacing",1.15)};color:{colour(obj.get("color"))};font-weight:{700 if obj.get("bold") else 400};font-style:{"italic" if obj.get("italic") else "normal"};text-align:{obj.get("align","left")};padding:{obj.get("padding",0)}px;white-space:pre-wrap;overflow:visible;'
                vertical = obj.get('vertical', 'top')
                if vertical in {'middle', 'bottom'}:
                    text_style += 'display:flex;flex-direction:column;justify-content:' + ('center' if vertical == 'middle' else 'flex-end') + ';'
                objects.append(f'<div class="o" {attrs} style="{esc(text_style)}">{esc(obj["text"])}</div>')
            elif typ == 'table':
                rows = []
                for i, row in enumerate(obj['rows']):
                    tag = 'th' if i == 0 else 'td'
                    bg = colour(obj.get('header_fill') if i == 0 else obj.get('fill'), 'FFFFFF')
                    rows.append('<tr>' + ''.join(f'<{tag} style="background:{bg};padding:{obj.get("padding",8)}px">{esc(v)}</{tag}>' for v in row) + '</tr>')
                table_style = style + f'border-collapse:collapse;table-layout:fixed;font-family:{font(obj.get("font_family",plan.get("font_family","Arial")))};font-size:{obj.get("font_size",20)}px;color:{colour(obj.get("color"))};text-align:{obj.get("align","left")};'
                objects.append(f'<table class="o" {attrs} style="{esc(table_style)}">{"".join(rows)}</table>')
            else:
                fill, stroke = colour(obj.get('fill'), 'none') if obj.get('fill') else 'none', colour(obj.get('stroke'), 'none') if obj.get('stroke') else 'none'
                geom = f'fill="{fill}" stroke="{stroke}" stroke-width="{obj.get("stroke_width",1)}"'
                if typ == 'chart':
                    content = chart_svg(obj)
                elif typ == 'shape':
                    kind = obj.get('geometry', 'rect')
                    if kind == 'ellipse':
                        content = f'<ellipse cx="{w/2}" cy="{h/2}" rx="{w/2}" ry="{h/2}" {geom}/>'
                    elif kind in {'triangle', 'chevron'}:
                        pts = [(w/2, 0), (w, h), (0, h)] if kind == 'triangle' else [(0, 0), (w*.65, 0), (w, h/2), (w*.65, h), (0, h), (w*.35, h/2)]
                        content = f'<polygon points="{" ".join(f"{a},{b}" for a,b in pts)}" {geom}/>'
                    else:
                        radius = obj.get('radius', min(w,h) * .1667) if kind == 'round_rect' else 0
                        content = f'<rect width="{w}" height="{h}" rx="{radius}" {geom}/>'
                else:
                    points = ' '.join(f'{a-x},{b-y}' for a, b in obj['points'])
                    if typ == 'polygon':
                        content = f'<polygon points="{points}" {geom}/>'
                    else:
                        arrow_id = esc('arrow-' + page['id'] + '-' + obj['id'])
                        line_colour = colour(obj.get('stroke'))
                        marker = f'<defs><marker id="{arrow_id}" orient="auto" markerWidth="8" markerHeight="8" refX="7" refY="4"><path d="M0,0 L8,4 L0,8 Z" fill="{line_colour}"/></marker></defs>' if obj.get('arrow') else ''
                        ending = f'marker-end="url(#{arrow_id})"' if obj.get('arrow') else ''
                        content = marker + f'<polyline points="{points}" fill="none" stroke="{line_colour}" stroke-width="{obj.get("stroke_width",2)}" {ending}/>'
                objects.append(f'<svg class="o" {attrs} style="{esc(style + "overflow:visible")}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(obj.get("description",obj["id"]))}">{content}</svg>')
        pid = esc(page['id'])
        print_rules.append(f'@page page-{pid}{{size:{width}px {height}px;margin:0}} #page-{pid}{{page:page-{pid}}}')
        pages.append(f'<section class="viewport" id="page-{pid}" data-width="{width}" data-height="{height}" aria-label="{esc(page["job"])}"><div class="canvas slide" style="width:{width}px;height:{height}px;background:{colour(page.get("background"),"FFFFFF")}">{"".join(objects)}</div></section>')
    title = esc(plan.get('title', 'Visual material'))
    output = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#e5e7e8}}.viewport{{position:relative;width:100%;margin:0 auto 24px;overflow:hidden}}.canvas{{position:absolute;top:0;left:0;transform-origin:top left;overflow:hidden}}.o{{position:absolute;margin:0}}td,th{{vertical-align:top}}@media print{{body{{background:none}}.viewport[hidden]{{display:block!important}}.viewport{{margin:0;break-after:page;width:var(--w)!important;height:var(--h)!important}}.canvas{{transform:none!important}}}}{''.join(print_rules)}</style>
<main>{''.join(pages)}</main><script>
function fit(){{for(const v of document.querySelectorAll('.viewport')){{const w=Number(v.dataset.width),h=Number(v.dataset.height),s=v.clientWidth/w;v.style.height=(h*s)+'px';v.style.setProperty('--w',w+'px');v.style.setProperty('--h',h+'px');v.querySelector('.canvas').style.transform='scale('+s+')';}}}}
addEventListener('resize',fit);fit();window.presentation={{goToSlide(i){{document.querySelectorAll('.viewport').forEach((v,j)=>v.hidden=j!==i);fit();}}}};
</script></html>'''
    destination = Path(destination)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='.visuasense-', suffix='.html', dir=destination.parent, delete=False) as f:
        temporary = Path(f.name)
        f.write(output)
    try:
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()

