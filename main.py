import time
from hft_simulator.market.environment import MarketEnvironment
from hft_simulator.agents.random_trader import RandomTrader
from hft_simulator.agents.stoikov_market_maker import StoikovMarketMaker
from hft_simulator.agents.latency_arbitrage_trader import LatencyArbitrageTrader
from config import SIMULATION_DURATION_SECONDS, ORDER_ARRIVAL_RATE
from hft_simulator.utils.logger import setup_logger

logger = setup_logger(__name__)

class Simulator:
    """Orchestrates the simulation and reports final PnL for each agent."""
    def __init__(self):
        # Agent list must be defined before the agent map
        self.agents = [
            RandomTrader("RT1", None),
            RandomTrader("RT2", None),
            StoikovMarketMaker("StoikovMM1", None),
            LatencyArbitrageTrader("Arb1", None),
        ]
        # Agent map for easy lookup by the market environment
        self.agent_map = {agent.agent_id: agent for agent in self.agents}
        
        self.market = MarketEnvironment(self.agent_map)
        
        # Now assign the market to each agent
        for agent in self.agents:
            agent.market = self.market
        
        self.duration = SIMULATION_DURATION_SECONDS

    def run(self):
        """
        Runs the main simulation loop and calculates PnL at the end.
        """
        start_time = time.time()
        logger.info("--- Starting HFT Simulation ---")
        while time.time() - start_time < self.duration:
            market_data = self.market.get_market_data()
            bbo_info = (f"Best Bid: {market_data['best_bid']:.2f}, Best Ask: {market_data['best_ask']:.2f}"
                        if market_data['best_bid'] and market_data['best_ask'] else "BBO: Not available")
            logger.info(f"--- Market Tick | Last Price: {market_data['last_price']:.2f} | {bbo_info} ---")

            # Agents place orders into the inbound queue
            for agent in self.agents:
                try:
                    agent.update(market_data)
                except Exception as e:
                    logger.error(f"Error updating agent {agent.agent_id}: {e}", exc_info=True)

            # Market processes the queue and matches orders
            self.market.process_inbound_queue()
            self.market.match_orders()

            try:
                time.sleep(1 / ORDER_ARRIVAL_RATE)
            except ZeroDivisionError:
                time.sleep(1)

        logger.info("--- Simulation Ended ---")
        self.report_pnl()

    def report_pnl(self):
        """Calculates and logs the final PnL for each agent."""
        logger.info("--- Final Profit and Loss Report ---")
        last_price = self.market.last_price
        
        for agent in self.agents:
            # Mark-to-market PnL = Realized PnL (cash change) + Unrealized PnL (inventory value)
            unrealized_pnl = agent.position * last_price
            realized_pnl = agent.cash - agent.initial_cash
            total_pnl = realized_pnl + unrealized_pnl
            
            logger.info(
                f"Agent: {agent.agent_id:<12} | "
                f"Total PnL: ${total_pnl:8.2f} | "
                f"Final Position: {agent.position:<4} | "
                f"Cash Change: ${realized_pnl:8.2f}"
            )
        logger.info(f"Total Trades Executed: {len(self.market.trade_history)}")


if __name__ == '__main__':
    simulator = Simulator()
    simulator.run()

