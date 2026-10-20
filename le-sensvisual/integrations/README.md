# Optional integrations

The optional `extension-chromium` and `extension-firefox` companions contain
complete detector WASM, loader, snapshot/overlay, panels and manifests, assembled
from the pinned Impeccable implementation. Import the chosen companion with
`python scripts/resources.py import <companion.zip>`, then resolve its manifest
with `python scripts/resources.py resolve <logical-manifest-path>`.
Chrome/Chromium and Firefox packages remain opt-in; no extension was installed.
Installation policies/store signing differ by browser. Firefox's local manifest
is a prepared build, not a claim of signed permanent installation.
Both request access to all URLs plus scripting/storage/navigation permissions
for inspection. These permissions apply only if the user installs the extension;
the skill file installer does not enable them. Chromium uses an offscreen
document; the Firefox source has a DOM-backed background-page fallback. Browser
loading and behavior have not been revalidated for this candidate.

All 59 rule definitions remain included. Findings about styles are contextual
review prompts, not universal bans or TYY achievement scores. Interpret them
against the actual subject/design. Technical findings also need verification.

Full Rust, host-provider/plugin/build, native-platform and remaining integration
source is preserved in the `upstream-source` companion at logical path
`third-party/impeccable-source.zip`. Import it, then extract with the tool launcher
when building a custom integration. Do not run upstream installers over the
integrated Le_SensVisual folder. Native platform/UI dependencies still apply.

Credits: Impeccable by Paul Bakaus, Apache-2.0; Le_SensVisual integration by TH_Ng.
