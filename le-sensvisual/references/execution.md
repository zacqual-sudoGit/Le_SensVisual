# Carry the composition through actual tool results

These helpers implement the [production](production.md) workflow for file-capable
hosts. New visual PPTX follows the [presentation recipe](presentations.md).
Its working map can be the writer's actual asset/layout structure or the checked
record below. Whole-image generation uses its image tool and visual review
directly. Other media, narrow edits and accepted-artifact conversion retain scope.

## Direct writer or checked record: the same dependencies

Read the actual host tool instructions and use its required writer/runtime.
A direct writer's consumed source associates each planned illustration with its
actual asset and placement. The AI makes the real generation/sourcing calls;
the writer loads those returned files/asset IDs before dependent placement.
Keep missing required assets as failed/unfinished dependencies. Inspect the
actual export's media, editable information and visual result. An unused plan
or a claim of equivalence cannot replace these operations.

The checked route supplies those file dependencies through `production.json` and
`writer_input`, or a bundled writer. Ordinary chat does not inherit a Codex skill
loader/filesystem; use its supported inputs and name an actual missing operation.
Neither route chooses worthwhile imagery or guarantees compliance by itself.

## Using the checked record

Resolve the [design](design-decisions.md), including supporting regions, and put
it in one `production.json` in the job folder. This replaces a duplicate map,
not a useful existing design system. The coordinator and writers consume its
actual geometry/asset bindings; inspection compares them with delivery.

Continue within the user's original task:

1. Resolve concrete visual expressions and their useful ambition from the
   audience/subject, then assign methods capable of their intended treatment.
2. Write the resolved composition and regional requests into the record. This
   selection is the AI's responsibility: `next` cannot discover an image or
   opportunity that was never planned. Record the scenes, illustrated objects and
   relationships needed to realise those benefits, with their placements.
3. Read `next`. Use the host's suitable image/sourcing tools for the requested
   parts; obtain the actual returned files and bind them. Record editable
   text, labels and measured relationships as the corresponding objects. Carry shared world, meaning and identity into
   every tool call, including local scenes and quiet reading fields.
4. Call `assemble` for a compatible bundled adapter, or have the host writer
   consume `writer_input(plan_file, output_id)`. It rejects missing/changed
   referenced assets before returning the selected pages, real file paths and
   shared design. Build from that result rather than a second interpretation
   of the brief. Inspect the actual artifact.
5. Render/reopen that exported artifact through a supported host renderer. View
   every page; harmonise the parts, restore missing expressions and reconsider
   worthwhile opportunities the record missed. Check content, reading and required
   operations separately. Reinspect after producer-owned changes.
6. Complete the file-bound visual review honestly, then deliver the artifact.

`next` reports work remaining; it does not run an AI, choose imagery or call an
image service. Its returned requests are instructions for the AI to dispatch
through actual available tools; printing them does not perform generation.
A picture displayed separately in chat has not reached a slide.
Use actual returned file/attachment transfer supported by the host. If the host
cannot access those bytes, identify that operation and find a supported route.
Do not invent an asset path or silently substitute generic text cards.

## Retain and save the actual image result

Use this handoff for artwork going into an assembled artifact. It adapts the
successful Gardens run's retrieve-file → place-asset pattern without its private
SDK, paths or layout. Data-URL ingestion and JS retention are new, untested code.
Keep the real result before leaving the generation call.
Choose the route for what the host actually returns:

| Actual result | Operation |
|---|---|
| Accessible image file | Reuse `bind` for a managed record, or load the file directly in the selected writer. |
| Image bytes/data URL/base64 object | Save the full payload, then bind/load the resulting file. Use the functions or commands below. |
| Download URL/opaque attachment ID | Obtain its file through the host's supported export/download first. These helpers perform no network or private-app requests. |

The Python functions accept raw image bytes and paths. JSON inputs accept a data
URL or local path as a string; `image_url`
(string or `{url:...}`), `b64_json`, image blocks with `data` and MIME type, and
`content`/`images`/`data`/`result`/`output` arrays containing those forms. It saves
PNG/JPEG/GIF/WebP/BMP/TIFF bytes. Supply a complete result, not its printed preview.
Multiple payloads require explicit zero-based `--select`; choose by the intended
region, not array order alone. Relative image paths resolve beside the result
JSON file. Existing SVG/source assets retain the normal bind/host-writer route.

**Python host, result already in memory:** use the existing module directly.
Resolve `scripts/` through that host's normal module/file mechanism. Choose the
standalone saver or the managed binder according to the existing authoring route.

```python
from production import save_image_result

# result is the actual returned value, not a retyped or shortened excerpt.
saved = save_image_result(result, "job/assets/clinic")
# Give saved["path"] to the existing writer. It identifies the real saved file.
```

For the managed production record, use this instead:

```python
from production import ingest_image_result
bound = ingest_image_result("job/production.json", "clinic-scene", result,
                            provenance="Actual image tool/source")
```

**Result arrives in a separate JavaScript tool context:** retain it through a
file-capable Node runtime with `scripts/retain_image_result.mjs`. Its exported
`retainImageResult(result, responseFile)` writes the complete JSON without
printing image data. Pass data through the tool API, not a shell command string.
Then reuse the Python coordinator:

```text
python scripts/production.py save-image --result job/image-result.json --to job/assets/clinic
python scripts/production.py ingest job/production.json clinic-scene --result job/image-result.json --provenance "Actual image tool/source"
```

Choose one saving operation. For the checked record, `ingest` saves and binds in
one step; an already saved image uses `bind`, then a host writer can consume
`writer_input`. A direct writer can use `save-image` or the host's supported
file transfer and consume those actual paths in its own placement structure.
Both saving operations return small path/hash summaries. File JSON or
stdin (`--result -`) avoids command-line image-data limits. The standalone saver
retains existing files; `ingest` reuses `bind`'s fingerprint/version handling.
Size/signature checks are structural, not image decoding, visual or TYY review.
The receiver still needs to support that image format.

For the Codex orchestration-to-file bridge, use the conditional [host recipe](tools.md#conditional-codex-image-result-bridge). Other hosts use their own file-capable runtime or supported attachment export; the Python operations above have no Codex dependency.

## Record contract

UTF-8 JSON; `schema_version: 1`. IDs start with a letter, then letters, digits,
hyphens or underscores. Each array's IDs are unique. Values below describe fields,
not a prescribed layout, style, asset count or final subject.

| Field | What the AI supplies |
|---|---|
| `brief`, `audience` | Actual task and viewers. |
| `design` | Concrete `world`, `meaning`, `relationships`, `composition`, `harmony` decisions. |
| `assets` | Chosen generated/sourced/provided files, each with `id`, `origin`, `description`; generated or unbound assets also need a regional `request`. `bind` records `path`, `sha256`, declared `provenance` and optional `tool_ref`. |
| `pages` | Each has `id`, `job`, `size: [width,height]`, optional RGB `background` and factual `notes`, plus `contributions` and `objects`. |
| `contributions` | Per-page entries with `id`, audience `benefit`, concrete visible `expression`, and `objects: [object-id,...]`. Connect every selected image to its contribution. Also review important opportunities absent from this inventory. |
| `objects` | Back-to-front actual objects, each with `id`, `type`, `box: [x,y,width,height]`. Use positive dimensions; coordinates are design units, including font sizes and strokes. Negative positions permit deliberate edge crops, but not wholly off-canvas objects. |
| `outputs` | Each has `id`, requested `format`, job-relative `path`, and `review` path declared before production. Optional `pages: [page-id,...]` chooses a subset/order; otherwise all pages. |
| Optional root values | `font_family` names an available chosen font; `pptx_width_inches` sets physical PPTX width. |

Declare all requested outputs and their page variants before dependent work.
Shared intent/assets do not require identical geometry in a poster and a deck.
PPTX requires one aspect ratio per deck. Each output points to its intended pages;
there is no image-first or editable-default branch.

### Object fields supported by the bundled adapters

RGB colours are six hexadecimal digits, optionally prefixed `#`. File paths are
relative to the record unless absolute reads are needed. Helper writes stay in
the job directory. Object order controls layering; opacity is explicit fading,
not a substitute for a calm reading field.

| `type` | Additional fields |
|---|---|
| `text` | `text`; optional `font_family`, `font_size`, `color`, `bold`, `italic`, `align` (left/center/right), `vertical` (top/middle/bottom), `line_spacing` (ratio), `padding`. Native text, no automatic shrinking. |
| `image` | `asset` ID; `fit` (contain/cover/explicit stretch), optional `opacity` greater than 0 up to 1. PPTX adapter accepts PNG/JPEG/GIF/BMP/TIFF; HTML additionally accepts SVG/WebP. Use another capable writer for other media. |
| `shape` | `geometry` (rect/round_rect/ellipse/triangle/chevron), optional `fill`, `stroke`, `stroke_width`, `radius` for round_rect, `opacity`. |
| `polygon` | `points: [[x,y],...]` in page coordinates, optional fill/stroke/stroke_width/opacity. |
| `line` | Page-coordinate `points`, optional `stroke`, `stroke_width`, `arrow`. Give its box positive bounds even for horizontal/vertical strokes. |
| `table` | Rectangular `rows`, optional font_family/font_size/color/align/padding/fill/header_fill. First row is the header. |
| `chart` | `kind` (bar/column/line), `categories`, `series: [{name,values,color}]`; optional font_family/font_size/color. Actual numeric values, truthful scales and actual/illustrative source status remain the AI's responsibility. |

All objects can carry a short `description`. Shapes/polygons support `none` for
transparent fill/stroke. Other opacity treatments, complex masks, rich text,
advanced charts, animations and layout features need a capable host writer.
Unsupported object fields/types are rejected rather than silently discarded.
The simple HTML chart is SVG; the PPTX chart/table is native. These adapters
do not promise pixel-identical typography or editability of painted details.

### Small record fragment

Within an already resolved page, a faded local scene and editable text might be:

```json
"contributions": [{
  "id": "reader-context",
  "benefit": "Make the reading experience tangible alongside its explanation",
  "expression": "Reader using the proposed service in a recognisable library",
  "objects": ["reader-scene", "reader-copy"]
}],
"objects": [
  {"id":"reader-scene","type":"image","asset":"library-reader",
   "box":[640,120,560,420],"fit":"cover","opacity":0.28},
  {"id":"reader-copy","type":"text","box":[680,180,460,180],
   "text":"Actual approved explanation goes here.","font_size":30,"color":"203F3C"}
]
```

This is a field illustration, not a complete runnable record, recommended
composition or proof that fading makes text readable. Choose the actual subject,
position and treatment from the task; inspect their combined visible result.

## Commands and dependencies

Resolve `scripts/` from the extracted package; `job/production.json` is the
producer's actual record, not a bundled demo. Use the real interpreter available
in the host. Commands below document the loop; they do not authorize development
tests when the owner has paused them.

```text
python scripts/production.py next job/production.json
python scripts/production.py bind job/production.json library-reader /actual/returned.png --provenance "actual source/tool and usage rights" --tool-ref returned-id
python scripts/production.py ingest job/production.json library-reader --result job/image-result.json --provenance "actual source/tool and usage rights"
python scripts/production.py writer-input job/production.json --output deck
python scripts/production.py assemble job/production.json --output deck
python scripts/production.py inspect job/production.json --output deck
python scripts/production.py review-template job/production.json --output deck --capture page1=preview/slide-1.png
```

`writer-input` is the host-writer alternative to bundled `assemble`, not a second
assembly step. Use it in the actual writer's runtime:

```python
from production import writer_input

job = writer_input("job/production.json", "deck")
# Implement the host's documented writer using job["pages"] and job["design"].
# Image objects reference job["assets"][object["asset"]]["path"].
# Preserve object["native_id"] where supported for delivery reconciliation.
# Export to job["output"]["path"], then inspect/render the actual export.
```

The returned `stage: ready_for_assembly` means only that declared image paths
exist and match their bindings. It does not run a writer or imply delivery or
visual success. `pages` retain the selected output order, contributions, geometry
and copy; `assets` contains only referenced assets, with absolute paths. Optional
font/physical-size settings are retained when present. Keep host-specific rich
features in its source while encoding supported placement/copy checkpoints in
the record. Unsupported checks remain explicit. New images or changed placements
update that same record before preparing the writer input again.

Repeat `--capture` for every actual page. `review-template` prints JSON; save it
to the output's declared review path, view the real captures and review the
central intent as well as the eleven lenses. `design_intent` contains
`assessment` (`achieved`, `unmet` or `unverified`), visible `evidence` and
`missed_material_opportunities` (a list, including important unplanned ones).
Only achieved intent with no remaining material omissions can complete managed
checks. Fill lenses with visible evidence or justified non-applicability;
`partial` also needs `remaining_cost` explaining the residual audience impact.
Record material gaps under `unresolved` rather than hiding them in that cost.
Record inspection limits and set `status` to `completed`. It starts unreviewed.
Report self-review accurately. `next` reads it; an applicable absent contribution
or unresolved issue remains unfinished. A partial assessment can be acceptable
only when its remaining cost does not defeat the central intent. No aggregate
score, image quota or requirement that all eleven lenses be strong is implied.
rc.6 review files need this explicit intent review before reuse; never fabricate
a new judgment or modify frozen benchmark evidence to satisfy a changed schema.

For `next`, exit code 2 means work remains: read the returned stage and continue
the same task. Exit 0 means its managed checks are complete, including declared
limits; exit 1 means a command/input failure. Other commands report success of
their particular operation, not overall TYY achievement.

Coordinator and HTML writer need Python 3.10+ standard library. PPTX assembly
additionally needs `python-pptx` 1.x and its normal dependencies; optional
requirements are in `scripts/requirements-production.txt`. Use an existing host
writer if suitable. Image result ingestion uses only the Python standard library;
the optional JSON retainer requires a file-capable Node runtime. Neither calls an
image service. Dependency setup follows existing authorization; the helpers
do not download/install anything or hold credentials. Rendering uses the host's
real renderer, or the separately documented browser helper for HTML. No desktop
PowerPoint, Codex path, private SDK, agent framework or model provider is required
by these Python writers.

For changed work, update the same record. `assemble --replace` preserves previous
artifact bytes before replacing; binding a different asset preserves its prior
version. Rerun inspection and actual review after changes. Do not amend past
benchmark outputs or disguise evaluator repairs as producer first-pass work.

## What the checks establish

The receipt binds the record and artifact hashes. PPTX inspection compares native
object IDs, text content, embedded image bytes, picture dimensions and table/chart
presence. HTML inspection compares IDs, text content and embedded image bytes.
These structural facts must remain distinct from receiver acceptance, visible
integration in the delivered canvas and the part's actual TYY contribution.
They do not establish good subject selection, complete diagram correctness,
actual editing behaviour, absence of visual clipping, or TYY quality. Other
formats carry explicit structural-inspection limits. Use the host's appropriate
checks for operations these helpers cannot inspect.

Visual review binds declared judgments to actual artifact/capture hashes. It is
an attestation, not proof that a model really looked or understood. Good fields
cannot rescue a generic design; reconsider missed opportunities in the visible
result. A new image displayed outside the artifact earns no integration credit.

The managed path can report ready only after its mechanical and declared visual
steps. A host writer using another source format should preserve object IDs where
supported or supply equivalent real evidence with explicit inspection limits.
Do not rewrite a rich design merely to fit this helper's object vocabulary.
No script can force every LLM to invoke it, grant a missing image tool, install
skills universally, or guarantee a high-quality first pass. Use supported skill
activation/file access in the actual host. A TXT attachment carries guidance;
the portable execution ZIP supplies helper files to code-capable environments.

**Candidate status:** rc.14 changes guidance, not helper code. The rc.13 checked
host-writer input remains runtime-unvalidated. The owner's later coached ChatGPT
rebuild demonstrated real artwork/PPTX integration through a direct writer;
it did not exercise these helpers or establish autonomous first-pass reliability.
No rc.14 output test has run. Further development tests require owner approval.
