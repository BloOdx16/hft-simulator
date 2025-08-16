import logging

# --- Simulation Configuration ---
SIMULATION_DURATION_SECONDS: int = 20
ORDER_ARRIVAL_RATE: float = 5.0  # Increased for more opportunities
LATENCY_MS: int = 2  # Milliseconds

# --- Market Configuration ---
INITIAL_PRICE: float = 100.00
MARKET_VOLATILITY: float = 0.05  # Standard deviation of price changes

# --- Agent Configuration ---
# Random Trader
RANDOM_TRADER_TRADE_CHANCE: float = 0.6

# Stoikov Market Maker
STOIKOV_RISK_AVERSION: float = 0.01  # Gamma (γ) parameter
STOIKOV_ORDER_BOOK_DENSITY: float = 1.5 # Kappa (κ) parameter
STOIKOV_ORDER_QUANTITY: int = 5

# Latency Arbitrage Trader
LATENCY_ARBITRAGE_THRESHOLD: int = 30 # Min order size to front-run
LATENCY_ARBITRAGE_QUANTITY: int = 2 # Size of the arbitrage order

# --- Logging Configuration ---
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'