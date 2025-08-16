from hft_simulator.agents.base_agent import TradingAgent
from hft_simulator.market.environment import MarketEnvironment
from hft_simulator.utils.logger import setup_logger
from typing import Dict, Any

logger = setup_logger(__name__)
class MarketMaker(TradingAgent):
    def __init__(self, agent_id: str, market: MarketEnvironment, spread: float, order_quantity: int):
        super().__init__(agent_id, market)
        self.spread = spread
        self.order_quantity = order_quantity
    def update(self, market_data: Dict[str, Any]):
        for order_id in list(self.orders.keys()): self.cancel_order(order_id)
        mid_price = self.market.last_price
        buy_price = round(mid_price - self.spread / 2, 2)
        sell_price = round(mid_price + self.spread / 2, 2)
        self.place_order('LIMIT', 'BUY', self.order_quantity, buy_price)
        self.place_order('LIMIT', 'SELL', self.order_quantity, sell_price)
        logger.debug(f"MarketMaker {self.agent_id} quoted: Bid @ {buy_price}, Ask @ {sell_price}")

