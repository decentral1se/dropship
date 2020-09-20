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

## development notes:

### How we handle asynchronous actions

We use the [Trio guest
mode](https://trio.readthedocs.io/en/latest/reference-lowlevel.html#using-guest-mode-to-run-trio-on-top-of-other-event-loops)
instead of relying on threads because those are hard to manage. Running two
loops (Gtk and Trio) has disadvantages but overall, it offers a very clear way
of organising and executing asynchronous operations.

In practice, this means you need to arrange the following:

1. Wire up your usual hook (`self.drop_box.connect("drag-data-received", self.on_drop)`)
2. In your hook function, call your asynchronous function via the `self.nursery.start_soon` API
3. Define your asynchronous function with `async def` and use the `await` keyword as usual

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
