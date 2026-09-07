import asyncio
import os
from dotenv import load_dotenv
from my_agent.src.execution_agent import ExecutionAgent
from my_agent.src.trading_strategy import TradingStrategyEngine
from my_agent.src.logger import log_info, log_error, log_performance

load_dotenv()

async def fetch_llm_signal():
    """Minta AI jelzés az integrációs teszteléshez."""
    return {'symbol': 'AAPL', 'action': 'BUY', 'quantity': 1}

async def run_trading_cycle(engine: TradingStrategyEngine, agent: ExecutionAgent):
    """Egyetlen kereskedési ciklus végrehajtása."""
    try:
        log_info("--- ÚJ KERESKEDÉSI CIKLUS INDÍTÁSA ---")
        
        signal = await fetch_llm_signal()
        log_info(f"AI Elemzés kimenete: {signal}")
        
        await engine.process_signal(signal)
        
        summary = await agent.get_account_summary()
        positions = await agent.get_positions()
        
        total_cash = float(summary.get('TotalCashBalance', 0.0))
        net_liq = float(summary.get('NetLiquidation', 0.0))
        open_positions_count = len(positions)
        
        log_performance(total_cash=total_cash, net_liquidation=net_liq, open_positions_count=open_positions_count)
        
    except Exception as e:
        log_error(f"Hiba a kereskedési ciklus során: {e}")

async def main():
    agent = ExecutionAgent(client_id=1, max_quantity_per_order=100)
    engine = TradingStrategyEngine(execution_agent=agent)
    
    INTERVAL_SECONDS = 3600 
    
    try:
        while True:
            await run_trading_cycle(engine, agent)
            log_info(f"Várakozás a következő ciklusig ({INTERVAL_SECONDS} mp)...")
            await asyncio.sleep(INTERVAL_SECONDS)
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        log_info("A főciklus manuálisan leállítva.")
    finally:
        await agent.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass