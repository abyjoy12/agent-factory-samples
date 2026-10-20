# Contributing

Contributors submit changes through pull requests from their own forks to
`kgvarun/agent-factory-samples:main`. This includes code, workflows, sample assets,
and documentation. Upstream write access is reserved for maintainers; `kgvarun`
is the current sole maintainer and repository administrator.

## Submit a change

1. Fork the repository into your GitHub account and clone your fork.
2. Create a topic branch in your fork, such as `feature/sample-name` or
   `fix/manifest-validation`.
3. Make a focused change and complete the validation below.
4. Push the topic branch to your fork and open a pull request targeting upstream
   `main`. Describe the problem, resulting behavior, validation, and known limits.
5. Address review comments and keep the branch up to date with upstream `main`.
   New changes dismiss earlier approvals and require another review.

Do not request upstream write access to submit a contribution. The maintainer
reviews and merges accepted pull requests.

## Validate locally

Use Python 3.10 or newer. Node.js 24 or newer is needed when running the
contribution-origin policy tests.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
git config core.hooksPath .githooks
python -m unittest discover -s tests -v
node --test tests/test_contribution_origin.cjs
python scripts/publication_guard.py
python scripts/generate_docs.py
python scripts/publication_guard.py --pages docs
PAF_ARCHIVE_PASSWORD='local-validation-only' python scripts/build_release.py
```

The sample passphrase above is only for disposable local validation archives.
Release automation uses a privately configured passphrase. Never commit generated
`.paf` files, credentials, tokens, cookies, customer data, or learned user memories.

Before committing, stage only the intended files and run:

```bash
python scripts/publication_guard.py --staged
```

Deployment URLs, hostnames, IP addresses, and deployment-domain email addresses
must stay out of every README and GitHub Pages output, including generated
HTML, JSON, assets, diagrams, and code blocks. Use role descriptions or reserved
example addresses. Keep runtime endpoints in operational configuration outside
publication inputs. Public references must use hosts already approved by
`scripts/publication_guard.py`; do not add deployment hosts or bypass the guard.

For agent samples, follow the [source and release contract](README.md#source-and-release-contract)
and [contribution checklist](README.md#validate-a-contribution). Document
prerequisites, source bindings, tool permissions, memory behavior, demo prompts,
validation evidence, and known limits. Preserve the intended workflow payload and
keep environment dependencies portable.

## Merge requirements

The upstream `main` ruleset requires:

- a pull request with one maintainer/code-owner approval;
- fresh approval after changes and resolution of review conversations;
- an up-to-date branch and passing `check` and `fork-origin` statuses;
- no force pushes or branch deletion by contributors.

`check` runs the tests, publication checks, documentation generation, and archive
round-trip validation without release secrets or publishing artifacts.
`fork-origin` verifies that the source branch belongs to a fork. Its trusted
workflow reads GitHub metadata and posts a status on the PR's head commit; it
does not check out or execute pull request code. GitHub may require maintainer
approval before running workflows for a first-time contributor.
Maintainers can manually rerun **Check contribution origin** with a pull request
number if its source or the author's permissions need to be checked again.

Repository administrators are exempt from these branch rules and may bypass
review and check requirements when merging. Administrator-authored pull requests
may also use upstream branches. This lets the sole maintainer merge their own
changes without another approver. Contributors must still use forks and follow
the review process.

Branch rules are configured in GitHub repository settings. `CODEOWNERS` and
workflow files support those rules; changing documentation alone does not change
GitHub enforcement.
