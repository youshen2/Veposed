.PHONY: check test host format lint
LUA ?= lua
RUFF ?= ruff

format:
	$(RUFF) format .

lint:
	$(RUFF) check .
	$(RUFF) format --check .

check:
	cargo fmt --all -- --check
	cargo clippy --workspace --all-targets -- -D warnings
	cargo test --workspace
	python3 -m unittest discover -s tools/tests
	python3 scripts/test-host.py
	python3 scripts/test-recovery.py
	python3 scripts/test-bootstrap.py --lua $(LUA)
	python3 scripts/test-module.py
	python3 scripts/test-installer.py --lua $(LUA)
	python3 scripts/test-manager.py

test:
	cargo test --workspace

host:
	python3 scripts/test-host.py
