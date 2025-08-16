import time
import collections
from typing import List, Dict, Any, Deque
from hft_simulator.core.order import Order
from hft_simulator.core.order_book import OrderBook
from config import LATENCY_MS, INITIAL_PRICE
from hft_simulator.utils.logger import setup_logger

logger = setup_logger(__name__)

class MarketEnvironment:
    """
    Simulates the market, including an inbound order queue for latency effects.
    """
    def __init__(self, agents: Dict[str, Any]):
        self.order_book = OrderBook()
        self.trade_history: List[Dict[str, Any]] = []
        self.last_price: float = INITIAL_PRICE
        self.latency: float = LATENCY_MS / 1000.0
        self.inbound_queue: Deque[Order] = collections.deque()
        self.agents = agents

    def handle_order(self, order: Order) -> None:
        """Adds an incoming order to the inbound queue instead of processing immediately."""
        self.inbound_queue.append(order)

    def peek_inbound_queue(self) -> List[Order]:
        """Allows an agent to see the pending orders without processing them."""
        return list(self.inbound_queue)

    def process_inbound_queue(self) -> None:
        """Processes all orders in the queue, applying latency."""
        orders_to_process = len(self.inbound_queue)
        for _ in range(orders_to_process):
            order = self.inbound_queue.popleft()
            time.sleep(self.latency)
            if order.order_type == 'LIMIT':
                self.order_book.add_order(order)
            elif order.order_type == 'MARKET':
                self._execute_market_order(order)

    def match_orders(self) -> None:
        while self.order_book.bids and self.order_book.asks:
            self.order_book._clean_stale_orders(self.order_book.bids)
            self.order_book._clean_stale_orders(self.order_book.asks)
            if not self.order_book.bids or not self.order_book.asks: break
            
            best_bid_price = -self.order_book.bids[0][0]
            best_ask_price = self.order_book.asks[0][0]
            if best_bid_price < best_ask_price: break

            buy_order = self.order_book.bids[0][1]
            sell_order = self.order_book.asks[0][1]
            trade_quantity = min(buy_order.quantity, sell_order.quantity)
            trade_price = buy_order.price if buy_order.timestamp < sell_order.timestamp else sell_order.price

            trade = {'price': trade_price, 'quantity': trade_quantity, 'time': time.time(),
                     'buy_agent_id': buy_order.agent_id, 'sell_agent_id': sell_order.agent_id}
            self.trade_history.append(trade)
            self.last_price = trade_price
            logger.info(f"TRADE: {trade_quantity} shares at {trade_price:.2f}")

            # Notify agents of the trade
            self.agents[buy_order.agent_id].record_trade(trade_price, trade_quantity, 'BUY')
            self.agents[sell_order.agent_id].record_trade(trade_price, trade_quantity, 'SELL')

            buy_order.quantity -= trade_quantity
            sell_order.quantity -= trade_quantity

    def _execute_market_order(self, order: Order) -> None:
        filled_quantity = 0
        aggressing_agent = self.agents[order.agent_id]
        
        if order.side == 'BUY':
            heap = self.order_book.asks
            while order.quantity > 0 and heap:
                self.order_book._clean_stale_orders(heap)
                if not heap: break
                resting_order = heap[0][1]
                resting_agent = self.agents[resting_order.agent_id]
                trade_quantity = min(order.quantity, resting_order.quantity)
                trade_price = resting_order.price
                
                self.last_price = trade_price
                filled_quantity += trade_quantity
                
                # Notify both agents
                aggressing_agent.record_trade(trade_price, trade_quantity, 'BUY')
                resting_agent.record_trade(trade_price, trade_quantity, 'SELL')

                resting_order.quantity -= trade_quantity
                order.quantity -= trade_quantity
        else:  # SELL
            heap = self.order_book.bids
            while order.quantity > 0 and heap:
                self.order_book._clean_stale_orders(heap)
                if not heap: break
                resting_order = heap[0][1]
                resting_agent = self.agents[resting_order.agent_id]
                trade_quantity = min(order.quantity, resting_order.quantity)
                trade_price = resting_order.price
                
                self.last_price = trade_price
                filled_quantity += trade_quantity

                # Notify both agents
                aggressing_agent.record_trade(trade_price, trade_quantity, 'SELL')
                resting_agent.record_trade(trade_price, trade_quantity, 'BUY')

                resting_order.quantity -= trade_quantity
                order.quantity -= trade_quantity
        
        if filled_quantity > 0:
            logger.info(f"Market {order.side} of {filled_quantity} for {order.agent_id} filled.")

    def get_market_data(self) -> Dict[str, Any]:
        return {'best_bid': self.order_book.get_best_bid(), 'best_ask': self.order_book.get_best_ask(),
                'last_price': self.last_price}
