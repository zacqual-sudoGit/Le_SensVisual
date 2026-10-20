# Tools, setup and capability limits

Use the host's supported tools when they already satisfy the task. This package adds optional local helpers; a TXT upload does not create runtime access. In the portable attachment, a relative Markdown reference resolves to its matching `RESOURCE: path` section in that attachment. Read that section directly; do not assume a missing local skill directory means the guidance is unavailable. Actual images and executables need the accompanying resources or host tools. For an extracted/installed package, resolve commands relative to its actual folder. Keep cwd at the user's project for engine context/source operations.

Select operations through [production](production.md)'s method choice. A finished
generated page needs retention, delivery and viewing. Assembly also needs actual
asset transfer and placement. In specialist instructions, a "native image tool"
means the host-provided generator/editor; source artwork through its supported
returned files, attachments or asset IDs.

## Establish capabilities in this task

Read the applicable host image/transfer, authoring and rendering instructions
before their operations. New visual PPTX work follows [presentations](presentations.md)'s
complete production sequence. An installed coding-agent skill may have automatic discovery and
local references; an ordinary chat may have only an uploaded text or archive.
Do not assume equivalent access or execution from an internal Codex example.
Resolve embedded TXT references by their RESOURCE headings. If an archive cannot
be opened, the self-contained chat guide carries the essential workflow.

Establish only the operations the selected method needs: generation/sourcing,
transfer, assembly where required, and viewing the result. Use actual tool
contracts and returns, rather than infer capability from code execution, a menu
item or a subscription. Retain the complete
return and use the concrete [image-result handoff](execution.md#retain-and-save-the-actual-image-result).
It covers accessible files, data URLs/base64 and opaque references, with a
conditional Codex bridge and portable Python operations. A missing wrapper output
does not establish that generation failed.
Use supported transfer mechanisms rather than private endpoints. Select an accessible
method that preserves the contribution and requested output; report a genuine
remaining operation limit. A different available writer is valid, but convenience
does not justify dropping the intended visual world.

Capability discovery establishes feasibility; assign tools to the resolved visual
experience and required operations. Our Python coordinator cannot invoke
host-private image tools. The host AI owns needed calls and, for assembly, their
asset handoff. New visual PPTX carries regional
requests, real assets and placements in the writer's consumed structure or our
checked production record. The required coordination does not depend on a JSON
format. Produce, obtain, place and inspect the actual artwork. Follow any
required writer/runtime rather
than selecting a library solely because it imports. Establish its supported
renderer before relying on desktop automation or declaring viewing unavailable.

Use the receiver's stated input types: uploads, asset IDs, files, URLs or inline
data only as supported. Neither raw code execution nor its absence establishes
those inputs. Promise DOM injection, binary embedding or live compilation only
when the actual interface supports the operation. Public URLs are not a universal
requirement; a declared self-contained HTML output still needs real image bytes.

If a call or input fails, distinguish a wrong invocation or execution environment
from an unavailable capability. Locate that failure before trying again. Repeat only when correcting an actual input or a changed condition makes
the operation plausible; rewording an unsupported promise is not a repair.
Choose another supported method preserving the visual benefit and requested
format/operations. Do not automatically replace PPTX with HTML or flatten text
that must remain editable. A materially different deliverable needs agreement;
otherwise state the specific unmet requirement without claiming completion.

## Conditional Codex image-result bridge

This example is only for a host exposing these actual tools and file access.
Other apps use their own tool names, memory and export mechanisms. Follow the
image tool's instructions; define `artPrompt`, `assetId` (its regional ID),
`helperUrl` (an actual file URL) and `responseFile` (an absolute job path) from
the current task.

```javascript
// In the orchestration context that invokes the image tool:
const result = await tools.image_gen__imagegen({prompt: artPrompt});
store(assetId, result);
generatedImage(result);

// Forward the full value as a JS tool argument to the file-capable runtime.
// This is programmatic transport; base64 never needs to be printed or retyped.
const code = `var imageTransfer = await import(${JSON.stringify(helperUrl)});
nodeRepl.write(await imageTransfer.retainImageResult(
  ${JSON.stringify(load(assetId))}, ${JSON.stringify(responseFile)}));`;
const saved = await tools.mcp__node_repl__js({code, title: "Retain generated artwork"});
for (const item of saved.content ?? []) if (item.type === "text") text(item.text);
```

Keep the stored result for recovery. Invoke the saving/binding operation on the
returned JSON path, then continue assembly and inspect the exported file. A
documented same-session generated file can instead use the existing-file route;
select the actual asset for this contribution, not an older similarly named file.
This small bridge only writes the result file. Run presentation-library authoring
through the host's documented script/runtime route; the bridge does not require
loading that library inside the JavaScript REPL.


## Complete product and resource loading

The main installation retains core/references, every specialist instruction and
style, helpers, small runtime data and rendered previews. Large software/source/
construction resources use the pinned manifest and separate cache; see
[installation](../INSTALL.md). Read only the active route. The generated chat
edition maps logical paths to RESOURCE sections and includes every specialist
instruction. CHAT-GUIDE.txt remains a reduced core adapter, not the full library.

## Command map

```text
python scripts/visuasense.py capabilities
python scripts/resources.py list
python scripts/resources.py import <companion.zip>
python scripts/resources.py resolve <logical-resource-path>
python scripts/visuasense.py context-read <path> --start 0 --chars 8000
python scripts/visuasense.py setup --engine
python scripts/visuasense.py detect <HTML/source/directory/URL>
python scripts/visuasense.py engine <verb> <arguments...>
python scripts/visuasense.py source impeccable <destination>
python scripts/visuasense.py source frontend-slides <destination>
python scripts/extract_pptx.py <input.pptx> <output-directory>
python scripts/production.py next <production.json>
python scripts/production.py bind <production.json> <asset-id> <actual-file> --provenance "actual origin"
python scripts/production.py ingest <production.json> <asset-id> --result <actual-result.json> --provenance "actual origin"
python scripts/production.py save-image --result <actual-result.json> --to <new-image-path>
python scripts/production.py assemble <production.json> --output <output-id>
python scripts/production.py inspect <production.json> --output <output-id>
node scripts/artifact.mjs scaffold deck|editorial|interface <output.html>
node scripts/artifact.mjs render <input.html> <output.png> --full-page
node scripts/artifact.mjs inspect <input.html> [report.json]
node scripts/artifact.mjs pdf <input.html> <output.pdf>
python scripts/install.py --host codex
```

Specify `--width`, `--height` and `--slide` for relevant render jobs. Scaffold can set stage dimensions and title; `--editable` explicitly adds browser text editing. Local saved edits are scoped to the base text revision. The supplied CSS/runtime are mechanics to adapt, not a final subject design. Inspect images using an actual vision tool; console checks alone cannot judge the result.

## Dependencies

| Operation | Required capability |
|---|---|
| Read/apply guidance | LLM access to the required files/text |
| Image creation/editing | A host image tool or separately authorized image API |
| Native HTML/source authoring | File/code capability; browser to view |
| Render/inspect/PDF helper | Node 18+ and Playwright with a Chromium browser |
| PPTX extraction | Python 3.10+ and python-pptx |
| Image-result saving/binding, production coordinator / fixed-canvas HTML writer | Python 3.10+ standard library; actual payloads/files. Optional JS result retainer uses Node file access. See execution.md; new handoff untested. |
| Native PPTX writer | Python 3.10+, python-pptx 1.x and dependencies; scripts/requirements-production.txt. New implementation, untested. A capable host writer is also valid. |
| Engine operations | Python launcher plus verified platform engine; individual browser/live verbs need their stated runtime |
| Browser live variants | Local project/dev server or supported static HTML, browser injection and an agent servicing events |
| Native app work | Actual iOS/Android build/render tooling |
| Build engine/extension from optional source companion | Appropriate Rust/wasm and upstream build dependencies |
| Publish presentation | Explicit publishing authorization and configured hosting account |

Do not silently download a browser/runtime, start paid generation or enable hooks. Use the authorized setup path and keep unresolved dependencies explicit. Explicit engine setup downloads the public pinned binary and verifies it in the external resource cache; it does not require an image API key. `third-party/ENGINE.json` records supported macOS/Linux/Windows assets and checksums. The recorded source snapshot and released binary share a version but are not claimed byte-identical builds of one commit.

When packages live outside Node's ordinary search path, set `VISUASENSE_NODE_MODULES` to that available package location. Set `VISUASENSE_BROWSER` to an existing Chromium executable when needed. These are runtime locations, not a request for secret values.

## Engine capabilities and authority

Use `engine <verb> --help` to inspect the exact executable contract before complex mutations. Available families include context/signals; palette; surface-brief; concept-seed/catalogue; comp-spec/comp-diff/font-match/build-phase; component-review; critique-storage; live/live-generate/live-poll/live-status/live-resume/live-accept/live-complete; hook management; doctor/pin; image generation and prompt embedding. Their files/state remain the engine's normal project records.

`detect` returns findings once with technical/style indexes in a bounded packet. Use `--offset`/`--limit` for more findings and explicit `detect --raw` for complete upstream diagnostics. `engine detect` uses the same interpreted route unless `engine --raw detect` is explicitly chosen. It is not a TYY quality scorer. Browser overlays/hooks also use the engine's own reporting: interpret aesthetic flags through TYY rather than treating them as design bans.

The integrated `engine context` returns discovered paths, bounded product/design/
surface-brief excerpts and token-key summaries. The 24,000-character serialized
budget labels partial documents and retains source path/SHA-256. Read relevant
remaining text with `context-read <path> --start N --chars N`; select token values
with `--pointer /path/to/key`. Platform references remain addressable. Missing
context does not impose an interview or delegation. `engine palette` returns the actual optional colour
seed with TYY interpretation. Concept exploration remains an explicit optional
interactive protocol. `engine --raw <verb>` exposes original output for diagnosis;
its prose does not outrank the parent skill. Automatic update checks and roll
telemetry are disabled in the launcher so stock updates cannot erase integration.

Source/install/update tooling is included, but the launcher routes Le_SensVisual installation through our installer to avoid replacing the integrated package with stock Impeccable. Host hooks and browser extensions are opt-in integrations; a file installation does not claim to enable them. The optional upstream-source companion preserves every upstream implementation, including provider/build/extension code; import and extract it when developing/building that integration. They are not additional prompts to load.

The file installer supports folder presets or `--destination`; a preset is not proof of current host discovery. Consult INSTALL.md and the host’s documentation. Consumer chat apps differ: attach the portable TXT/Markdown or use their supported saved-instruction/skill import. No universal permanent-install API is claimed.

The complete package includes the coordinator/writers and specialist library.
Scripts do not create image-tool access, force invocation, certify understanding
or bypass host limits. See [release status](../RELEASE-STATUS.md) for actual verification scope.

## Delivery honesty

State whether a function is packaged, available after setup, actually exercised or unsupported in this host. Never report successful visual review without seeing a render, original image layers recovered from PNG, editable PPTX produced by an HTML exporter, or independent review from a shared-context self-check. Public release licence/credit decisions are separate from runtime capability.

## Specialist compatibility

Examples in imported references use `impeccable` as shorthand for the verified
parent launcher `python scripts/visuasense.py engine`. Resolve paths from the
package root. These are opt-in specialist operations, not commands to run for
every visual. Set VISUASENSE_PROVIDER when host inference is insufficient.

The raw engine retains upstream aesthetic warnings and strict comp/plate gates,
including assumptions about raster vs vector media. They are not TYY law. Choose
the parent coordinated production/authoring/review route for a valid design outside those
assumptions rather than removing good illustrations to satisfy an inapplicable
gate. Do not label unrun gates passed. Browser-extension style flags likewise
require contextual judgment. Technical checks and relevant component/live
operations remain available; no engine binary was rewritten in this package.

The opt-in Chromium and Firefox companions retain their complete logical integrations/ paths. Import the chosen companion and use resources.py resolve on its manifest to obtain its real cache path.
They are local developer builds, not signed store packages. Read their permissions
and installation notes. The preserved source supports rebuilding them. Neither
extension is installed into the user's browser by the skill installer.
