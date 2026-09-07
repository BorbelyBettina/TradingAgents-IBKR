import asyncio
from execution_agent import ExecutionAgent

async def main():
    agent = ExecutionAgent(client_id=2)
    try:
        # 1. Számlaadatok ellenőrzése
        summary = await agent.get_account_summary()
        print("\n--- SZÁMLA ÖSSZEGZÉS ---")
        for key, val in summary.items():
            print(f" - {key}: {val} USD")

        # 2. Vételi teszt (1 db AAPL részvény vásárlása piaci áron)
        # Figyelem: Paper Trading fiókban hajtódik végre!
        print("\n--- TESZT MEGBÍZÁS ---")
        trade = await agent.execute_order(symbol='AAPL', action='BUY', quantity=1, order_type='MKT')
        print(f"Végrehajtott kötés ára: {trade.orderStatus.avgFillPrice} USD")

    except Exception as e:
        print(f"Hiba történt: {e}")
    finally:
        await agent.disconnect()

if __name__ == '__main__':
    asyncio.run(main())