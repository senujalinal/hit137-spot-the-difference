"""
game_state.py
HIT137 Group Assignment 3

Manages the game logic - tracking found differences, mistakes and score.
"""


class GameState:
    """
    Tracks current round state and cumulative score.
    Max 3 mistakes per round, 5 differences to find.
    """

    MAX_MISTAKES = 3
    TOTAL_DIFFERENCES = 5
    CLICK_TOLERANCE = 50  # pixels

    def __init__(self):
        self._total_score = 0
        self._found_indices = set()
        self._mistakes = 0
        self._locked_out = False
        self._revealed = False

    def reset_round(self):
        """Reset per-round state, keep cumulative score."""
        self._found_indices = set()
        self._mistakes = 0
        self._locked_out = False
        self._revealed = False

    def process_click(self, click_x, click_y, alterations):
        """
        Check if click hits an unfound difference.
        Returns dict with hit/mistake/lockout/complete info.
        """
        if self._locked_out or self._revealed:
            return {"hit": False, "index": None, "mistake": False,
                    "locked_out": self._locked_out, "complete": self.is_complete}

        for idx, alt in enumerate(alterations):
            if idx in self._found_indices:
                continue
            if self._hits(click_x, click_y, alt.region):
                self._found_indices.add(idx)
                self._total_score += 1
                return {"hit": True, "index": idx, "mistake": False,
                        "locked_out": False, "complete": self.is_complete}

        # missed
        self._mistakes += 1
        locked = self._mistakes >= self.MAX_MISTAKES
        if locked:
            self._locked_out = True
        return {"hit": False, "index": None, "mistake": True,
                "locked_out": locked, "complete": False}

    def reveal_all(self):
        self._revealed = True

    @property
    def found_indices(self):
        return set(self._found_indices)

    @property
    def found_count(self):
        return len(self._found_indices)

    @property
    def mistakes(self):
        return self._mistakes

    @property
    def mistakes_remaining(self):
        return self.MAX_MISTAKES - self._mistakes

    @property
    def remaining(self):
        return self.TOTAL_DIFFERENCES - len(self._found_indices)

    @property
    def is_locked_out(self):
        return self._locked_out

    @property
    def is_revealed(self):
        return self._revealed

    @property
    def is_complete(self):
        return len(self._found_indices) >= self.TOTAL_DIFFERENCES

    @property
    def is_round_over(self):
        return self._locked_out or self._revealed or self.is_complete

    @property
    def total_score(self):
        return self._total_score

    def _hits(self, cx, cy, region):
        """Check if click is inside region or within tolerance of its centre."""
        x, y, w, h = region
        if x <= cx <= x + w and y <= cy <= y + h:
            return True
        dist = ((cx - (x + w//2))**2 + (cy - (y + h//2))**2) ** 0.5
        return dist <= self.CLICK_TOLERANCE
