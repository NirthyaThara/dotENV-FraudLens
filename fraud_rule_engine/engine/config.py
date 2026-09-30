from dataclasses import dataclass

@dataclass(frozen=True)
class ScoringConfig:
    medium_threshold: float = 30
    high_threshold: float = 60
    flag_threshold: float = 60
    corroboration_bonus_2: float = 5
    corroboration_bonus_3: float = 10
    max_score: float = 100

DEFAULT_CONFIG = ScoringConfig()
