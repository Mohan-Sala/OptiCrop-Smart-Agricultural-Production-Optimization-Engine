from datetime import datetime, time
from typing import List
from app.models.deployment import DeploymentFreezeWindow

class FreezeWindowService:
    """Service to evaluate whether a deployment action falls within a configured deployment freeze window."""

    @staticmethod
    def is_frozen(current_time: datetime, windows: List[DeploymentFreezeWindow]) -> bool:
        """Determines if the given current_time falls inside any active freeze window.
        
        Weekly schedule calculation is normalized to seconds since Monday 00:00:00 UTC.
        """
        # Day of week: Monday is 0, Sunday is 6
        current_day = current_time.weekday()
        current_offset = (
            current_day * 86400
            + current_time.hour * 3600
            + current_time.minute * 60
            + current_time.second
        )

        for win in windows:
            if not win.is_active:
                continue

            start_offset = (
                win.start_day_of_week * 86400
                + win.start_time_utc.hour * 3600
                + win.start_time_utc.minute * 60
                + win.start_time_utc.second
            )
            end_offset = (
                win.end_day_of_week * 86400
                + win.end_time_utc.hour * 3600
                + win.end_time_utc.minute * 60
                + win.end_time_utc.second
            )

            if start_offset <= end_offset:
                if start_offset <= current_offset <= end_offset:
                    return True
            else:
                # Window spans across the end-of-week boundary (e.g. Sunday night to Monday morning)
                if current_offset >= start_offset or current_offset <= end_offset:
                    return True

        return False
