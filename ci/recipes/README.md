# Catalog packaging patches

Each directory contains the changes applied to the source commit recorded in
`ci/package-provenance.json`. Apply its patch from that repository's root with
`patch -p1 < package.patch`. Complete source trees and original notices remain
in the published archives.

Patches and bundled license texts retain their upstream licenses. The catalog's
license does not replace them. Archive SHA-256 values refer to the published
bytes; the provenance record also identifies each patch and test suite.
