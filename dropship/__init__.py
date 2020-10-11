from logging import basicConfig, getLogger
from os import environ

from trio import open_nursery, sleep_forever
from trio_gtk import run


def main():
    """Trio main entrypoint."""
    from dropship.dropship import DropShip

    async def _main():
        async with open_nursery() as nursery:
            DropShip(nursery)
            await sleep_forever()

    run(_main)


basicConfig(level=environ.get("LOGLEVEL", "INFO"))
log = getLogger("dropship")
