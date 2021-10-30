linter:
	PYTHONPATH=$(shell pwd)/project poetry run black --line-length 120 project
	PYTHONPATH=$(shell pwd)/project poetry run isort project