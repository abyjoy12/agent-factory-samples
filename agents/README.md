# Agent catalog

Samples are organized first by the business application they integrate with, then by use case:

```text
agents/
└── <application>/
    └── <use-case>/
```

Each use-case directory contains one reviewable Agent Builder workflow, its archive metadata, a complete `sample.json` documentation manifest, supporting assets, and demo material. Generated `.paf` archives are release assets and are not committed.

## Applications

- [JD Edwards EnterpriseOne](jd-edwards/)
- [PeopleSoft](peoplesoft/)
- [Oracle E-Business Suite](oracle-ebs/)
- [Cross-application](cross-application/)

Application and use-case slugs in `sample.json` must match their directory names. The agent `slug` remains independent and determines the stable release asset filename.

## Design blueprints

The [EBS staging blueprints](../integrations/ebs-staging-blueprints/README.md) cover WO reschedule and PO change draft creation. They live under integrations while native workflows and destination validation are pending. Follow their promotion guide before adding either to this runnable sample tree.

## Shared capability model

The [registry model](../architecture/registry-model.md) separates reusable agents from shared tools, skills and workflow tasks. The agreed target is independent canonical tool definitions referenced by agents. Existing sample folders and design-local contracts remain in their current form until a deliberate migration preserves catalog and release compatibility.
