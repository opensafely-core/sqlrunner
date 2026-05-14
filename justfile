set dotenv-load := true
set positional-arguments := true

# list available commands
default:
    @"{{ just_executable() }}" --list

# clean up temporary files
clean:
    rm -rf .venv

# Install production requirements into and remove extraneous packages from venv
prodenv:
    uv sync --no-dev

# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#

# Install dev requirements into venv without removing extraneous packages
devenv: install-precommit
    uv sync --inexact

# Ensure precommit is installed
install-precommit:
    #!/usr/bin/env bash
    set -euo pipefail

    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || uv run pre-commit install

# Upgrade a single package to the latest version as of the cutoff in pyproject.toml
upgrade-package package: && uvmirror devenv
    uv lock --upgrade-package {{ package }}

# Upgrade all packages to the latest versions
upgrade-all cooldown="7 days ago": && devenv
    uv lock --upgrade --exclude-newer "{{ cooldown }}"

# update the uv mirror requirements file
uvmirror file="requirements.uvmirror.txt":
    rm -f {{ file }}
    uv export --format requirements-txt --frozen --no-hashes --all-groups --all-extras > {{ file }}

# This is the default input command to update-dependencies action
# https://github.com/bennettoxford/update-dependencies-action

# recipe is used for doing lockfileMaintenance via update-dependencies action, until min release age is respected fo uv
update-dependencies: upgrade-all && uvmirror

# *args is variadic, 0 or more. This allows us to do `just test -k match`, for example.

# Run the tests
test *args:
    uv run coverage run --module pytest "$@"
    uv run coverage report || uv run coverage html

format *args:
    uv run ruff format --diff --quiet "$@"

lint *args:
    uv run ruff check "$@" .

lint-actions:
    docker run --rm -v $(pwd):/repo:ro --workdir /repo rhysd/actionlint:1.7.8 -color

# Run the various dev checks but does not change any files
check:
    #!/usr/bin/env bash
    set -euo pipefail

    failed=0

    check() {
      echo -e "\e[1m=> ${1}\e[0m"
      rc=0
      # Run it
      eval $1 || rc=$?
      # Increment the counter on failure
      if [[ $rc != 0 ]]; then
        failed=$((failed + 1))
        # Add spacing to separate the error output from the next check
        echo -e "\n"
      fi
    }

    check "just check-lockfile"
    check "just format"
    check "just lint"
    check "just lint-actions"
    test -d docker/ && check "just docker/lint"

    if [[ $failed > 0 ]]; then
      echo -en "\e[1;31m"
      echo "   $failed checks failed"
      echo -e "\e[0m"
      exit 1
    fi

# validate uv.lock
check-lockfile:
    #!/usr/bin/env bash
    set -euo pipefail
    # Make sure lockfile is reproducible from pyproject.toml
    unset UV_EXCLUDE_NEWER
    rc=0
    uv lock --check

# Fix formatting, import sort ordering, and justfile
fix:
    -uv run ruff check --fix .
    -uv run ruff format .
    -just --fmt --unstable

# Run the dev project
run: devenv
    echo "Not implemented yet"
