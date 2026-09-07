import asyncio
from execution_agent import ExecutionAgent
from trading_strategy import TradingStrategyEngine

async def main():
    agent = ExecutionAgent(client_id=2, max_quantity_per_order=100)
    engine = TradingStrategyEngine(execution_agent=agent)

    # Szimulált AI kereskedési jelek sorozata
    ai_signals = [
        {'symbol': 'AAPL', 'action': 'BUY', 'quantity': 1},
        {'symbol': 'MSFT', 'action': 'HOLD', 'quantity': 0},
        {'symbol': 'TSLA', 'action': 'BUY', 'quantity': 150}  # Kockázatkezelő által elutasítandó
    ]

    try:
        for signal in ai_signals:
            await engine.process_signal(signal)
            await asyncio.sleep(1)

    except Exception as e:
        print(f"Hiba az integrációs teszt során: {e}")
    finally:
        await agent.disconnect()

if __name__ == '__main__':
    asyncio.run(main())