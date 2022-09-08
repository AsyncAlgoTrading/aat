# Contributing

Thank you for your interest in contributing to aat!


## Reporting bugs, feature requests, etc.

To report bugs, request new features or similar, please open an issue on the Github
repository.

A good bug report includes:

- Expected behavior
- Actual behavior
- Steps to reproduce (preferably as minimal as possible)

## Minor changes, typos etc.

Minor changes can be contributed by navigating to the relevant files on the Github repository,
and clicking the "edit file" icon. By following the instructions on the page you should be able to
create a pull-request proposing your changes. A repository maintainer will then review your changes,
and either merge them, propose some modifications to your changes, or reject them (with a reason for
the rejection).

## Setting up a development environment

If you want to help resolve an issue by making some changes that are larger than that covered by the above paragraph, it is recommended that you:

- Fork the repository on Github
- Clone your fork to your computer
- Run the following commands inside the cloned repository:
  - `pip install -e .[dev]` - This will install the Python package in development
    mode.
- Validate the install by running the tests:
  - `py.test` - This command will run the Python tests.
  - `flake8 aat/` - This command will run the Python linters.

Once you have such a development setup, you should:

- Make the changes you consider necessary
- Run the tests to ensure that your changes does not break anything
- Run the linters to ensure that your changes does not break anything
- Run mypy if necessary to alert for problems with type annotations
- If you add new code, preferably write one or more tests for checking that your code works as expected.
- Commit your changes and publish the branch to your github repo.
- Open a pull-request (PR) back to the main repo on Github.

## Style
### Docstrings
Docstrings are [google format](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).


### Python
Python code is formatted with [black](https://github.com/psf/black) and [flake8](https://github.com/PyCQA/flake8) and annotated for typings with [mypy](https://github.com/python/mypy).

#### Misc
- Public methods should be `camelCase`
- Public attributes should be `camelCase`
- Private methods should be `snake_case`
- Private attributes should be `snake_case`
- JSON import/export should be `snake_case`

### JS
JS Code is writted in `typescript` and formatted with `eslint` and `prettier`.

### C++
C++ Code is formateed with [cpplint](https://github.com/cpplint/cpplint) and [clang-format](https://clang.llvm.org/docs/ClangFormat.html).

