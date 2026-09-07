import asyncio
from execution_agent import ExecutionAgent

async def main():
    # Inicializálás max. 100 db-os megbízási limit-tel
    agent = ExecutionAgent(client_id=2, max_quantity_per_order=100)
    try:
        # 1. Számlaadatok és Pozíciók ellenőrzése
        summary = await agent.get_account_summary()
        positions = await agent.get_positions()

        print("\n--- JELENLEGI POZÍCIÓK ---")
        if not positions:
            print(" - Nincs nyitott pozíció.")
        for pos in positions:
            print(f" - {pos['symbol']}: {pos['position']} db (Átlagár: {pos['avg_cost']} USD)")

        print("\n--- SZÁMLA ÖSSZEGZÉS ---")
        for key, val in summary.items():
            print(f" - {key}: {val} USD")

        # 2. TESZT: Normál vételi megbízás (1 db AAPL)
        print("\n--- TESZT 1: Normál megbízás (1 db AAPL) ---")
        trade1 = await agent.execute_order(symbol='AAPL', action='BUY', quantity=1, order_type='MKT')
        if trade1:
            print(f"Végrehajtott kötés ára: {trade1.orderStatus.avgFillPrice} USD")

        # 3. TESZT: Kockázatkezelés elutasítási teszt (150 db AAPL > max 100)
        print("\n--- TESZT 2: Kockázatkezelő teszt (150 db AAPL - Limit feletti) ---")
        trade2 = await agent.execute_order(symbol='AAPL', action='BUY', quantity=150, order_type='MKT')

    except Exception as e:
        print(f"Hiba történt: {e}")
    finally:
        await agent.disconnect()

if __name__ == '__main__':
    asyncio.run(main())