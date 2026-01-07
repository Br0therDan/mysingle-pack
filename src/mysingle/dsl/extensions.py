"""
DSL Extensions for Pine Script compatibility.

Provides support for:
- var (State variables)
- plot (Visualizations)
- strategy.* (Trading commands)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class Visualization:
    """Visualization command data"""

    type: str
    series: pd.Series
    title: Optional[str] = None
    color: Optional[str] = None
    linewidth: Optional[int] = None
    style: Optional[str] = None
    value: Optional[float] = None  # For hline


@dataclass
class TradingCommand:
    """Trading command data"""

    type: str
    id: str
    direction: Optional[str] = None
    qty: Optional[float] = None
    limit: Optional[float] = None
    stop: Optional[float] = None
    comment: Optional[str] = None


class ExecutionContext:
    """
    Context to capture side effects during DSL execution.
    Passed via params['_context'].
    """

    def __init__(self, equity: float = 100000.0, position_size: float = 0.0):
        self.visualizations: List[Visualization] = []
        self.trading_commands: List[TradingCommand] = []
        self.state_variables: Dict[str, Any] = {}
        self.equity = equity
        self.position_size = position_size

    def add_visualization(self, viz: Visualization):
        self.visualizations.append(viz)

    def add_trading_command(self, cmd: TradingCommand):
        self.trading_commands.append(cmd)

    def set_variable(self, name: str, value: Any):
        self.state_variables[name] = value

    def get_variable(self, name: str) -> Any:
        return self.state_variables.get(name)


# StrategyWrapper and other root proxies are now in proxies.py
