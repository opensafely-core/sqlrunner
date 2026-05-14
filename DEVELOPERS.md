# Notes for developers

## System requirements

### just

Follow installation instructions from the [Just Programmer's Manual](https://just.systems/man/en/chapter_4.html) for your OS.

Add completion for your shell. E.g. for bash:
```
source <(just --completions bash)
```

Show all available commands
```
just #  shortcut for just --list
```

### uv

Follow installation instructions from the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/) for your OS.


## Development

Set up a local development environment with

```sh
just devenv
```

and create a new branch.
Then, iteratively:

* Make changes to the code
* Run the tests with

  ```sh
  just test
  ```

* Check the code for issues with

  ```sh
  just check
  ```

* Fix any issues with

  ```sh
  just fix
  ```

* Commit the changes

Finally, push the branch to GitHub and open a pull request against the `main` branch.

### Use a dev image with opensafely-cli

Build a docker image tagged `sqlrunner:dev` that can be used in `project.yaml` for local testing:

```sh
just docker/build-for-os-cli

```

## Dependency management
Dependencies are managed with `uv`.
See the [uv documentation](https://docs.astral.sh/uv/concepts/projects/dependencies) for details on usage.

Changes to dependencies should be made via `uv` commands, or by modifying `pyproject.toml` directly followed by
[locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) via `uv` or `just` commands like
`just devenv` or `just upgrade-all`. You should not modify `uv.lock` manually.

Note that `uv.lock` must be reproducible from `pyproject.toml`. Otherwise, `just check` will fail.
If `just check` errors, you might have modified one file but not the other:
  - If you modified `pyproject.toml`, you must update `uv.lock` via `uv lock` / `just upgrade-all` or similar.
  - If you did not modify `pyproject.toml` but have changes in `uv.lock`, you should revert the changes to `uv.lock`,
  modify `pyproject.toml` as you require, then run `uv lock` to update `uv.lock`.

## Tagging a new version

OpenSAFELY SQL Runner follows [Semantic Versioning, v2.0.0][2].

A new __patch__ version is automatically tagged when a group of commits is pushed to the `main` branch;
for example, when a group that comprises a pull request is merged.
Alternatively, a new patch version is tagged for each commit in the group that has a message title prefixed with `fix`.
For example, a commit with the following message title would tag a new patch version when it is pushed to the `main` branch:

```
fix: a bug fix
```

A new __minor__ version is tagged for each commit in the group that has a message title prefixed with `feat`.
For example, a commit with the following message title would tag a new minor version when it is pushed to the `main` branch:

```
feat: a new feature
```

A new __major__ version is tagged for each commit in the group that has `BREAKING CHANGE` in its message body.
For example, a commit with the following message body would tag a new major version:

```
Remove a function

BREAKING CHANGE: Removing a function is not backwards-compatible.
```

Whilst there are other prefixes besides `fix` and `feat`, they do not tag new versions.

[1]: https://github.com/casey/just/
[2]: https://semver.org/spec/v2.0.0.html
