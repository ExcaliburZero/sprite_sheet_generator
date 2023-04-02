.PHONY: format

format:
	python -m black **.py

typecheck:
	python -m mypy --strict **.py