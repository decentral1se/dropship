from subprocess import PIPE

from trio import TASK_STATUS_IGNORED, CancelScope, open_process, run_process

from dropship import log


async def wormhole_send(fpath, parent, task_status=TASK_STATUS_IGNORED):
    """Run `wormhole send` on a local file path."""
    with CancelScope() as scope:
        command = ["wormhole", "send", fpath]
        process = await open_process(command, stderr=PIPE)
        output = await process.stderr.receive_some()
        code = output.decode().split()[-1]
        task_status.started((code, scope,))
        log.info(f"wormhole_send: now waiting for other side ({code})")
        await process.wait()
        log.info(f"wormhole_send: succesfully transfered ({code})")

    if scope.cancel_called:
        process.terminate()
        log.info(f"wormhole_send: succesfully terminated process ({code})")

    parent._remove_pending_transfer(code)


async def wormhole_recv(code, parent, task_status=TASK_STATUS_IGNORED):
    """Run `wormhole receive` on a pending transfer code."""
    with CancelScope() as scope:
        command = ["wormhole", "receive", "--accept-file", code]
        process = await open_process(command, stderr=PIPE)
        task_status.started((scope,))
        log.info(f"wormhole_recv: now starting receiving process ({code})")
        await process.wait()
        log.info(f"wormhole_recv: succesfully received ({code})")

    if scope.cancel_called:
        process.terminate()
        log.info(f"wormhole_recv: succesfully terminated process ({code})")

    parent._remove_pending_transfer(code)
