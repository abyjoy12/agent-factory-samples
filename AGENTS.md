# Publication privacy

The user requires deployment URLs and hostnames to stay out of every README and
GitHub Pages output. This applies to prose, links, tables, diagrams, code blocks,
email addresses containing deployment domains, catalog manifests, and generated
HTML/JSON/assets. Use role descriptions or reserved example addresses. Keep actual
runtime endpoints in operational configuration outside publication inputs.

Public documentation, source, and download references are limited to the public
hosts approved in `scripts/publication_guard.py`. Do not add a deployment host to
that allowlist or bypass the guard to publish a change.

Before committing, run `python3 scripts/publication_guard.py --staged`. Before
publishing Pages, regenerate the site and run
`python3 scripts/publication_guard.py --pages docs`. The generator, repository
hooks, and GitHub Actions enforce these checks. Configure hooks in a new checkout
with `git config core.hooksPath .githooks`.

Preserve unrelated work in this shared checkout. Stage only the intended changes.
