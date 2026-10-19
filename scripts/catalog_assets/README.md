# Catalog presentation and discovery

The Pages catalog is generated from `agents/<application>/<use-case>/sample.json` by `scripts/generate_docs.py`. Edit these source files and assets; generated `docs/` files are replaced during publishing. Workflow definitions and existing guide URLs stay in their current folders.

## Describe a sample for discovery

Every maintained sample includes a `catalog` object:

```json
{
  "catalog": {
    "question": "Which supplier commitments should the buyer check first?",
    "domains": ["Procurement", "Supply chain"],
    "modules": ["Purchasing"],
    "useCases": ["Supplier follow-up", "Exception triage"],
    "keywords": ["vendor", "purchase order", "PO"],
    "technicalFeatures": [],
    "actionMode": "Read-only"
  }
}
```

- **Question:** a specific business question supported by the agent's documented prompts and data. It heads the card, followed by the description from `summary`. Avoid claims about current data, prediction, automated changes or coverage that the sample cannot support.
- **Domain:** the business function, such as Finance or Human resources.
- **Module:** the application area, such as Receivables or Learning management. Use shared terms where modules overlap across products.
- **Functional use case:** the job to be done, independent of application and implementation. For example, Capacity planning connects staffing, learning and campus samples.
- **Keywords:** short synonyms, acronyms and likely visitor search terms.
- **Technical features:** normally leave empty. SQL, REST, PL/SQL, database tools, document/CSV input, parsing, routing, date/time and text composition are derived from the saved graph. Memory is derived from the declared memory configuration. Add an editorial feature only when graph structure needs interpretation; the executive sample explicitly declares Agent subagents, and the EBS renewal sample declares Vector search and Email notifications. Never tag a planned MCP integration as an implemented feature.
- **Action mode:** an explicit description of current behavior. Use Read-only for evidence-only flows and Reviewed write actions for workflows such as EBS renewal that stage and submit records after review. Review this field when adding tools that change records or infrastructure; a compelling card question does not establish action capability.

`scripts/catalog_taxonomy.json` is the controlled vocabulary for domains, modules, functional use cases and explicit technical features. Reuse existing labels; add a label there deliberately when a new capability requires it. Generation rejects unknown labels and duplicate sample slugs. Legacy manifests without `catalog` remain loadable using their existing category/use-case fields.

## Interaction

- Text search covers the card question, title, description, capabilities, taxonomy labels, memory description and keywords.
- Selections are **OR within a facet**, **AND across facets**. Space-separated search terms must all match.
- Counts on each option reflect the other selected facets and the search text. Zero-count unselected options are disabled; selected options can always be removed.
- Query parameters are `q`, repeated `application`, `domain`, `module`, `usecase`, `feature`, and `sort`. Copy link shares the current view. Example: `?usecase=Capacity+planning&domain=Human+resources`.
- Quick-start links begin a fresh task search across applications. Sort options change ordering without removing filters.
- Agent links carry the current filter state so Back to catalog restores it. The guide sidebar also links each taxonomy label back to a filtered catalog.
- The complete catalog and all guide links are server-rendered. If JavaScript is unavailable, the cards remain usable; search and filters are hidden. No third-party search service, font, analytics script or runtime dependency is required.
- On smaller screens, Filters opens a collapsible panel. Escape closes it. Controls have labels, visible keyboard focus, a results announcement, and skip links.

## Generate

From the repository root:

```bash
python scripts/generate_docs.py \
  --repository-url https://github.com/kgvarun/agent-factory-samples/tree/main \
  --release-base-url https://github.com/kgvarun/agent-factory-samples/releases/download/latest
```

The existing Pages workflow regenerates and publishes the site on push to `main`. The release workflow continues to package each original workflow into its encrypted PAF archive.

## Purpose-first names

Use the business or operational purpose first and append the application: `Invoice Review and Actions — Fusion ERP`. `catalog.displayName` optionally controls catalog display and falls back to `title`; the guide also records the actual PAF workflow name. Keep the manifest title and version aligned with its official export.
