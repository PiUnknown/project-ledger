"""Thread-safe in-process per-IP and UTC-day request caps."""

from __future__ import annotations

from datetime import date, datetime, timezone
from threading import Lock


class RequestLimiter:
    def __init__(self, per_ip_per_minute: int, daily_cap: int) -> None:
        if per_ip_per_minute <= 0 or daily_cap <= 0:
            raise ValueError("request limits must be positive")
        self._per_ip_per_minute = per_ip_per_minute
        self._daily_cap = daily_cap
        self._minute_windows: dict[str, tuple[int, int]] = {}
        self._current_day: date | None = None
        self._daily_count = 0
        self._lock = Lock()

    def consume(self, ip_address: str, now: datetime | None = None) -> str | None:
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("now must include a timezone")
        current = current.astimezone(timezone.utc)
        minute_window = int(current.timestamp() // 60)

        with self._lock:
            if self._current_day != current.date():
                self._current_day = current.date()
                self._daily_count = 0

            prior_window, prior_count = self._minute_windows.get(ip_address, (minute_window, 0))
            ip_count = prior_count if prior_window == minute_window else 0
            if ip_count >= self._per_ip_per_minute:
                return "rate_limited"
            if self._daily_count >= self._daily_cap:
                return "daily_cap_reached"

            self._minute_windows[ip_address] = (minute_window, ip_count + 1)
            self._daily_count += 1
            expired = [
                address
                for address, (window, _) in self._minute_windows.items()
                if window < minute_window
            ]
            for address in expired:
                del self._minute_windows[address]
            return None
