"""Trading operations module with advanced MetaTrader5 functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from .dataframe import Mt5DataClient

if TYPE_CHECKING:
    from datetime import datetime


class Mt5TradingClient(Mt5DataClient):
    """MetaTrader5 trading client with advanced trading operations.

    This class extends Mt5DataClient to provide specialized trading functionality
    including position management, order analysis, and trading performance metrics.
    """

    def calculate_position_pnl(
        self,
        symbol: str | None = None,
        group: str | None = None,
        ticket: int | None = None,
    ) -> pd.DataFrame:
        """Calculate profit/loss for open positions.

        Args:
            symbol: Optional symbol filter.
            group: Optional group filter.
            ticket: Optional position ticket filter.

        Returns:
            DataFrame with position P&L calculations.
        """
        positions_df = self.positions_get_as_df(
            symbol=symbol, group=group, ticket=ticket
        )

        if positions_df.empty:
            return pd.DataFrame()

        positions_df = positions_df.copy()
        positions_df["unrealized_pnl"] = positions_df["profit"]
        positions_df["pnl_percentage"] = (
            positions_df["profit"] / positions_df["volume"] * 100
        )

        return positions_df[
            [
                "symbol",
                "volume",
                "price_open",
                "price_current",
                "unrealized_pnl",
                "pnl_percentage",
                "swap",
                "profit",
            ]
        ]

    def get_trading_summary(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get comprehensive trading summary for a period.

        Args:
            date_from: Start date for analysis.
            date_to: End date for analysis.
            symbol: Optional symbol filter.

        Returns:
            Dictionary with trading statistics.
        """
        deals_df = self.history_deals_get_as_df(
            date_from=date_from, date_to=date_to, symbol=symbol
        )

        if deals_df.empty:
            return {
                "total_deals": 0,
                "total_profit": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
            }

        profit_deals = deals_df[deals_df["profit"] > 0]
        loss_deals = deals_df[deals_df["profit"] < 0]

        total_profit = deals_df["profit"].sum()
        total_wins = len(profit_deals)
        total_losses = len(loss_deals)
        total_deals = len(deals_df)

        win_rate = (total_wins / total_deals * 100) if total_deals > 0 else 0.0

        gross_profit = profit_deals["profit"].sum() if not profit_deals.empty else 0.0
        gross_loss = abs(loss_deals["profit"].sum()) if not loss_deals.empty else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")

        return {
            "total_deals": total_deals,
            "winning_deals": total_wins,
            "losing_deals": total_losses,
            "total_profit": total_profit,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "largest_win": profit_deals["profit"].max()
            if not profit_deals.empty
            else 0.0,
            "largest_loss": loss_deals["profit"].min() if not loss_deals.empty else 0.0,
            "average_win": profit_deals["profit"].mean()
            if not profit_deals.empty
            else 0.0,
            "average_loss": loss_deals["profit"].mean()
            if not loss_deals.empty
            else 0.0,
        }

    def get_symbol_trading_stats(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> pd.DataFrame:
        """Get trading statistics grouped by symbol.

        Args:
            date_from: Start date for analysis.
            date_to: End date for analysis.

        Returns:
            DataFrame with per-symbol trading statistics.
        """
        deals_df = self.history_deals_get_as_df(date_from=date_from, date_to=date_to)

        if deals_df.empty:
            return pd.DataFrame()

        symbol_stats = (
            deals_df.groupby("symbol")
            .agg({
                "profit": ["count", "sum", "mean"],
                "volume": "sum",
            })
            .round(2)
        )

        symbol_stats.columns = [
            "deal_count",
            "total_profit",
            "avg_profit",
            "total_volume",
        ]
        symbol_stats = symbol_stats.reset_index()

        return symbol_stats.sort_values("total_profit", ascending=False)

    def analyze_drawdown(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, float]:
        """Analyze account drawdown for a period.

        Args:
            date_from: Start date for analysis.
            date_to: End date for analysis.

        Returns:
            Dictionary with drawdown analysis.
        """
        deals_df = self.history_deals_get_as_df(date_from=date_from, date_to=date_to)

        if deals_df.empty:
            return {"max_drawdown": 0.0, "current_drawdown": 0.0}

        deals_df = deals_df.sort_values("time")
        deals_df["cumulative_profit"] = deals_df["profit"].cumsum()
        deals_df["running_max"] = deals_df["cumulative_profit"].cummax()
        deals_df["drawdown"] = deals_df["cumulative_profit"] - deals_df["running_max"]

        max_drawdown = deals_df["drawdown"].min()
        current_drawdown = deals_df["drawdown"].iloc[-1]

        return {
            "max_drawdown": max_drawdown,
            "current_drawdown": current_drawdown,
            "max_drawdown_percentage": (
                max_drawdown / deals_df["running_max"].max() * 100
            )
            if deals_df["running_max"].max() > 0
            else 0.0,
        }

    def get_daily_pnl(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> pd.DataFrame:
        """Get daily profit/loss summary.

        Args:
            date_from: Start date for analysis.
            date_to: End date for analysis.

        Returns:
            DataFrame with daily P&L indexed by date.
        """
        deals_df = self.history_deals_get_as_df(date_from=date_from, date_to=date_to)

        if deals_df.empty:
            return pd.DataFrame()

        deals_df = deals_df.copy()
        deals_df["date"] = deals_df["time"].dt.date

        daily_pnl = (
            deals_df.groupby("date")
            .agg({
                "profit": "sum",
                "ticket": "count",
            })
            .rename(columns={"ticket": "deal_count"})
        )

        daily_pnl["cumulative_pnl"] = daily_pnl["profit"].cumsum()

        return daily_pnl

    def validate_order_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate and check an order request before sending.

        Args:
            request: Order request parameters.

        Returns:
            Dictionary with validation results and order check.
        """
        required_fields = ["action", "symbol", "volume", "type"]
        missing_fields = [field for field in required_fields if field not in request]

        validation_result: dict[str, Any] = {
            "is_valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "warnings": [],
        }

        if validation_result["is_valid"]:
            try:
                order_check = self.order_check_as_dict(request)
                validation_result["order_check"] = order_check
                validation_result["margin_required"] = order_check.get("margin", 0.0)
                validation_result["profit_estimation"] = order_check.get("profit", 0.0)
            except Exception as e:  # noqa: BLE001
                validation_result["is_valid"] = False
                validation_result["error"] = str(e)

        if request.get("volume", 0) <= 0:
            validation_result["warnings"].append("Volume must be positive")  # type: ignore[attr-defined]

        return validation_result

    def get_risk_metrics(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, float]:
        """Calculate risk metrics for trading performance.

        Args:
            date_from: Start date for analysis.
            date_to: End date for analysis.

        Returns:
            Dictionary with risk metrics.
        """
        daily_pnl_df = self.get_daily_pnl(date_from=date_from, date_to=date_to)

        if daily_pnl_df.empty:
            return {"sharpe_ratio": 0.0, "sortino_ratio": 0.0, "volatility": 0.0}

        daily_returns = daily_pnl_df["profit"]
        mean_return = daily_returns.mean()
        volatility = daily_returns.std()

        downside_returns = daily_returns[daily_returns < 0]
        downside_volatility = (
            downside_returns.std() if len(downside_returns) > 0 else 0.0
        )

        sharpe_ratio = (mean_return / volatility) if volatility > 0 else 0.0
        sortino_ratio = (
            (mean_return / downside_volatility) if downside_volatility > 0 else 0.0
        )

        return {
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "volatility": volatility,
            "mean_daily_return": mean_return,
            "downside_volatility": downside_volatility,
            "positive_days": len(daily_returns[daily_returns > 0]),
            "negative_days": len(daily_returns[daily_returns < 0]),
        }
