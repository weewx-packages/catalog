# Add or update a package

Publish a versioned archive containing one top-level directory with `install.py`
and the package files. Uploaded GitHub release assets work, as do static HTTPS
downloads on another server. The package can remain in its author's repository.
Installer destinations must be under `bin/user` or `skins`, which the repository client manages. Additional
Python packages and schemas belong below `bin/user`; keep their import and
configuration paths consistent with that layout.

## Add the metadata

Add a package entry to [repository.json](repository.json), using an existing
entry as a template. Choose a stable lowercase package ID and copy
`installer_name` from the installer's `name`. Each package needs a description,
one or more types, and at least one release. Keywords make hardware models and
features searchable.

Each release supplies its exact version, Python and WeeWX requirements, archive
format, download URL, and SHA-256 digest. Use the publisher's documented version
requirements. Versions must be PEP 440 without local labels such as `+gSHA`.
Keep prereleases identifiable; use a separate `.post` version for catalog
packaging changes and record the source commit in provenance. If compatibility
has an unverified upper boundary, restrict the range rather than claiming support for future major releases.

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

Install the experimental [standalone repository client](https://github.com/weewx-packages/weewx-package-manager#install)
in a WeeWX Python environment. Stock WeeWX has no repository validation command.
With the client importable in that environment:

```shell
python -m user.packages repo validate repository.json
```

Or run `just fast` in the same environment. Validation checks the whole index,
including identifiers, duplicate versions, requirements, and URL rules. The
schema alone checks structure; it cannot check archive bytes or whether a
publisher's compatibility claims are correct.

Before submitting, download and hash each new archive, check that its installer
name and version match the metadata, and test installation on a disposable
station through `python -m user.packages install PACKAGE_ID --repo ALIAS`. First
register its index with `python -m user.packages repo add ALIAS INDEX_URL`.
Use the station's `bin` directory on `PYTHONPATH` for an extension-installed client.
Also verify the normal archive installation with
`weectl extension install VERSIONED_ARCHIVE_URL`. The
legacy URL installer alone does not exercise the repository client's managed
paths and transaction rules. A successful install does not verify real hardware
behavior.

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
