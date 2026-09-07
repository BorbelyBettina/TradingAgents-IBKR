import asyncio
from execution_agent import ExecutionAgent

class TradingStrategyEngine:
    def __init__(self, execution_agent: ExecutionAgent):
        self.agent = execution_agent

    async def process_signal(self, signal: dict):
        """
        AI kereskedési jel feldolgozása és továbbítása az ExecutionAgent felé.
        
        :param signal: dict formátumú jel, pl.:
                       {'symbol': 'AAPL', 'action': 'BUY', 'quantity': 10}
        """
        symbol = signal.get('symbol')
        action = signal.get('action', '').upper()
        quantity = signal.get('quantity', 0)

        print(f"\n[StrategyEngine] Új AI jel érkezett: {action} {quantity} db {symbol}")

        if action == 'HOLD':
            print("[StrategyEngine] 'HOLD' jelzés, nincs teendő.")
            return None

        if action in ['BUY', 'SELL']:
            # Döntés átadása a végrehajtó ágensnek
            result = await self.agent.execute_order(
                symbol=symbol,
                action=action,
                quantity=quantity,
                order_type='MKT'
            )
            return result
        else:
            print(f"[StrategyEngine] Ismeretlen akció: {action}")
            return None