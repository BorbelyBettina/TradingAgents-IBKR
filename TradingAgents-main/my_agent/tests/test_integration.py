import asyncio
from my_agent.src.execution_agent import ExecutionAgent
from my_agent.src.trading_strategy import TradingStrategyEngine
from my_agent.src.logger import log_performance

async def main():
    agent = ExecutionAgent(client_id=2, max_quantity_per_order=100)
    engine = TradingStrategyEngine(execution_agent=agent)

    ai_signals = [
        {'symbol': 'AAPL', 'action': 'BUY', 'quantity': 1},
        {'symbol': 'MSFT', 'action': 'HOLD', 'quantity': 0},
        {'symbol': 'TSLA', 'action': 'BUY', 'quantity': 150}
    ]

    try:
        for signal in ai_signals:
            await engine.process_signal(signal)
            await asyncio.sleep(1)

    except Exception as e:
        print(f"Hiba az integrációs teszt során: {e}")

    finally:
        # A CSV mentést a finally ágban is meghívjuk, hogy mindenképpen lefusson
        print("CSV mentés tesztelése...")
        log_performance(total_cash=10000.0, net_liquidation=10500.0, open_positions_count=1)
        await agent.disconnect()

if __name__ == '__main__':
    asyncio.run(main())