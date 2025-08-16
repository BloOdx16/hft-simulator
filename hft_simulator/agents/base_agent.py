from typing import Dict, Any, TYPE_CHECKING
from hft_simulator.market.environment import MarketEnvironment
from hft_simulator.core.order import Order, ORDER_TYPE, SIDE

if TYPE_CHECKING:
    from hft_simulator.market.environment import MarketEnvironment

class TradingAgent:
    """Base class for all trading agents, with PnL tracking."""
    def __init__(self, agent_id: str, market: 'MarketEnvironment'):
        self.agent_id: str = agent_id
        self.market: 'MarketEnvironment' = market
        self.position: int = 0
        self.initial_cash: float = 100000.0
        self.cash: float = self.initial_cash
        self.orders: Dict[str, 'Order'] = {}

    def place_order(self, order_type: 'ORDER_TYPE', side: 'SIDE', quantity: int, price: float | None = None):
        order = Order(self.agent_id, order_type, side, quantity, price)
        self.orders[order.order_id] = order
        self.market.handle_order(order)

    def cancel_order(self, order_id: str):
        if order_id in self.orders:
            self.market.order_book.cancel_order(order_id)
            del self.orders[order_id]

    def record_trade(self, price: float, quantity: int, side: 'SIDE'):
        """Updates cash and position based on a confirmed trade."""
        if side == 'BUY':
            self.cash -= price * quantity
            self.position += quantity
        else: # SELL
            self.cash += price * quantity
            self.position -= quantity

    def update(self, market_data: Dict[str, Any]):
        raise NotImplementedError