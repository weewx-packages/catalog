default: fast

fast:
    weectl extension repo validate repository.json
    python3 ci/upstreams.py readme --check

test-ci:
    python3 -m pytest -q ci/tests
