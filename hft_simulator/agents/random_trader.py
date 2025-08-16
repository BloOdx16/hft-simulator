import random
from hft_simulator.agents.base_agent import TradingAgent
from hft_simulator.market.environment import MarketEnvironment
from config import RANDOM_TRADER_TRADE_CHANCE
from hft_simulator.utils.logger import setup_logger
from typing import Dict, Any

logger = setup_logger(__name__)

class RandomTrader(TradingAgent):
    """A trader that places random orders to simulate noise."""
    def update(self, market_data: Dict[str, Any]):
        if random.random() < RANDOM_TRADER_TRADE_CHANCE:
            side = random.choice(['BUY', 'SELL'])
            quantity = random.randint(1, 50)
            order_type = random.choice(['MARKET', 'LIMIT'])
            price = None
            if order_type == 'LIMIT':
                if side == 'BUY' and market_data['best_bid']:
                    price = round(market_data['best_bid'] * (1 - 0.001), 2)
                elif side == 'SELL' and market_data['best_ask']:
                    price = round(market_data['best_ask'] * (1 + 0.001), 2)
                else:
                    order_type = 'MARKET'
            
            logger.info(f"RandomTrader {self.agent_id} queuing a {side} {order_type} order for {quantity}.")
            self.place_order(order_type, side, quantity, price)


