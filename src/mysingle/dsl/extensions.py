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

    def __init__(self):
        self.visualizations: List[Visualization] = []
        self.trading_commands: List[TradingCommand] = []
        self.state_variables: Dict[str, Any] = {}

    def add_visualization(self, viz: Visualization):
        self.visualizations.append(viz)

    def add_trading_command(self, cmd: TradingCommand):
        self.trading_commands.append(cmd)


class StrategyWrapper:
    """Wrapper for strategy.* commands"""

    def __init__(self, context: Optional[ExecutionContext]):
        self._context = context

    def entry(
        self,
        id: str,
        direction: str,
        qty: Optional[float] = None,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        comment: Optional[str] = None,
    ):
        if self._context:
            self._context.add_trading_command(
                TradingCommand(
                    type="entry",
                    id=id,
                    direction=direction,
                    qty=qty,
                    limit=limit,
                    stop=stop,
                    comment=comment,
                )
            )

    def close(
        self,
        id: str,
        comment: Optional[str] = None,
        qty_percent: Optional[float] = None,
    ):
        if self._context:
            self._context.add_trading_command(
                TradingCommand(
                    type="close",
                    id=id,
                    comment=comment,
                    qty=qty_percent,  # reusing qty for qty_percent
                )
            )

    def exit(
        self,
        id: str,
        from_entry: str,
        stop: Optional[float] = None,
        limit: Optional[float] = None,
        comment: Optional[str] = None,
    ):
        if self._context:
            self._context.add_trading_command(
                TradingCommand(
                    type="exit",
                    id=id,
                    direction=from_entry,
                    stop=stop,
                    limit=limit,
                    comment=comment,
                )
            )

    def cancel(self, id: str):
        if self._context:
            self._context.add_trading_command(TradingCommand(type="cancel", id=id))

    # Constants
    long = "long"
    short = "short"


def var_wrapper(value: Any, **kwargs) -> Any:
    """
    Wrapper for 'var' keyword.
    In vectorized execution, this currently just returns the initial value.
    Future: Implement state persistence if needed.
    """
    return value


def plot_wrapper(
    context: Optional[ExecutionContext],
    series: Any,
    title: str = "",
    color: str = "",
    linewidth: int = 1,
    style: str = "",
):
    """Wrapper for 'plot' command"""
    if context:
        # Ensure series is a pandas Series (handle scalars)
        if not isinstance(series, (pd.Series, pd.DataFrame)):
            # If scalar, we might not want to plot it as a series unless we have the index.
            # But for now, just store it.
            pass

        context.add_visualization(
            Visualization(
                type="plot",
                series=series,
                title=title,
                color=color,
                linewidth=linewidth,
                style=style,
            )
        )
