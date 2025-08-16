from hft_simulator.agents.base_agent import TradingAgent
from hft_simulator.market.environment import MarketEnvironment
from config import LATENCY_ARBITRAGE_THRESHOLD, LATENCY_ARBITRAGE_QUANTITY
from hft_simulator.utils.logger import setup_logger
from typing import Dict, Any

logger = setup_logger(__name__)

class LatencyArbitrageTrader(TradingAgent):
    """
    An agent that attempts to front-run large market orders.
    """
    def __init__(self, agent_id: str, market: MarketEnvironment):
        super().__init__(agent_id, market)
        self.large_order_threshold = LATENCY_ARBITRAGE_THRESHOLD
        self.arbitrage_quantity = LATENCY_ARBITRAGE_QUANTITY
        self.in_arbitrage_position = False

    def update(self, market_data: Dict[str, Any]):
        if self.in_arbitrage_position:
            side_to_close = 'SELL' if self.position > 0 else 'BUY'
            logger.info(f"LATENCY_ARB ({self.agent_id}): Exiting position.")
            self.place_order('MARKET', side_to_close, abs(self.position))
            self.in_arbitrage_position = False
            return

        if self.position == 0:
            inbound_orders = self.market.peek_inbound_queue()
            for order in inbound_orders:
                if (order.order_type == 'MARKET' and
                        order.quantity >= self.large_order_threshold and
                        order.agent_id != self.agent_id):
                    
                    logger.warning(f"LATENCY_ARB ({self.agent_id}): Detected large inbound {order.side} "
                                 f"order for {order.quantity}. Front-running!")
                    
                    self.place_order('MARKET', order.side, self.arbitrage_quantity)
                    self.in_arbitrage_position = True
                    return

