setup-dev:
	rm -rf .venv;
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip
	.venv/bin/pip3 install poetry
	.venv/bin/poetry install
	.venv/bin/pre-commit install
