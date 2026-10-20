# Install or use Le_SensVisual

## Native skill installation

The main ZIP contains one `le-sensvisual/` folder with SKILL.md, all specialist
instructions/styles, helpers, required small runtime data and four visual
previews. Keep its subfolders together. Modules are supporting resources, not
separately discoverable skills. DELIVERY.json declares the installed files.

After extracting or cloning the repository, choose the appropriate command:

```text
python <le-sensvisual-folder>/scripts/install.py --host codex
python <le-sensvisual-folder>/scripts/install.py --host claude-code
python <le-sensvisual-folder>/scripts/install.py --destination <host-skills-directory>
```

Codex uses CODEX_HOME/skills when set, otherwise ~/.codex/skills. Claude Code uses
~/.claude/skills. The installer copies only manifest-declared files and backs up
an existing Le_SensVisual outside skill discovery. Codex and Claude Code
also migrate a recognised legacy `visuasense` installation into that backup
area, avoiding duplicate discovery. For a custom host directory, inspect any
legacy sibling yourself. Historical helper filenames, cache and VISUASENSE_*
environment variables retain their compatible names. It enables no hooks, credentials,
extensions or agent registrations. Other host presets are convenience paths;
use the host's documented directory when uncertain. Reload discovery if needed.
Invoke `$le-sensvisual`, `/le-sensvisual`, or the host's supported skill mechanism with
the normal task. Use nested role files only with supported, authorized delegation.

## Optional software and full construction resources

All guidance stays local. The engine, original upstream source, complete browser
extensions and full Gardens production study are separate pinned companions.
Their logical paths, sizes and SHA-256 hashes are in third-party/RESOURCES.json.

```text
python <le-sensvisual-folder>/scripts/resources.py list
python <le-sensvisual-folder>/scripts/resources.py import <companion.zip>
python <le-sensvisual-folder>/scripts/resources.py resolve <logical-resource-path>
python <le-sensvisual-folder>/scripts/visuasense.py setup --engine
```

Import accepts a supplied companion ZIP or a preserved complete/offline ZIP or
folder whose resource bytes match the pins. It verifies a complete resource
group before promoting it to the external cache; it does not execute software.
`resolve` reports the actual verified file path. Source extraction and engine
commands use the same resolver. Engine setup alone can explicitly download the
current platform binary from the real URL/checksum in ENGINE.json. Other
companions are distributed alongside this release; no future publication URL is
assumed. Offline users can choose the full offline bundle, or pass explicit
`--resources <archive>` to the installer (repeatable).

The Windows cache is `~/.cache/visuasense`, independent of per-process sandbox
LOCALAPPDATA; macOS/Linux use their user cache directories. VISUASENSE_CACHE can
select another location outside the skill. Acquired resources are never copied
into later skill installs. Import/availability does not install browser extensions
or grant host tools. Read integrations/README.md before browser installation.

## Ordinary chat apps

Use the generated **chat-guidance ZIP** where archive reading is supported. It
contains ten entries: six text files including SKILL.md and all method,
specialist/style text, helper source, lookup/licences; plus four owner-selected
preview images. Logical paths map
to `RESOURCE: path` sections; follow its links or resource lookup. This is the
complete written guidance/source edition, not a native executable installation.
Machine font/catalogue/browser data and optional software stay in the native or
resource distributions. A helper source section is not an executable local file;
a file-capable host can use the native package or materialize needed helper files
through its supported operations. Never assume attachments share a filesystem.

For hosts that reject ZIP, the generated UTF-8 complete-guidance TXT contains
the same written library. Images are separate companions. Read the core and
relevant sections; do not load all 34 styles for one task. Large-file retrieval
and model attention vary. CHAT-GUIDE.txt is a reduced core adapter and remains
labelled as such. No format can guarantee every host reads or obeys every section.

Ask the host to read SKILL.md and report the version and relevant resources before
sending the normal task. This checks access, not compliance or permanent install.
Use its actual saved-skill/import feature when available. Never paste binary ZIP
bytes. A standalone repository URL does not perform context import.

Gemini documents up to ten files per ordinary ZIP. The ten-file edition meets
that count; an equivalent uncompressed `Gemini-stored.zip` is also supplied.
Earlier ZIP uploads failed to expose readable content, including a user report
for rc.18. Neither format is verified to fix ingestion; use direct UTF-8 TXT
and separately attached previews when needed. Explicit Import
Code supports one folder/repo up to 5,000 files/100 MB. Microsoft Copilot documents
TXT/MD, not ZIP. Native plugin/API importers have different caps; the native
package is not claimed to satisfy every plugin's file-count/per-file constraints.
GitHub hosting supplies versioned files, not universal tools or extraction.

## Execution prerequisites

Python helpers need Python 3.10+; PPTX authoring/extraction also needs python-pptx.
Browser helpers need Node 18+, Playwright and an existing Chromium browser.
Read references/tools.md for actual operation contracts. Keep project cwd and use
absolute helper paths. Image creation, asset transfer, authoring and viewing are
separate capabilities. Reading guidance supplies none of them. Publishing, paid
APIs, hooks and extensions remain explicit operations. Render trusted authored
files in an appropriate sandbox; local helpers are not an untrusted-code boundary.

## Evidence and official references

This revision has packaging/source checks and a local manifest-based install.
No new model/output or cross-host behaviour test was run for rc.23. The previous complete rc.15 archive remains recoverable. MIT for
original work and third-party notices are preserved. See RELEASE-STATUS.md.

References checked 19 October 2026:
- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Gemini file limits](https://support.google.com/gemini/answer/14903178?hl=en)
- [Gemini repository import](https://support.google.com/gemini/answer/16176929)
- [Microsoft Copilot upload](https://support.microsoft.com/en-gb/microsoft-365-copilot/file-upload-in-microsoft-copilot)
