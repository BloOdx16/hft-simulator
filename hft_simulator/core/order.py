import time
import uuid
from typing import Literal

SIDE = Literal['BUY', 'SELL']
ORDER_TYPE = Literal['LIMIT', 'MARKET']

class Order:
    """
    Represents an order in the order book with detailed attributes.
    """
    def __init__(self,
                 agent_id: str,
                 order_type: ORDER_TYPE,
                 side: SIDE,
                 quantity: int,
                 price: float | None = None):
        if order_type == 'LIMIT' and price is None:
            raise ValueError("Limit orders must have a price.")
        self.order_id: str = str(uuid.uuid4())
        self.agent_id: str = agent_id
        self.order_type: ORDER_TYPE = order_type
        self.side: SIDE = side
        self.quantity: int = quantity
        self.price: float | None = price
        self.timestamp: float = time.time()

    def __lt__(self, other: 'Order') -> bool:
        if self.price == other.price:
            return self.timestamp < other.timestamp
        if self.side == 'BUY':
            return self.price > other.price
        else:  # SELL
            return self.price < other.price

    def __repr__(self) -> str:
        return (f"Order(id={self.order_id}, agent={self.agent_id}, "
                f"type={self.order_type}, side={self.side}, "
                f"qty={self.quantity}, price={self.price})")
