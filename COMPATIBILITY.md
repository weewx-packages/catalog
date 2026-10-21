# Check upcoming WeeWX changes

The compatibility workflow runs daily at 04:23 UTC, on catalog pushes and pull
requests, and through **Run workflow** in GitHub Actions. It tests the latest
stable, non-yanked release of every catalog package against the current commits
of `weewx/weewx` branches `master` and `development`, on Python 3.10 and 3.14.
These checks warn about changes already published in those branches. They cannot
predict a change that WeeWX has not pushed yet.

Each case downloads the catalog archive, checks its SHA-256, installs it into a
disposable station and imports its installed modules. The package's pytest suite
runs against the extracted release files. Tests come from a source revision
resolved once per run, normally the release tag. Extension source changes that
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
and executes only catalog code. No additional token or organization secret is
needed.

GitHub can delay scheduled runs and disables public-repository schedules after
60 days without repository activity. Check the workflow's **Actions** page if
runs stop. [GitHub's schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
describes these limits.

## Add a package check

Add an entry keyed by the catalog package ID to `ci/packages.json`. Set
`repository` to the GitHub repository containing its pytest suite, `ref` to a
source ref such as `v{version}`, `imports` to the installed Python modules to
check, and `allowed_skips` to an empty list unless a specific optional feature
is unavailable. The source ref must contain a `tests/` directory. Tests must run
with WeeWX, pytest and PHP as their dependencies. Add any extra dependencies to
the workflow before adding a suite that needs them.

Every catalog package needs a check. CI rejects missing entries so new packages
cannot silently escape testing. Archive URLs can point to any supported host;
the test source is configured separately from the download.

Run `just test-ci` to test the automation locally. It needs Python 3.10 or later,
pytest and packaging. Full compatibility runs require WeeWX and PHP and use
temporary station directories.
