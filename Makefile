install:
	pip install -r requirements.txt

run:
	python3 main.py maps/easy/01_linear_path.txt

debug:
	python3 main.py maps/easy/01_linear_path.txt

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


.PHONY: install run debug clean lint
