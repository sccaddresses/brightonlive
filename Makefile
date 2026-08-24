.PHONY: install test offline run validate release bundle

install:
	python -m pip install -e ".[dev]"

test:
	pytest

offline:
	python run.py offline

run:
	python run.py run --config config/brighton.yaml

validate:
	python scripts/validate_repo.py
	python scripts/validate_outputs.py --allow-empty

release:
	python scripts/release_gate.py --strict

bundle:
	python scripts/build_release_bundle.py
