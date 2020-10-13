# Dropship

[![Build Status](https://travis-ci.org/decentral1se/dropship.svg?branch=main)](https://travis-ci.org/decentral1se/dropship)

Lets try magic wormhole with a nice graphical interface.

![Screen cast of dropship interface](https://vvvvvvaria.org/~r/dropship0.1.gif)

_(click for video)_

## Install

> Coming Soon™

## Develop

### Documentation

See our [wiki](https://git.vvvvvvaria.org/rra/dropship/wiki).

### Install for Hacking

Install [poetry](https://python-poetry.org/docs/#installation) and then install the package locally.

```
$ poetry install
```

### Run in Hackity Hack Hack Mode

```bash
$ poetry run dropship
```

### Updating dependencies

- Change the bounds/versions/etc. in the [pyproject.toml](./pyproject.toml)
- Run `poetry update`
- Commit and push your changes

The [poetry.lock](./poetry.lock) file helps us all get the same dependencies.

### Adding a Github Mirror

We use a Github mirror so we can have a [gratis automated release build](./.travis.yml).

Add the following to the bottom of your `.git/config`.

```
[remote "all"]
  url = ssh://gitea@vvvvvvaria.org:12345/rra/dropship.git
  url = git@github.com:decentral1se/dropship.git
```

The `git push -u all main` will setup `git push` to automatically push to both remotes.

### Make a new Release

> Publishing binaries is disabled until we make further progress on [#3](https://git.vvvvvvaria.org/rra/dropship/issues/3)

```bash
$ git tag $mytag  # follow semver.org please
$ git push
```

The [Travis CI configuration](./.travis.yml) will run [a build](https://travis-ci.org/github/decentral1se/dropship) and [publish binaries here](https://github.com/decentral1se/dropship/releases).
