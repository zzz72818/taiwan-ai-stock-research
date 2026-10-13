"""Bounded retries for transient Windows / sync-client replacement locks."""
import time


def replace_with_retry(temporary, destination):
    for attempt in range(4):
        try:
            temporary.replace(destination)
            return
        except PermissionError:
            if attempt == 3:
                raise
            time.sleep(0.05 * (attempt + 1))
