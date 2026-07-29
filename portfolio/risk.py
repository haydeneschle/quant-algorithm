"""
Dynamic risk management via a 2-bit saturating counter, modeled on
the classic bimodal branch predictor used in CPU design. This is a
different sizing dimension from the ATR-based volatility scalar in
volatility.py: this one reacts to *how the strategy itself has been
performing*, whereas the ATR scalar reacts to *how volatile the
market currently is*. The two multiply together in Portfolio.
"""

from enum import IntEnum
from dataclasses import dataclass


class RiskState(IntEnum):
    """
    2-bit saturating counter, modeled directly on the classic bimodal
    branch predictor: 4 states, one step per outcome, saturating at
    the extremes. Only crossing the midpoint changes the effective
    'prediction' (here, whether we're in a conservative or aggressive
    regime) — a single anomalous result doesn't flip the regime,
    but sustained wins/losses will.
    """
    STRONGLY_CONSERVATIVE = 0
    WEAKLY_CONSERVATIVE = 1
    WEAKLY_AGGRESSIVE = 2
    STRONGLY_AGGRESSIVE = 3


@dataclass(frozen=True)
class RiskBounds:
    """
    The min/max range each risk parameter can take. RiskGovernor
    interpolates continuously within these bounds based on the
    current RiskState, rather than jumping between fixed tiers.
    """
    min_position_size: float = 0.05
    max_position_size: float = 0.20
    min_stop_loss_pct: float = 0.03
    max_stop_loss_pct: float = 0.08
    min_open_positions: int = 2
    max_open_positions: int = 6


@dataclass(frozen=True)
class RiskProfile:
    """The concrete, resolved risk parameters for the current state."""
    max_position_size: float
    stop_loss_pct: float
    max_open_positions: int


class RiskGovernor:
    """
    Dynamic risk sizing via a 2-bit saturating counter, rather than
    fixed discrete tiers. Every trade outcome nudges the counter by
    one step (saturating at the extremes); position size, stop-loss
    width, and max concurrent positions are all interpolated smoothly
    from the current state rather than jumping between arbitrary tiers.
    """

    def __init__(self, bounds: RiskBounds = None,
                 starting_state: RiskState = RiskState.WEAKLY_CONSERVATIVE):
        self.bounds = bounds or RiskBounds()
        self.state = starting_state

    def record_trade_result(self, pnl: float) -> None:
        """Call after every closed trade. One step per outcome, saturating at extremes."""
        if pnl > 0:
            self.state = RiskState(min(self.state + 1, max(RiskState)))
        else:
            self.state = RiskState(max(self.state - 1, min(RiskState)))

    @property
    def is_aggressive_regime(self) -> bool:
        """The 'effective prediction' — only the top bit matters, exactly like a bimodal predictor."""
        return self.state >= RiskState.WEAKLY_AGGRESSIVE

    @property
    def current_profile(self) -> RiskProfile:
        """
        Resolve the current RiskState into concrete sizing parameters
        by linearly interpolating across RiskBounds. Using a continuous
        interpolation (rather than a lookup table per state) means the
        bounds can be tuned independently of how many discrete states exist.
        """
        t = self.state / max(RiskState)  # normalize state to 0.0 -> 1.0

        b = self.bounds
        position_size = b.min_position_size + t * (b.max_position_size - b.min_position_size)
        stop_loss = b.min_stop_loss_pct + t * (b.max_stop_loss_pct - b.min_stop_loss_pct)
        max_positions = round(b.min_open_positions + t * (b.max_open_positions - b.min_open_positions))

        return RiskProfile(
            max_position_size=position_size,
            stop_loss_pct=stop_loss,
            max_open_positions=max_positions,
        )