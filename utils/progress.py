import time


class ProgressBar:
    """
    Tracks upload/download progress and renders a Telegram-friendly text bar.
    Updates are throttled to min_interval seconds to respect Telegram's edit
    rate limit (roughly 1 edit/s per chat).
    """

    BAR_WIDTH = 20
    MIN_INTERVAL = 3.5  # seconds between message edits

    def __init__(self, total: int) -> None:
        self.total = total
        self.start_time = time.monotonic()
        self._last_update = 0.0

    def should_update(self) -> bool:
        return (time.monotonic() - self._last_update) >= self.MIN_INTERVAL

    def render(self, current: int, header: str) -> str:
        self._last_update = time.monotonic()
        elapsed = time.monotonic() - self.start_time or 0.001

        speed = current / elapsed  # bytes/s
        pct = (current / self.total * 100) if self.total else 0
        filled = int(self.BAR_WIDTH * pct / 100)
        bar = "█" * filled + "░" * (self.BAR_WIDTH - filled)

        remaining = self.total - current
        eta = remaining / speed if speed > 0 else 0

        return (
            f"{header}\n\n"
            f"[{bar}] {pct:.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 {_fmt_bytes(current)} / {_fmt_bytes(self.total)}\n"
            f"⚡ Speed: {_fmt_bytes(speed)}/s\n"
            f"⏳ ETA: {_fmt_eta(eta)}"
        )


def _fmt_bytes(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _fmt_eta(seconds: float) -> str:
    if seconds <= 0:
        return "0s"
    if seconds < 60:
        return f"{int(seconds)}s"
    m, s = divmod(int(seconds), 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


# Exported for other modules
format_bytes = _fmt_bytes
