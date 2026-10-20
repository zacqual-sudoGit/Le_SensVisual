> Adapted for Le_SensVisual by TH_Ng from Impeccable. Apply the parent TYY design authority. Use this specialist procedure only for its stated task; contextual style suggestions do not override the resolved design.

# Operate mode depth (and Read notes)

Use for working interfaces: app UIs, admin dashboards, settings, tables and tools. Apply the parent TYY authority and [craft-floor.md](craft-floor.md). Reading/teaching surfaces use [mode-read.md](mode-read.md); useful typography and consistency advice here may transfer, while interface density and interaction recipes remain conditional.

## The product slop test

Familiarity is often a feature here. The test is whether a category-fluent user can trust the interface immediately or must pause at every subtly-off component.

Product UI's failure mode isn't flatness, it's strangeness without purpose: over-decorated buttons, mismatched form controls, gratuitous motion, display fonts where labels should be, invented affordances for standard tasks. The bar is earned familiarity. The tool should disappear into the task.

## Typography

- **One family is often right.** Product UIs don't need display/body pairing. A well-tuned sans carries headings, buttons, labels, body, data.
- **Stable readable scale.** Choose rem or fluid sizing for the actual hierarchy and viewports; preserve text zoom and prevent headings from overwhelming compact work areas.
- **Tighter scale ratio.** 1.125–1.2 between steps is typical. More type elements here than on brand surfaces; exaggerated contrast creates noise.
- **Line length still applies for prose** (65–75ch). Data and compact UI can run denser; tables at 120ch+ are fine.

## Color

Choose colour intensity from the product identity, subject world, tasks and readable hierarchy. Restrained and immersive treatments are valid; protect distinguishable controls and state meanings within either.

- State-rich semantic vocabulary: hover, focus, active, disabled, selected, loading, error, warning, success, info. Standardize these.
- Coordinate action/state colours with grouping, atmosphere and subject identity. Keep the primary action and important statuses distinguishable when accents also serve imagery or other content.
- A second neutral layer for sidebars, toolbars, and panels (slightly cooler or warmer than the content surface).

## Layout

- Adapt structure where needed: collapse sidebars, reflow columns and make tables usable. Coordinate typography with those changes rather than relying on font shrinkage alone.

## Components

Supply the actual states each interactive component needs: default, hover, focus, active, disabled, loading and error as applicable.

- Choose loading feedback suited to expected duration and layout stability; skeletons, progress indicators and concise status text serve different jobs.
- Empty states that teach the interface, not "nothing here."
- Consistent affordances across the surface. Same button shape. Same form-control vocabulary. Same icon style.
- Overlays escape their container. An absolutely positioned dropdown inside an `overflow: hidden` or `overflow: auto` ancestor gets clipped; reach for `<dialog>`, the popover API, `position: fixed`, or a portal.

## Motion

- 150–250 ms on most transitions. Users are in flow; don't make them wait for choreography.
- Motion can explain state, guide attention or sustain the intended experience. Keep repeated work efficient and provide reduced-motion alternatives.
- Keep essential tasks available promptly; use orchestrated entry only when it serves the experience without blocking access.

## Product constraints

- Decorative motion that doesn't convey state.
- Inconsistent component vocabulary across screens. If the "save" button looks different in two places, one is wrong.
- Display fonts in UI labels, buttons, data.
- Reinventing standard affordances for flavor (custom scrollbars, weird form controls, non-standard modals).
- Heavy color or full-saturation accents on inactive states.
- Modal as first thought. Modals are usually laziness. Exhaust inline / progressive alternatives first.

## Product permissions

Product can afford things brand surfaces can't.

- System fonts and familiar sans defaults.
- Standard navigation patterns: top bar + side nav, breadcrumbs, tabs, command palettes.
- Density. Tables with many rows, panels with many labels, dense information when users need it.
- Consistency over surprise. The same visual vocabulary screen to screen is a virtue; delight is saved for moments, not pages.
