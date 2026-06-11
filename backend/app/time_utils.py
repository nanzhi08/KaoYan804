from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def local_today_start_as_utc_naive() -> datetime:
    local_start = datetime.now().astimezone().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    return local_start.astimezone(timezone.utc).replace(tzinfo=None)
