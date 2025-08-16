import math
from hft_simulator.agents.base_agent import TradingAgent
from hft_simulator.market.environment import MarketEnvironment
from config import STOIKOV_RISK_AVERSION, STOIKOV_ORDER_BOOK_DENSITY, MARKET_VOLATILITY, SIMULATION_DURATION_SECONDS, STOIKOV_ORDER_QUANTITY
from hft_simulator.utils.logger import setup_logger
from typing import Dict, Any
import time
from hft_simulator.utils.logger import setup_logger

logger = setup_logger(__name__)

class StoikovMarketMaker(TradingAgent):
    """
    Implements the Avellaneda-Stoikov market-making model.
    """
    def __init__(self, agent_id: str, market: MarketEnvironment):
        super().__init__(agent_id, market)
        self.risk_aversion: float = STOIKOV_RISK_AVERSION
        self.kappa: float = STOIKOV_ORDER_BOOK_DENSITY
        self.sigma_sq: float = MARKET_VOLATILITY ** 2
        self.session_duration: int = SIMULATION_DURATION_SECONDS
        self.start_time: float = time.time()
        self.order_quantity: int = STOIKOV_ORDER_QUANTITY

    def update(self, market_data: Dict[str, Any]):
        for order_id in list(self.orders.keys()):
            self.cancel_order(order_id)

        time_remaining = self.session_duration - (time.time() - self.start_time)
        if time_remaining <= 0:
            if self.position != 0:
                logger.info(f"Stoikov agent {self.agent_id} session ended. Liquidating position.")
                side = 'SELL' if self.position > 0 else 'BUY'
                self.place_order('MARKET', side, abs(self.position))
            return

        mid_price = self.market.last_price
        reservation_price = mid_price - self.position * self.risk_aversion * self.sigma_sq * time_remaining
        term_1 = self.risk_aversion * self.sigma_sq * time_remaining
        term_2 = (2 / self.risk_aversion) * math.log(1 + (self.risk_aversion / self.kappa))
        optimal_spread = term_1 + term_2
        buy_price = round(reservation_price - optimal_spread / 2, 2)
        sell_price = round(reservation_price + optimal_spread / 2, 2)

        if buy_price < sell_price:
            self.place_order('LIMIT', 'BUY', self.order_quantity, buy_price)
            self.place_order('LIMIT', 'SELL', self.order_quantity, sell_price)
            logger.info(f"StoikovMM {self.agent_id} (Inv: {self.position}): "
                        f"Res Price: {reservation_price:.2f}, Quote: {buy_price} @ {sell_price}")
        else:
            logger.warning(f"StoikovMM {self.agent_id} quote crossed. No orders placed.")



