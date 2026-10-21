# Add or update a package

Publish a versioned archive containing one top-level directory with `install.py`
and the package files. Uploaded GitHub release assets work, as do static HTTPS
downloads on another server. The package can remain in its author's repository.

## Add the metadata

Add a package entry to [repository.json](repository.json), using an existing
entry as a template. Choose a stable lowercase package ID and copy
`installer_name` from the installer's `name`. Each package needs a description,
one or more types, and at least one release. Keywords make hardware models and
features searchable.

Each release supplies its exact version, Python and WeeWX requirements, archive
format, download URL, and SHA-256 digest. Use the publisher's documented version
requirements. If compatibility has an unverified upper boundary, restrict the
range rather than claiming support for future major releases.

Compute the digest from the exact bytes users will download:

```shell
curl --fail --location --output package.zip VERSIONED_ARCHIVE_URL
sha256sum package.zip
```

Archive URLs must identify a fixed version. A URL containing `latest`, a moving
branch, or a replaceable artifact cannot keep an existing release reproducible.
Publish a new version when bytes change, and keep older compatible releases
listed. To withdraw a release from selection, set its `yanked` field to `true`.

## Validate the index

Using a WeeWX build with repository support:

```shell
weectl extension repo validate repository.json
```

Or run `just fast` when `weectl` is on PATH. Validation checks the whole index,
including identifiers, duplicate versions, requirements, and URL rules. The
schema alone checks structure; it cannot check archive bytes or whether a
publisher's compatibility claims are correct.

Before submitting, download and hash each new archive, check that its installer
name and version match the metadata, and test installation on a disposable
station. A successful install does not verify real hardware behavior.

Submit the metadata as a pull request. Describe which package or version you
added and which installation test you ran.

New packages also need a [compatibility check](COMPATIBILITY.md#add-a-package-check).

## Keep the package table in sync

The README package table is generated from `repository.json`, including manually
maintained packages. After editing the index, run:

```shell
python3 ci/upstreams.py readme
just fast
```

Validation rejects a stale table. The upstream skin publishing workflow updates
the index, test profile and README in one commit. See
[mirrored skin packaging](COMPATIBILITY.md#mirrored-skins-and-release-packaging)
for its release selection and tests.
