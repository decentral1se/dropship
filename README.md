# Dropship

[![Build Status](https://travis-ci.org/decentral1se/dropship.svg?branch=main)](https://travis-ci.org/decentral1se/dropship)

Lets try magic wormhole with a nice graphical interface.

![Screen cast of dropship interface](https://vvvvvvaria.org/~r/dropship0.1.gif)

_(click for video)_

## Install

> Coming Soon™

## Develop

### Install for Hacking

You'll need to install [pygobject](https://pygobject.readthedocs.io/) and system dependencies first.

It is recommended to do this through your system package manager. For a Debian based system, you would run the following:

```bash
$ sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

Then, you can install `dropship` using [poetry](https://python-poetry.org/docs/#installation):

```
$ poetry install
```

### Run in Hackity Hack Hack Mode

```bash
$ poetry run dropship
```

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

```bash
$ git tag $mytag  # follow semver.org please
$ git push
```

The [Travis CI configuration](./.travis.yml) will run [a build](https://travis-ci.org/github/decentral1se/dropship) and [publish binaries here](https://github.com/decentral1se/dropship/releases).

## Documentation from the Wild West

There isn't much but there is stuff out there!

- https://github.com/exaile/exaile
- https://github.com/virtuald/pygi-composite-templates
- https://github.com/sharkwouter/minigalaxy
- https://developer.puri.sm/Librem5/Apps/Gnome.html

Also try the `#glade` channel on the Gnome IRC.
