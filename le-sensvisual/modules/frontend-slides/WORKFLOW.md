# HTML presentations

Specialist production module under the parent TYY authority. It supplies visual
exploration, HTML decks, scoped deck changes, PPTX extraction, animation, editing,
export and optional publishing. It does not generate editable PPTX by itself.

## Resolve and compose

Use the user's audience, actual content, takeaway, context and requested format.
Infer familiar decisions when clear; clarify only material missing information.
Choose a deck only when it fits the job. A responsive reading page can be a better
choice for long teaching/reference content. Editability is conditional.

Resolve each slide's communication job, subject-specific focal carrier,
supporting visual opportunities, reading field and shared identity. Let content
relationships vary the composition across the deck. Obtain/create the actual
artwork and meaningful objects rather than leaving them in an outline.

If the user needs help choosing an aesthetic, render concrete short previews.
Use the number of choices needed; a clear supplied direction needs no ceremony.
Start with STYLE_PRESETS.md (12 presets), or the compact bold-template-pack index
(34 systems). Load only a relevant preview card, then a chosen design.md. Recipes
are starting points to adapt to the subject, not limits on useful illustration.

## Construct

For fixed-stage slides, choose the requested dimensions; 1920×1080 is conventional
widescreen, not a universal requirement. Scale the composition uniformly for
viewing. Keep navigation outside the stage. A reading page uses natural flow.

The parent `scripts/artifact.mjs scaffold deck` supplies inline mechanics and the
complete `assets/deck-runtime.js`: keyboard, wheel, touch/pointer navigation,
controls and HTML download, with text editing/local persistence enabled explicitly by `--editable`. Its neutral shell
requires actual art direction. Consult html-template.md, viewport-base.css and
animation-patterns.md for additional patterns; don't combine incompatible stage
controllers. Include reduced-motion behavior and intentional print styles.

Use semantic HTML, actual assets, an intentional type scale, readable text at
viewing size and coherent colour roles. Follow the parent's
[coordinated production workflow](../../references/production.md): use available
image tools for the planned illustrations, suitable sources/tools for supporting
symbols, and HTML to assemble the returned artwork with readable information and
accurate relationships. Keep code/formulas/data real and provide copyable companions
when required. Asset paths must survive export.

Apply the parent's actual-host check before relying on file, image or browser
operations and read their applicable instructions. Artwork production, actual
asset acquisition and placement form one sequence within this task. Another
capable writer executes the same composition and its production dependencies.

## Modify or import

For scoped changes, retain the deck's useful identity and inspect neighbouring
slides and affected behaviors. A redesign may change the system as requested.
For PPTX input, prefer parent scripts/extract_pptx.py: text/runs, image blobs/crops,
groups, tables, charts, notes and geometry are extraction evidence. The original
scripts/extract-pptx.py is retained for simpler legacy use. Neither reconstructs
an arbitrary flattened image into original editable objects. Determine whether
the request is a fresh composition or fidelity-preserving conversion.

## Inspect and deliver

View all slides at the actual aspect and intended reading size, plus relevant
small-screen viewing. Check world/meaning/relationships/composition/harmony,
loaded artwork, hierarchy, clipping and content completeness. Exercise actual
navigation, editing and reduced-motion behavior where supplied. Technical checks
and screenshot similarity cannot certify audience understanding or TYY quality.

Deliver the actual HTML and required assets. Explain that text editing does not
make baked-in image text or every illustration editable. A downloaded HTML file
must retain external asset dependencies or embed them explicitly.

## Export and sharing

The parent cross-platform artifact helper renders PNG and browser-print PDF
using an existing Playwright/Chromium setup. Print can preserve browser text and
vector content; PDF is still static and is not editable PPTX. The retained Bash
scripts/export-pdf.sh captures raster slide pages, has its own runtime/download
requirements and widescreen assumptions; inspect before using another aspect.
Use the parent helper for selected dimensions and explicit dependencies.

The retained scripts/deploy.sh publishes to Vercel. Use only when the user asks
to publish and the hosting setup is available. Its npx fallback may download the Vercel CLI; it requires an existing login and an intentionally prepared public folder (or contained static assets); do not silently deploy or promise a price/availability. Inspect its
help and current hosting contract. Local delivery needs no deployment.

## Resources

- [12 presets](STYLE_PRESETS.md)
- [34-system catalogue](bold-template-pack/selection-index.json)
- [Preview/design recipes](bold-template-pack/templates/)
- [Stage CSS](viewport-base.css), [HTML patterns](html-template.md)
- [Alternative deck-stage web component](bold-template-pack/deck-stage.js): navigation, speaker-note events and print mechanics; use its own API instead of combining controllers
- [Animation patterns](animation-patterns.md)
- [Legacy PPTX helper](scripts/extract-pptx.py)
- [Optional deployment](scripts/deploy.sh), [raster PDF](scripts/export-pdf.sh)
