# Assets, extraction and conditional reconstruction

Use actual files and supported operations. Preserve originals. A flattened image does not contain recoverable original text/shape layers.

## New material

Use [production](production.md)'s selected method. For assembly, generate or source the contributing illustrations, photographs and illustrated symbols, then bring their actual files/IDs into the composition through the shared [production map](production.md). For assembly, obtain clean artwork with needed copy areas; text-free artwork is an option, not a skill default. Request true transparent output where isolated assets must sit on the page ground. Inspect alpha on light/dark grounds: a painted checkerboard is not transparency.

Reuse assets when their actual subject/action fits. A crop cannot add an absent action. Verify source resolution, margins and final crop/scale. Environmental art can establish atmosphere while smaller subject objects support individual messages.

## Three extraction jobs

1. **PPTX → contents/assets:** `scripts/extract_pptx.py` exports text/runs, images, positions, tables, chart data and notes, traversing groups. These are reconstruction ingredients. Unsupported objects and incomplete chart properties remain reported; this is not a PPTX renderer/generator.
2. **Accepted image → region references:** authored boxes identify artwork and reading regions. The interface engine's `comp-spec`/`--inspect-map` produces crops/measurements. Automatic bands do not understand semantic parts. A crop retains only existing pixels.
3. **Code → design system:** interface `document`/`extract` identifies real tokens and repeated patterns, then records/refactors them. It does not recover picture layers.

## Preserve an accepted image when requested

Inventory its focal setting, supporting objects, text, relationships, reading fields and identity. Choose the least disruptive supported operation:

- Use original clean artwork/native source when available.
- For a small wording correction, use supported image editing or a clean text region with replacement copy. Inspect obsolete/duplicated lettering.
- For editable copy, combine clean artwork with native text. Retain useful art where possible; regenerate needed clean assets with the original as reference when necessary, disclosing changes.
- Reconstruct precise diagrams/charts natively when their content and geometry are known. Do not promise exact recovery of unknown data or arbitrary original layers.

The engine's strict accepted-composition workflow measures assets/layout/screenshot fidelity in capable coding hosts. Use it for an actual reference-fidelity job. It is not compulsory for fresh work, and its raster reproduction gates do not ban truthful native diagrams elsewhere.

Check identity, action, proportion, material, crop, alpha and relationships after assembly. Keep conversion subordinate to the user's requested operation.
