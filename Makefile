.PHONY: build clean format test

build: clean
	python3 -m build

clean:
	rm -f dist/*

format:
	isort --profile black ./wgtui ./test
	black ./wgtui ./test

test:
	python3 -m unittest discover test
