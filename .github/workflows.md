# .github/workflows

## ISSUE_TEMPLATE

Used as templates when creating new issues in the repo

## Workflows

### constraints.txt

Constraints.txt is a pip install file that constrains some python requirements outside of poetry.

### dependabot-auto-merge.yml

A workflow that runs on PRs that will automatically merge dependabot update PRs that pass testing

### release-please.yml

A workflow that manages releases for the repo. On merges to the main branch, it scans them for [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
and will then create or update a release pr with those changes. The [release-please](https://github.com/googleapis/release-please) docs have more info.

When that release pr is merged, it will build and upload to pypi.

### release.yml

A workflow that runs on the creation of releases to upload the package to pypi

### Required Secrets

* THIS_PAT - a personal access token that has access to create releases on this repo and edit the repo's settings. Used with release-please and repo-manager
* PYPI_TOKEN - a pypi token that can upload to pypi for this package. Used with release

## dependabot.yml

Configures dependabot updates and alerts for this repo

## release-drafter.yml

Configures how release notes are written by release-please
