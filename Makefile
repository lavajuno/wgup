.PHONY: build clean coverage format test

build: clean format
	python3 -m build

clean:
	rm -f dist/*

coverage:
	coverage run --source="wgup" -m unittest discover test && \
	coverage html -d coverage.d

format:
	isort --profile black ./wgup ./test
	black ./wgup ./test

test:
	python3 -m unittest discover test
