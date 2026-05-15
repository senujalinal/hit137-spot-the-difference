"""
game_state.py
HIT137 Group Assignment 3

Manages game logic - tracking found differences, mistakes and score.
Score is cumulative across multiple images (never resets).
"""


class GameState:
    """
    Tracks current round state and cumulative score.
    Max 3 mistakes per round, 5 differences to find.
    """

    # player loses the round after this many wrong clicks
    MAX_MISTAKES  = 3
    # every image always has exactly this many hidden differences
    TOTAL_DIFFERENCES = 5
    # how close a click needs to be to count as a hit, in image pixels
    CLICK_TOLERANCE = 50

    def __init__(self):
        # carries over between images so the player builds a running total
        self._total_score = 0
        # keeps track of which differences the player has already found
        self._found_indices = set()
        # counts how many times the player clicked the wrong area this image
        self._mistakes = 0
        # flips to True once the player burns through all 3 mistakes
        self._locked_out = False
        # flips to True when the player presses Reveal All
        self._revealed = False

    def reset_round(self):
        # Reset per-round state, keep cumulative score.
        self._found_indices = set()
        self._mistakes = 0
        self._locked_out = False
        self._revealed = False

    def process_click(self, click_x, click_y, alterations):
        """
        Check if click hits an unfound difference.
        Returns dict with hit/index/mistake/locked_out/complete info.
        """
        # ignore clicks once the round is over to avoid accidental changes
        if self._locked_out or self._revealed:
            return {"hit": False, "index": None, "mistake": False,
                    "locked_out": self._locked_out, "complete": self.is_complete}

        for idx, alt in enumerate(alterations):
            # skip any difference the player already found
            if idx in self._found_indices:
                continue
            if self._hits(click_x, click_y, alt.region):
                self._found_indices.add(idx)
                # each correct find is worth one point toward the running total
                self._total_score += 1
                return {"hit": True, "index": idx, "mistake": False,
                        "locked_out": False, "complete": self.is_complete}

        # click didn't land on any unfound difference, so it counts as a mistake
        self._mistakes += 1
        locked = self._mistakes >= self.MAX_MISTAKES
        if locked:
            self._locked_out = True
        return {"hit": False, "index": None, "mistake": True,
                "locked_out": locked, "complete": False}

    def reveal_all(self):
        # stop accepting clicks and let the GUI show the remaining circles
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
        # tells the player how many wrong clicks they have left before lockout
        return self.MAX_MISTAKES - self._mistakes

    @property
    def remaining(self):
        # how many differences are still waiting to be found
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
        # the round ends by finding all differences, running out of guesses, or revealing
        return self._locked_out or self._revealed or self.is_complete

    @property
    def total_score(self):
        # Cumulative score across all images loaded this session.
        return self._total_score

    def _hits(self, cx, cy, region):
        # Check if click is inside region or within tolerance of its centre.
        x, y, w, h = region
        # direct hit inside the bounding box
        if x <= cx <= x + w and y <= cy <= y + h:
            return True
        # also accept clicks that land just outside but close to the centre
        dist = ((cx - (x + w//2))**2 + (cy - (y + h//2))**2) ** 0.5
        return dist <= self.CLICK_TOLERANCE