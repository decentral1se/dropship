# Dropship

> Get Things From One Computer To Another, Safely

[Magic-wormhole](https://magic-wormhole.readthedocs.io/en/latest) with a nice graphical interface.

![Screen cast of dropship interface](https://vvvvvvaria.org/~r/dropship0.1.gif)

_(click for video)_

## Features

- ???

## Supported Languages

- English

## System requirements

Dropship should work on the following distributions:

- Debian Stretch (9.0)

Other Linux distributions may work as well. We currently do not support MacOS or Windows.

Dropship requires the following system dependencies:

- GTK+
- Python > 3.6
- PyGObject 3.30.5+
- Cairo > 1.14

## Install

[![PyPI version](https://badge.fury.io/py/dropship.svg)](https://badge.fury.io/py/dropship)
[![Build Status](https://travis-ci.org/decentral1se/dropship.svg?branch=main)](https://travis-ci.org/decentral1se/dropship)

<details><summary>Debian Stretch</summary>
<pre>
$ sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install dropship
$ dropship  # run in your command-line terminal
</pre>
</details>

## Develop

See our [wiki](https://git.vvvvvvaria.org/rra/dropship/wiki).
