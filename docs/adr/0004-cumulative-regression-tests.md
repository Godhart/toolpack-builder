# ADR 0004: Cumulative regression tests

Status: accepted

Every fixed defect gets a regression test. Existing tests are retained unless the contract itself is intentionally changed. Release verification runs the full suite and `scripts/verify_package.py`.
