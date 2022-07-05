# Contributing Guidelines

First off, thanks for considering to contribute to this project!

These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Git flow

### Creating branches

A new branch should be always created from the main branch `master`, except in certain cases which require to be justified.

#### Naming pattern

The pattern is: `{category}/{slugified-description}`. Where:

- `category` is the type of work. Can be: `feature`, `bug`, `tooling`, `refactor`, `test`, `chore`, `release`, `hotfix`, `docs`, `ci`, `deploy` or `release-candidate`.
- `slugified-description` is the description of the work, slugified.

Example: `feature/improve-encoding`

### Merge Requests workflow

#### Rules

- the code coverage must be increased or equal, never decreased. If you write some new code, write new tests.
- the code must run without any error on the CI.

#### Using the draft status

A draft Merge Request is a merge request that is not ready to be merged but the code is published to allow other team mates follow the development.

Comments are welcome but they must be global, about the conception, not the details (wait for the WIP status removal).

---

## Code Style

Make sure your code _roughly_ follows [PEP-8](https://www.python.org/dev/peps/pep-0008/) and keeps things consistent with the rest of the code. Related tools:

- docstrings: [sphinx-style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html#the-sphinx-docstring-format) is used to write technical documentation.
- formatting: [black](https://black.readthedocs.io/) is used to automatically format the code without debate.
- sorted imports: [isort](https://pycqa.github.io/isort/) is used to sort imports
- static analisis (linter): [flake8](https://flake8.pycqa.org/) is used to catch some dizziness and keep the source code healthy.

---

## Git hooks

We use git hooks through [pre-commit](https://pre-commit.com/) to enforce and automatically check some "rules". Please install it before to push any commit: `pre-commit install`.

See the relevant configuration file: `.pre-commit-config.yaml`.
