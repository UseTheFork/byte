[private]
[doc('Display the list of recipes')]
default:
  @just --list


[doc('Run Pytest With Coverage Report')]
test:
		uv run pytest --cov-report=xml --cov-report=term-missing --cov=src/byte src/tests/
