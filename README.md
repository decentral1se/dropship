# dropship

[![Build Status](https://travis-ci.org/decentral1se/dropship.svg?branch=main)](https://travis-ci.org/decentral1se/dropship)

Lets try magic wormhole with a nice graphical interface.

![Screen cast of dropship interface](https://vvvvvvaria.org/~r/dropship0.1.gif)

_(click for video)_

## what is what:

- `dropship.py`, run this with python3.
- `dropship.glade`, UI file, edit with glade.
- `dropship.css`, additional styling for UI.

## install:

`sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0`

`pip install -r requirments.txt`

## run:

`python3 dropship.py`

## operations:

### github mirror:

Add the following to the bottom of your `.git/config`.

```
[remote "all"]
  url = ssh://gitea@vvvvvvaria.org:12345/rra/dropship.git
  url = git@github.com:decentral1se/dropship.git
```

The `git push -u all main` will setup `git push` to automatically push to both remotes.

### make a release:

`git tag 0.0.1dev$whatever && git push`

The [Travis CI configuration](https://git.vvvvvvaria.org/rra/dropship/src/branch/main/.travis.yml) will run [a build](https://travis-ci.org/github/decentral1se/dropship) and [publish binaries here](https://github.com/decentral1se/dropship/releases).
