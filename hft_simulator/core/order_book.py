import heapq
from typing import List, Dict, Tuple
from hft_simulator.core.order import Order

class OrderBook:
    """
    Manages the limit order book for a single asset using heaps for efficiency.
    """
    def __init__(self):
        self.bids: List[Tuple[float, Order]] = []
        self.asks: List[Tuple[float, Order]] = []
        self.orders: Dict[str, Order] = {}

    def add_order(self, order: Order) -> None:
        if order.order_type != 'LIMIT' or order.price is None:
            return
        self.orders[order.order_id] = order
        if order.side == 'BUY':
            heapq.heappush(self.bids, (-order.price, order))
        else:
            heapq.heappush(self.asks, (order.price, order))

    def cancel_order(self, order_id: str) -> None:
        if order_id in self.orders:
            self.orders[order_id].quantity = 0
            del self.orders[order_id]

    def _clean_stale_orders(self, heap: List[Tuple[float, Order]]) -> None:
        while heap and heap[0][1].quantity == 0:
            heapq.heappop(heap)

    def get_best_bid(self) -> float | None:
        self._clean_stale_orders(self.bids)
        return -self.bids[0][0] if self.bids else None

    def get_best_ask(self) -> float | None:
        self._clean_stale_orders(self.asks)
        return self.asks[0][0] if self.asks else None