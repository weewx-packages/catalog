# Check upcoming WeeWX changes

The compatibility workflow runs one group each weekday at 04:23 UTC, following
the assignments in `ci/mirrors.json`. Each project runs once a week. Catalog
pushes, pull requests and **Run workflow** check every group. It tests the latest
stable, non-yanked release of every catalog package against the current commits
of WeeWX branches `master` and `development`, on Python 3.10 and 3.14.
These checks warn about changes already published in those branches. They cannot
predict a change that WeeWX has not pushed yet.

## WeeWX mirror

The organization keeps a fork at [weewx-packages/weewx](https://github.com/weewx-packages/weewx).
Before tests on the catalog's `main` branch, a separate job copies all upstream
branches and tags with their history from `weewx/weewx`. Tests then read pinned
commits from this fork. A failed sync prevents the tests from starting. Pull
requests use the most recently synchronized copy and receive no push key.

The job uses the catalog secret `WEEWX_MIRROR_SSH_KEY`, a deploy key with write
access to the fork alone. Extension installers and tests never receive this
key. The fork's own Actions are disabled; automation lives in this catalog.
Deploy keys must remain enabled in the organization's **Member privileges**
settings for the mirror key to work.

Updates are atomic and allow fast-forward branch updates and new tags. Divergent
history or a changed existing tag fails the sync for investigation. Branches and
tags deleted upstream remain in the fork. Keep local development in separate
repositories so mirror branches can follow upstream unchanged. Git history is
copied; GitHub issues, release assets and wikis are separate from this sync.

## Package checks

Each case downloads the catalog archive, checks its SHA-256, installs it into a
disposable station and imports its installed modules. The package's pytest suite
runs against the extracted release files. Tests come from a source revision
resolved once per run, normally the release tag, or a project suite in this
catalog. Separate jobs each get their own station and Python environment.
Large plans use child matrices of at most 200 jobs; the full pinned plan remains
an artifact used by tests and reporting. Extension source changes that
have not been released cannot hide a broken release archive.

Python and WeeWX requirement mismatches fail the check. Unexpected skipped
tests and suites with no executed tests also fail. Explicitly allowed skips are
listed per package in [ci/packages.json](ci/packages.json). LiveData's PHP tests
use PHP on the runner. Physical hardware, web hosting and long-running station
operation remain outside these tests.

## Follow failures

The workflow maintains one issue per failing package in this catalog, labelled
`compatibility`. Its table identifies WeeWX commits, Python versions and failed
checks, with links to the complete logs and JUnit artifacts. Existing issues are
updated, and a recurrence reopens the same issue. A complete passing matrix
closes the issue with a link to the successful run.

Download, checksum and dependency setup errors make the workflow fail. They do
not create a package compatibility issue or close an existing one. Missing or
cancelled matrix jobs also prevent automatic closure. The workflow does not
attribute a failed test to WeeWX without investigation.

Issues are maintained only for runs on the catalog's `main` branch. Tests run
with read permissions; a separate reporting job has permission to write issues
and executes only catalog code. Issue reporting uses the normal GitHub token.

GitHub can delay scheduled runs and disables public-repository schedules after
60 days without repository activity. Check the workflow's **Actions** page if
runs stop. [GitHub's schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
describes these limits.

## Add a package check

Add an entry keyed by the catalog package ID to `ci/packages.json`. Set
`repository` to the GitHub repository containing its pytest suite, `ref` to a
source ref such as `v{version}`, `imports` to the installed Python modules to
check, and `allowed_skips` to an empty list unless a specific optional feature
is unavailable. For a project with only prereleases, set `allow_prereleases`
to true. Its catalog version stays a prerelease and installation requires
`weectl extension install <package> --pre`.

By default, the source revision supplies `tests/`. For a suite maintained in this
catalog, set `tests_path` to `ci/project_tests/<repository>`. Its `payload`,
`station` and `case` fixtures identify the checksum-verified archive, disposable
station and complete pinned case. Test behavior from the payload or installed
modules. Tests must not import runtime code from the source checkout.

Use `pip_packages` for additional Python dependencies and `system_packages` for
Debian package names. Direct WeeWX dependencies and apt command options are
rejected. An `install_prerequisites` list pins other extensions by repository
and full `sha`; `install_input` supplies explicit installer answers without
credentials. Prerequisite setup failures are infrastructure errors.

Before importing, project checks compare every Python file declared by the
installer with the released bytes, using the core's actual destination mapping.
This rejects an importable but altered installed runtime. The import subprocess
uses only the station's `bin` directory on `PYTHONPATH`.
For modules that cannot import on the runner's hardware, use `imports: []` and
import the real payload inside functional tests, replacing only the hardware
boundary. This does not count as physical device validation.

Non-extension projects, such as a WordPress plugin or standalone rendering tool,
use `ci/external.json`, keyed by ID, with `release` and `check_profile` fields.
Their profiles use `kind: external` and the same project-test fixtures. They
receive their own checks without a WeeWX installer or an installable catalog
entry. A blocked extension may use `kind: source` with `coverage: component`
for independent payload behavior. That profile skips installation; the failed
installation and missing prerequisites remain documented separately.

Every catalog package needs a check. `ci/project_coverage.py` also matches all
tracked sources to release, external or component profiles before planning.
CI rejects missing entries so projects cannot silently escape testing.
[Package provenance](ci/package-provenance.json) records exact source revisions,
archive and patch hashes, test files and declared limits. Archive URLs can point to any supported host;
the test source is configured separately from the download.

Run `just test-ci` to test the automation locally. It needs Python 3.10 or later,
pytest, packaging, Git and Bash. Full compatibility runs require WeeWX and PHP
and use temporary station directories.

## Mirrored skins and release packaging

[Upstream skins](.github/workflows/upstreams.yml) runs at 04:03 UTC on Mondays for
NeoWX Material, Wednesdays for Belchertown and Fridays for DivumWX. The weekday
assignments are in `ci/upstreams.json`, using cron weekday numbers. Manual runs
include all three skins. Branches and tags keep their upstream history;
divergent refs stop the sync. Actions in these forks are disabled. Each fork has
its own write deploy key, available only to the mirror job.

The workflow selects stable GitHub releases. NeoWX Material also uses stable
version tags, matching its upstream release process. Untagged branch changes are
mirrored but do not become catalog updates. Prereleases are excluded.

Belchertown's existing archive is copied byte for byte. The other skins are
packaged with `git archive` from the selected immutable commit. No installer or
runtime code is patched. Each candidate is installed and rendered against WeeWX
`master` and `development`, with both commits pinned for the run. NeoWX Material
and Belchertown use Python 3.10 and 3.14; DivumWX uses 3.14 because its upstream
requires Python 3.13.5 or later and WeeWX 5.5 or later.

DivumWX 1.7.0.post1 uses a separately versioned, cleaned archive. The recipe in
`ci/repack_divumwx.py` verifies every input file against the audited 1.7.0 tag,
retains freely licensed fonts with full notices and replaces AstroDot letters
with Unicode zodiac symbols. The original archive is withdrawn. The `blocked`
field prevents direct publication of future tags until their assets are reviewed.
Use restrictions and redistribution grants are evaluated separately.

The skin suite runs the original installer, verifies installer identity and
imports from the installed station, fills an isolated SQLite archive, and runs
the actual report generators. It rejects report errors, missing output files and
invalid generated JSON. DivumWX's schema additions run against an existing base
archive, as they do on a running station. Its installation prompts receive an
explicit fixture without API secrets. NeoWX Material's StandardReport skin is
selected explicitly, following its upstream installation instructions.

Forecast/API calls, MQTT, live astronomy services, optional cameras, timelapse
and browser interaction are outside these report checks. The test configuration
disables external forecast and update features. Physical stations are untouched.

Only a complete passing candidate matrix can publish. A separate job uploads
archives and provenance receipts to this catalog's GitHub releases under
`PACKAGE/vVERSION`. That job executes catalog code only. Existing release bytes
are never replaced. It appends the release to `repository.json`, pins its test
source in `ci/packages.json`, and regenerates the README package table from the
index. All three files are committed together. The weekly compatibility workflow
checks the published downloads, maintaining issues for regressions in catalog
releases. It also runs on catalog pushes and pull requests and can be started
manually.

Package descriptions, source repositories and compatibility requirements are
maintained in [ci/upstreams.json](ci/upstreams.json). Versions come from upstream
tags and must match the archive's installer; SHA-256 is computed from the exact
published bytes. Adding a skin requires a definition, a test profile and a
separate mirror deploy key. Failed candidate tests leave the published catalog
at its previous version; inspect the candidate workflow logs before retrying.

## Source backups and upstream activity

The [Extension mirrors workflow](.github/workflows/mirrors.yml) handles the
additional repositories from the [wiki review](WIKI-AUDIT.md). Assignments in
`ci/mirrors.json` spread each repository's weekly capture across Monday through
Friday at 03:43 UTC. Manual runs include every group. The three skin mirrors
retain their separate release workflow; independent continuations are never
overwritten by upstream synchronization.

Each synchronized repository has its own write deploy key. The keys are stored
in five weekday bundles to stay within the catalog's secret-count limit. Only
the trusted mirror job receives them. Ref updates preserve history, reject
divergence and retain branches and tags removed upstream. Mirroring copies Git
source; it does not automatically approve a new catalog package or release.

The snapshot job captures open GitHub issues and PRs, discussion replies, reviews,
inline review comments and available file patches. Full snapshots are committed
to the private [upstream-backup](https://github.com/weewx-packages/upstream-backup)
repository on `weekday-1` through `weekday-5`. Commit history retains earlier
versions when a thread changes or closes. External attachments, binaries absent
from GitHub's patch responses, pre-existing closed discussions, release assets
and wikis are outside this discussion capture.

Public artifacts contain activity summaries and fingerprints. One catalog issue
reports newly open, changed or no-longer-open upstream items. Changed license
notice files are highlighted for review; their contents are not interpreted as
an automatic ban on restricted-use software. Activity comments notify subscribers
when something changes. The private backup job's deploy key cannot write to any
extension repository, and no extension code runs in that job.

The reporting job records the latest public activity and source-check summaries
in `ci/upstream-state.json` and `ci/source-quality.json`. Each run updates only
its assigned groups. Discussion bodies and patches stay in the private archive.

Source checks use Python 3.14 with current WeeWX `master` and `development`
checkouts. They compile runtime Python, archive the exact fork commit and run
the original installer against an isolated station. Checks receive no mirror,
backup or issue-write credentials. Unsupported layouts are recorded as
`not-covered`, rather than passing without an installation test. Packages
already in the catalog use their separate release tests. Hardware operation,
API access and generated skin behavior require project-specific tests beyond
this source-installation baseline.

A separate reporting job maintains installation issues in this catalog. Missing
branch results cannot close an existing failure. Failures identify the tested
source and WeeWX commits; dependency or configuration failures need investigation
before being attributed to a WeeWX change.

Public GitLab upstreams use the same weekly discussion backup. Merge request
notes and available diffs are captured along with issues; the public index
distinguishes issue and merge request numbers. Anonymous GraphQL reads provide
notes when GitLab requires authentication for its REST notes endpoint.

A test profile may list extra Python dependencies in `pip_packages`. Requirements
are parsed before matrix creation. Direct WeeWX requirements are rejected, and
a pip constraint preserves the installed core version for transitive dependencies.

Source profiles may name `install_prerequisites` as repository/SHA pairs. Those
extensions are installed first in the same disposable station, and their exact
refs appear in the results. Prerequisite failures remain infrastructure errors.
An `install_skip_reason` records an unavailable hardware platform after syntax
checks; it never counts as a successful installation. PiSenseHat has only component coverage: its installer imports platform-specific
modules and the required SHTC3 native ABI has no matching library or buildable
source in the inspected archives. Its LPS22 register and LOOP conversion checks
do not imply a working complete device installation.

A non-catalog source profile can set `source_archive: true` and a branch in
`ref`. The planner resolves its commit and archive checksum together before
starting jobs. This follows current source independently of a stable catalog
release. Use `coverage: source` for full source checks and `coverage: component`
for a limited payload check; these labels appear in failure reports.
