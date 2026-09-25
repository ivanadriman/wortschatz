"""
core/srs_engine.py - Spaced Repetition (SM-2 variant) and Leitner interval scheduling.
Provides deterministic calculation of intervals, ease factors, and due dates.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class SRSState:
    reps: int = 0
    interval_days: int = 0
    ease_factor: float = 2.5
    next_review_date: Optional[str] = None  # YYYY-MM-DD
    status: str = "new"                     # new, learning, mastered


def calculate_next_review(
    rating: int,  # 1 = Needs Practice / Again, 2 = Good, 3 = Easy / Mastered
    current_reps: int = 0,
    current_interval: int = 0,
    current_ease: float = 2.5,
    today: Optional[datetime] = None
) -> SRSState:
    """
    SuperMemo-2 (SM-2) inspired scheduling algorithm.
    """
    if today is None:
        today = datetime.now()

    if rating == 1:  # Failed / Needs Practice
        new_reps = 0
        new_interval = 1
        new_ease = max(1.3, current_ease - 0.2)
        new_status = "learning"
    elif rating == 2:  # Good / Maintained
        if current_reps == 0:
            new_interval = 1
        elif current_reps == 1:
            new_interval = 3
        else:
            new_interval = int(round(current_interval * current_ease))
        new_reps = current_reps + 1
        new_ease = current_ease
        new_status = "learning" if new_interval < 7 else "mastered"
    else:  # rating == 3: Mastered / Easy
        if current_reps == 0:
            new_interval = 3
        elif current_reps == 1:
            new_interval = 7
        else:
            new_interval = int(round(current_interval * current_ease * 1.3))
        new_reps = current_reps + 1
        new_ease = min(3.0, current_ease + 0.15)
        new_status = "mastered"

    next_date = (today + timedelta(days=new_interval)).strftime("%Y-%m-%d")

    return SRSState(
        reps=new_reps,
        interval_days=new_interval,
        ease_factor=round(new_ease, 2),
        next_review_date=next_date,
        status=new_status
    )
