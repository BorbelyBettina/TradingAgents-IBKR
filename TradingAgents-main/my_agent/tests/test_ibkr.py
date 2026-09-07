import asyncio
from ib_async import *

async def main():
    ib = IB()
    try:
        # Csatlakozás a TWS-hez
        await ib.connectAsync('127.0.0.1', 7497, clientId=1)
        print("\n>>> SIKERES CSATLAKOZÁS AZ IBKR PAPER TRADING FIÓKHOZ! <<<\n")

        # Apple (AAPL) részvény kiválasztása
        contract = Stock('AAPL', 'SMART', 'USD')
        await ib.qualifyContractsAsync(contract)

        # Történeti adatok lekérése (az elmúlt 1 nap, 1 órás gyertyákkal)
        bars = await ib.reqHistoricalDataAsync(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 hour',
            whatToShow='TRADES',
            useRTH=True
        )

        if bars:
            print("AAPL legutóbbi órás árfolyam-adatai:")
            latest_bar = bars[-1]
            print(f" - Időpont: {latest_bar.date}")
            print(f" - Nyitó ár: {latest_bar.open} USD")
            print(f" - Legmagasabb ár: {latest_bar.high} USD")
            print(f" - Legalacsonyabb ár: {latest_bar.low} USD")
            print(f" - Záró ár: {latest_bar.close} USD")
            print(f" - Forgalom (kötésszám): {latest_bar.volume}")
        else:
            print("Nem érkeztek történeti adatok.")

    except Exception as e:
        print(f"\nHiba történt: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nKapcsolat bontva.")

if __name__ == '__main__':
    asyncio.run(main())