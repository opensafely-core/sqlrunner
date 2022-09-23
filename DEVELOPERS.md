# Notes for developers

## System requirements

### `just`

[`just`][1] is a handy way to save and run project-specific commands.
It's unrelated to the package with the same name on PyPI.

```sh
# macOS
brew install just

# Linux
# Install from https://github.com/casey/just/releases

# Show all available commands
just # Shortcut for just --list
```

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
