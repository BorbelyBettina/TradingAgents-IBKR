import asyncio
from ib_async import *
from my_agent.src.logger import log_info, log_warning, log_error, log_performance

class ExecutionAgent:
    def __init__(self, host='127.0.0.1', port=7497, client_id=2, max_quantity_per_order=100):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.max_quantity_per_order = max_quantity_per_order
        self.ib = IB()

    async def connect(self):
        """Csatlakozás az IBKR TWS / Gateway felületéhez automatikus újracsatlakozással."""
        if not self.ib.isConnected():
            try:
                await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)
                log_info("[ExecutionAgent] Sikeresen csatlakozva az IBKR-hez.")
            except Exception as e:
                log_error(f"[ExecutionAgent] Csatlakozási hiba: {e}")
                raise e

    async def disconnect(self):
        """Kapcsolat bontása."""
        if self.ib.isConnected():
            self.ib.disconnect()
            log_info("[ExecutionAgent] Kapcsolat bontva.")

    async def get_positions(self):
        """A számlán meglévő nyitott pozíciók lekérdezése."""
        await self.connect()
        positions = await self.ib.reqPositionsAsync()
        pos_list = []
        for p in positions:
            pos_list.append({
                'symbol': p.contract.symbol,
                'position': p.position,
                'avg_cost': p.avgCost
            })
        return pos_list

    async def get_account_summary(self):
        """Számlaegyenleg és szabad tőke lekérdezése."""
        await self.connect()
        summary = await self.ib.accountSummaryAsync()
        account_data = {}
        for item in summary:
            if item.tag in ['TotalCashValue', 'BuyingPower', 'NetLiquidation']:
                account_data[item.tag] = float(item.value)
        return account_data

    async def record_daily_metrics(self):
        """Adatgyűjtés a szakdolgozati teljesítménygrafikonokhoz."""
        summary = await self.get_account_summary()
        positions = await self.get_positions()
        
        cash = summary.get('TotalCashValue', 0.0)
        net_liq = summary.get('NetLiquidation', 0.0)
        pos_count = len(positions)
        
        log_performance(cash, net_liq, pos_count)

    async def execute_order(self, symbol: str, action: str, quantity: int, order_type: str = 'MKT', limit_price: float = None):
        """Megbízás ellenőrzése és végrehajtása kockázatkezelési szabályokkal."""
        await self.connect()

        # KOCKÁZATKEZELÉS 1: Maximális darabszám
        if quantity > self.max_quantity_per_order:
            log_warning(f"[Risk Check REJECTED] A kért mennyiség ({quantity} db) meghaladja a limitet ({self.max_quantity_per_order} db)!")
            return None

        contract = Stock(symbol, 'SMART', 'USD')
        await self.ib.qualifyContractsAsync(contract)

        # Nyitvatartáson kívüli MKT -> LMT konverzió
        if order_type.upper() == 'MKT' and limit_price is None:
            ticker = self.ib.reqMktData(contract)
            await asyncio.sleep(1)
            price = ticker.close or ticker.last or ticker.marketPrice()
            
            if not price or price != price:
                bars = await self.ib.reqHistoricalDataAsync(
                    contract, endDateTime='', durationStr='1 D',
                    barSizeSetting='1 hour', whatToShow='TRADES', useRTH=True
                )
                if bars:
                    price = bars[-1].close

            limit_price = round(price, 2)
            order_type = 'LMT'
            log_info(f"[ExecutionAgent] Nyitvatartáson kívüli megbízás LMT típusra módosítva ({limit_price} USD áron).")

        # KOCKÁZATKEZELÉS 2: Fedezet
        if action.upper() == 'BUY':
            summary = await self.get_account_summary()
            available_cash = summary.get('TotalCashValue', 0.0)
            estimated_cost = quantity * (limit_price if limit_price else 0.0)

            if estimated_cost > available_cash:
                log_warning(f"[Risk Check REJECTED] Nincs elegendő fedezet! Szükséges: {estimated_cost:.2f} USD, Elérhető: {available_cash:.2f} USD.")
                return None

        if order_type.upper() == 'LMT':
            order = LimitOrder(action.upper(), quantity, limit_price)
            order.outsideRth = True
            order.tif = 'GTC'
        else:
            order = MarketOrder(action.upper(), quantity)

        log_info(f"[ExecutionAgent] Megbízás küldése: {action} {quantity} db {symbol} ({order_type} @ {limit_price if limit_price else 'MKT'})...")
        trade = self.ib.placeOrder(contract, order)

        await asyncio.sleep(2)

        log_info(f"[ExecutionAgent] Megbízás állapota: {trade.orderStatus.status}")
        return trade