# Presentations

Apply TYY to each slide's job and the shared identity. Honour image, HTML, PDF or editable presentation requests. Do not default to editability or force a route merely because its tools are available.

## Enter the requested route

**Finished slide images:** use [production](production.md)'s selected generation
or assembly method. Preserve each complete canvas's world, supporting expressions,
relationships and required copy; inspect and deliver the finished images.

**New visual PPTX:** execute the five stages below automatically. Read
[production](production.md) for artwork coordination and the host's actual image,
transfer, authoring and rendering instructions before their operations. Resolve
each tool's supported inputs and outputs; having a slide library establishes
only one part of the job. The user commissions the whole production process.

## One illustrated composition drives artwork and assembly

1. **Compose the whole experience.** Assign slide jobs and dimensions. Make the
   subject tangible through its setting, people, objects, actions and relationships.
   Give the main and useful supporting messages illustrated treatments with
   shared art direction, reading fields and clear hierarchy. Inspect a relevant
   accessible reference; when bundled, open the [Gardens preview](../examples/gardens/preview.jpg)
   and [construction account](../examples/gardens/ASSEMBLY.md) for distributed
   artwork and actual assembly. Resolve regional subjects/actions, benefits,
   dimensions/aspects, copy/icon fields, layers and placements in one working map.
   Use the writer's actual asset/layout structure or `production.json` with
   [execution](execution.md)'s helpers. This map supplies the actual artwork
   requests and writer inputs, rather than describing a deck after construction.
   Resolve missing visual opportunities before treating that map as complete.
2. **Produce its artwork.** Actually call the available image-generation tool
   for planned new scenes, illustrated objects and supporting treatments; source
   or reuse suitable existing artwork. Use each destination's planned size/aspect,
   focal subject/action, shared style, copy/icon space, crop and layering needs in
   its request. Follow [production](production.md)'s asset briefing, keeping
   editable copy/numbering out of asset images. Independent assets or a crop-safe
   sheet are valid. Select supported generation sizes and inspect the returned
   subjects, dimensions and consistency. With the coordinator, `next` supplies
   the pending requests; the AI still makes the actual tool calls.
3. **Obtain and assign the actual assets.** Retain the full result and use the
   host's supported file/export/transfer operation. Save returned bytes/data URLs
   with the [handoff implementation](execution.md#retain-and-save-the-actual-image-result)
   or an equivalent file operation. Associate each usable asset with its region.
   Its dependent placement remains unfinished until the writer receives the real
   asset. Pass actual file/asset references into the writer's consumed placements;
   the coordinator can do this with `bind` or `ingest`. A filename or separately
   displayed image does not establish embedding.
4. **Assemble and harmonise.** Use the host's documented writer with that actual
   asset/placement map, or bundled `assemble`. `writer_input(plan_file, output_id)`
   is available for a checked host-writer handoff. Load required artwork before
   dependent placement; preserve a missing asset as an unfinished operation.
   Compose editable wording and precise information with it. Preserve proportions;
   compose crops, scale, layers, local fading and calm reading fields together.
   Coordinate the whole set's colour, detail, typography and imagery. Restore
   missing subject actions, atmosphere and supporting illustrations before polish.
   Continue these operations within the original task.
5. **Export and inspect the actual deck.** Reopen/render the exported PPTX through
   a supported renderer and view every slide. Compare world, atmosphere, illustrated
   meaning, relationships and harmony with the audience need and reference,
   including useful opportunities omitted by the plan. Then check facts, reading
   size, crop, page count and editing. Refine and inspect again. Identify any
   unavailable operation precisely and disclose the remaining requirement.

Both authoring paths consume the illustrated plan and actual assets. A direct
writer's source must connect asset identities/paths to intended placements and
inspect their embedding in the export; merely claiming equivalence is insufficient.
The helper schema need only encode supported checkpoints; preserve richer host
features and disclose inspection limits. Name a real missing operation. No original
TYY deck, private Codex SDK or shared image-service filesystem is assumed.

### Assembly mechanics and editing

Convert design coordinates consistently: `x_output = x_design × output_width /
design_width`, likewise for y/height. A scene-backed card can layer ground,
illustration, local fading, symbol and editable copy; retain recognisable artwork
around the quiet text field. Set requested wording as editable text. Preserve
required data/diagram edits in suitable chart and relationship objects; handle
explicit symbol-editing requirements at this stage. Picture assets remain movable,
resizable and replaceable; painted details remain pixels. A flattened slide image
does not supply editable wording.

Scope explicit plain-material requests, narrow edits and accepted-artifact
conversion to those jobs. If generation, transfer, assembly, export or inspection
is blocked, use a supported alternative preserving the intended contribution and
requested deliverable; report a genuine remaining limit. Check receiver acceptance,
visible integration and TYY contribution separately. A format change needs agreement.

## HTML suite

Read [the adapted Frontend Slides workflow](../modules/frontend-slides/WORKFLOW.md), then only selected style material and needed implementation resources. It includes 12 presets, 34 detailed systems, preview recipes, animation patterns, fixed-stage CSS, PPTX extraction, PDF export and deployment helpers.

TYY directs the subject expression. Adapt a template or create a custom direction around the planned scenes, photographs, illustrated objects, diagrams and information. Templates supply supporting visual systems and mechanics.

- Infer speaking-versus-reading use when clear; ask when it materially changes density.
- Choose page count from content/use. Give pages complementary jobs.
- Show alternatives when direction is consequential and unsettled. A settled brief does not require three approvals.
- Conventional landscape HTML decks use a 1920×1080 stage scaled as one canvas. Other requested proportions are valid: configure scaffold dimensions. Do not force widescreen on a portrait request.
- `assets/deck-runtime.js` supplies actual navigation, touch, editing and download. Editing native text does not make baked artwork text editable.
- Integrate supporting visuals with body messages. A rich cover plus generic text-card pages does not fulfil the design goal.

## Delivery

`scripts/artifact.mjs` renders, inspects and prints PDF through an available Playwright browser. Print preserves browser text/vector content where supported; the upstream screenshot-based PDF helper is included when a raster snapshot is desired. Interactivity/animation does not remain interactive in PDF.

Package local assets or embed them. Hosted fonts remain external unless made local/embedded. Publish only with actual authorization. Inspect the delivered export's pages, type, crop and dimensions.
