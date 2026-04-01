

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceAlertResult:
    """监测结果。"""

    hit_profit: bool
    hit_loss: bool
    pnl_percent: float


def check_price_threshold(
    cost_price: float,
    current_price: float,
    profit_ratio: float,
    loss_ratio: float,
) -> PriceAlertResult:
    """
    判断当前价是否达到止盈或止损比例。

    参数说明：
    - cost_price: 成本价，必须大于 0
    - current_price: 当前价格
    - profit_ratio: 止盈比例（百分比，正数；例如 10 表示 +10%）
    - loss_ratio: 止损比例（百分比，正数；例如 5 表示 -5%）
    """
    if cost_price <= 0:
        raise ValueError("cost_price 必须大于 0")
    if profit_ratio < 0 or loss_ratio < 0:
        raise ValueError("profit_ratio 和 loss_ratio 必须为非负数")

    pnl_percent = (current_price - cost_price) / cost_price * 100.0
    hit_profit = pnl_percent >= profit_ratio
    hit_loss = pnl_percent <= -loss_ratio

    return PriceAlertResult(
        hit_profit=hit_profit,
        hit_loss=hit_loss,
        pnl_percent=pnl_percent,
    )


if __name__ == "__main__":
    result = check_price_threshold(
        cost_price=100.0,
        current_price=112.0,
        profit_ratio=10.0,
        loss_ratio=5.0,
    )
    print(result)
