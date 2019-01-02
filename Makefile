# Testing
test:
	pipenv run pytest -v -c env.list

# Cleanup
clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf .cache

clean_vscode:
	rm -rf .vscode

clean_pypi:
	rm -rf dist
	rm -rf epages_rest_python.egg-info

clean_all: clean clean_vscode clean_pypi

.PHONY: test \
clean clean_vscode clean_pypi clean_all
