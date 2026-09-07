import asyncio
from ib_async import *

class ExecutionAgent:
    def __init__(self, host='127.0.0.1', port=7497, client_id=2):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()

    async def connect(self):
        """Csatlakozás az IBKR TWS / Gateway felületéhez."""
        if not self.ib.isConnected():
            await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)
            print("[ExecutionAgent] Sikeresen csatlakozva az IBKR-hez.")

    async def disconnect(self):
        """Kapcsolat bontása."""
        if self.ib.isConnected():
            self.ib.disconnect()
            print("[ExecutionAgent] Kapcsolat bontva.")

    async def get_account_summary(self):
        """Számlaegyenleg és szabad tőke lekérdezése."""
        await self.connect()
        summary = await self.ib.accountSummaryAsync()
        account_data = {}
        for item in summary:
            if item.tag in ['TotalCashValue', 'BuyingPower', 'NetLiquidation']:
                account_data[item.tag] = float(item.value)
        return account_data

    async def execute_order(self, symbol: str, action: str, quantity: int, order_type: str = 'MKT', limit_price: float = None):
        """
        Megbízás végrehajtása.
        
        :param symbol: Részvény ticker (pl. 'AAPL')
        :param action: 'BUY' vagy 'SELL'
        :param quantity: Darabszám
        :param order_type: 'MKT' (Market) vagy 'LMT' (Limit)
        :param limit_price: Limit ár (ha nincs megadva, automatikusan lekéri az utolsó árat)
        """
        await self.connect()

        contract = Stock(symbol, 'SMART', 'USD')
        await self.ib.qualifyContractsAsync(contract)

        # Ha nyitvatartáson kívül küldünk MKT megbízást, átváltjuk LMT-re az utolsó ismert áron
        if order_type.upper() == 'MKT' and limit_price is None:
            ticker = self.ib.reqMktData(contract)
            await asyncio.sleep(1)
            price = ticker.close or ticker.last or ticker.marketPrice()
            
            # Ha nincsenek élő adatfolyamok, lekérjük a legutóbbi órás záróárat
            if not price or price != price:  # NaN ellenőrzés
                bars = await self.ib.reqHistoricalDataAsync(
                    contract, endDateTime='', durationStr='1 D',
                    barSizeSetting='1 hour', whatToShow='TRADES', useRTH=True
                )
                if bars:
                    price = bars[-1].close

            limit_price = round(price, 2)
            order_type = 'LMT'
            print(f"[ExecutionAgent] Nyitvatartáson kívüli megbízás LMT típusra módosítva ({limit_price} USD áron).")

        # Megbízás objektum összeállítása
        if order_type.upper() == 'LMT':
            order = LimitOrder(action.upper(), quantity, limit_price)
            order.outsideRth = True
            order.tif = 'GTC'
        else:
            order = MarketOrder(action.upper(), quantity)

        print(f"[ExecutionAgent] Megbízás küldése: {action} {quantity} db {symbol} ({order_type} @ {limit_price if limit_price else 'MKT'})...")
        trade = self.ib.placeOrder(contract, order)

        # Várakozás a megbízás elküldésére és visszaigazolására
        await asyncio.sleep(2)

        print(f"[ExecutionAgent] Megbízás állapota: {trade.orderStatus.status}")
        return trade