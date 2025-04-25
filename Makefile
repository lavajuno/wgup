all:
	@echo "Available targets: format"

format:
	isort --profile black .
	black .
