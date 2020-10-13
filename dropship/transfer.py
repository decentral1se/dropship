from os.path import basename, getsize


class PendingTransfer:
    """A pending transfer context and config."""

    def __init__(self, fpath, code, scope):
        self.fpath = fpath
        self.code = code
        self.scope = scope

    @property
    def fname(self):
        """Filename being transferred."""
        return basename(self.fpath)

    @property
    def size(self):
        """Filename size."""
        return self._human_readable_size(getsize(self.fpath))

    def cancel(self):
        """Cancel the transfer."""
        self.scope.cancel()

    def _human_readable_size(self, num, suffix="B"):
        """Convert file size to human readable format.

           Thanks Fred. See https://stackoverflow.com/a/1094933.
        """
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, "Yi", suffix)
