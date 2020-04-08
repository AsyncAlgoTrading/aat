CONFIG=./config/synthetic.cfg


run:  build  ## Clean and make target, run target
	python3 -m aat $(CONFIG)

buildext: ## build the package extensions
	python3 setup.py build_ext

build: ## build the package
	python3 setup.py build

js:  ## build the js assets
	cd js && yarn build

install: ## install the package
	python3 -m pip install .

tests: ## Clean and Make unit tests
	python3 -m pytest -vvv ./aat/tests --cov=aat --junitxml=python_junit.xml --cov-report=xml --cov-branch

lint: ## run linter
	python3 -m flake8 aat setup.py

fix:  ## run autopep8/tslint fix
	python3 -m autopep8 --in-place -r -a -a aat/ setup.py

fixcpp:  ## run clang-format
	clang-format -i -style=file `find ./cpp -name "*.*pp"`

annotate: ## MyPy type annotation check
	python3 -m mypy aat

annotate_l: ## MyPy type annotation check - count only
	python3 -m mypy -s aat | wc -l 

docs:  ## Build the sphinx docs
	make -C docs html
	open ./docs/_build/html/index.html

dist:  ## dist to pypi
	rm -rf dist build
	python3 setup.py sdist bdist_wheel
	twine check dist/* && twine upload dist/*

clean: ## clean the repository
	find . -name "__pycache__" | xargs rm -rf
	find . -name "*.pyc" | xargs rm -rf
	rm -rf .coverage coverage cover htmlcov logs build dist *.egg-info
	find . -name "*.so"  | xargs rm -rf
	make -C ./docs clean

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'

.PHONY: run buildext build js install tests lint fix docs dist clean help fixcpp

