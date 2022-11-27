.DEFAULT_GOAL := help
.PHONY: develop build lint checks tests tests-ci-gha

develop-rust:
	make -C rust develop

develop: develop-rust  ## Setup project for development

build-rust:
	make -C rust build

build: build-rust  ## Build the project

lint-rust:
	make -C rust lint

lint: lint-rust  ## Run project linters

checks-rust:
	make -C rust checks

checks: checks-rust  ## Run any other checks

tests-rust:
	make -C rust tests

tests: tests-rust  ## Run the tests

tests-ci-gha-rust:
	make -C rust tests-ci-gha

tests-ci-gha: tests-ci-gha-rust
	
