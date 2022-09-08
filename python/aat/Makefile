PYTHON=python
CONFIG=./config/synthetic.cfg

.DEFAULT_GOAL := help
.PHONY: build develop clean help

build:  ## build the library
	maturin build

develop:  ## build the library for development
	pip install --no-deps -e .[develop]

clean:  ## clean the project
	git clean -fdx

# Thanks to Francoise at marmelab.com for this
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'
