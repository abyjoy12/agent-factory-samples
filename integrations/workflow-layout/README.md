# AI World workflow layout verification

The 2026-10-18 repair covers the 28 catalog workflows on `build.oracleagentfactory.com`. All 144 processing nodes now read from left to right, with 134 numbered native sticky notes above their stages. All 31 Agent nodes select `AIW26-PAF-HOL6004-BOO6096` (OpenAI Compatible). Their descriptions explain the workflow, its boundaries and at least two sample questions; use the expand control beside Agent Description to read the full text.

The defect came from saved layout data: 119 generic cards in 22 catalog workflows forced an outer width of 340 pixels while the Builder rendered narrower inner forms. This left blank strips and misplaced connection handles. Removing the forced dimensions lets the Builder measure each card naturally. Dependency columns and measured vertical spacing prevent overlaps, including parallel branches.

The native `.paf` format was valid. It is an encrypted Agent Factory workflow archive, with a ZIP containing metadata and workflow JSON after decryption. It is separate from Open Agent Spec. The initial audit found no forced card widths in the other 30 accessible workflows, so the evidence does not establish a problem across all agents.

## Expanded Build verification — 2026-10-18

The current pass covers all **49 catalog samples** and **52 Agent nodes** under **editor@oracleagentfactory.com**. All use `AIW26-PAF-HOL6004-BOO6096`. Chromium measured every workflow without overlaps, card-width mismatches or clipped sticky notes, and every Agent Description has at least two sample questions. Publication and memory settings were preserved; the twenty new Fusion review drafts have both memory switches off and remain unpublished.

The [current sanitized record](build-validation-2026-10-18.json) records the ownership, model, settings, layout and conversation smoke checks per sample. The initial pass included 49 primary requests, 20 Fusion limitations requests and three additional read-only requests covering the two JDE memory flows and the invoice/action flow. These checked response availability, without proving every tool invocation, cross-session learning or business conclusion.

The [Fusion follow-up](../fusion-apps/validation-2026-10-18.json) reran twenty primary questions after credential changes and verified all three invoice action outcomes through independent reads. Both changed workflows passed browser layout checks again, and the 49-sample ownership/model/settings audit passed. The new invoice fixture is canceled at zero amount. Final instance imports and bindings remain to be validated.

The original 28-workflow repair and its narrower checks below remain a historical record.

## Checks

The sanitized [verification record](verification.json) contains per-workflow counts and results:

- Chromium opened all 28 workflows and measured their rendered nodes: zero overlaps, card-width mismatches or vertically clipped sticky notes. Every connection advances to a column on the right.
- Live readback matched every original connection and all other processing-node settings, including custom instructions and tool bindings. Names, summaries, permissions, publication states and Agent Memory settings were preserved.
- The official encrypted export was decrypted in memory and its nodes and edges compared with the live workflow. Each of the 28 local workflows was then rebuilt into a native `.paf`, decrypted again and compared exactly at the JSON payload level.
- A fresh, read-only Campus Capacity Review chat completed with the new model. The remaining workflows were checked structurally and visually; their earlier demo-validation records remain historical and do not claim a new full runtime validation.

The encrypted archives used for verification and private audit responses remain outside this repository. The live repair preserved workflow publication states. Pushing these sources to `main` invokes the repository's normal archive release workflow.

## Future imports and regeneration

The checked-in `workflow.json` and `archive-metadata.json` files come from the final official export. Build archives with `scripts/build_release.py` using the repository's existing secret mechanism. Follow each sample's setup steps to rebind sources, upload required files and set Agent Memory after import.

Configure `AIW26-PAF-HOL6004-BOO6096` in every final AI World lab instance. Model definitions and credentials are excluded from the workflow archives. This repair updates the build instance and export sources; it does not deploy to unspecified final lab instances.

`python scripts/prepare_lab_workflows.py` reapplies the layout, model and description conventions to local sources. Its conservative default spacing accommodates expanded cards. For tighter parallel branches, pass `--measurements /path/to/browser-audit.json`; the file is a list of objects with `path` and `nodes`, where each node supplies `id`, `width` and `height`. Recheck rendered geometry after changing component forms or descriptions. Follow any live update with an official export to capture the server's current workflow lineage before rebuilding release archives.
