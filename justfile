default: fast

fast:
    weectl extension repo validate repository.json

test-ci:
    python3 -m pytest -q ci/tests
