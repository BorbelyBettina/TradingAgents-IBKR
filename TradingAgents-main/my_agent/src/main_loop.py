import asyncio
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from my_agent.src.execution_agent import ExecutionAgent
from my_agent.src.trading_strategy import TradingStrategyEngine
from my_agent.src.logger import log_info, log_error, log_performance

load_dotenv()

# A projekt gyökérmappájának (TradingAgents-main) hozzáadása a rendszerútvonalakhoz
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]  # TradingAgents-main könyvtár

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

async def fetch_llm_signal(symbol: str = "AAPL") -> dict:
    """
    Meghívja a TauricResearch / TradingAgents elemző pipeline-ját interaktív bekérés nélkül,
    OpenAI API használatával, majd feldolgozza a kimenetet a kereskedési architektúra számára.
    """
    try:
        log_info(f"LLM Elemzés indítása a következő szimbólumra: {symbol} (OpenAI)...")
        
        # A modulok importálása a cli-ből
        from cli.main import _build_run_config, StatsCallbackHandler, ANALYST_ORDER
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # Konfiguráció beállítása
        default_selections = {
            "ticker": symbol,
            "analysts": ["market_analyst", "fundamentals_analyst", "technical_analyst"],
            "research_depth": "shallow",
            "llm_provider": "openai",
            "shallow_thinker": "gpt-4o-mini",
            "deep_thinker": "gpt-4o",
            "backend_url": "https://api.openai.com/v1",
            "start_date": "",
            "end_date": "",
            "interval": "1d"
        }

        # Konfiguráció felépítése
        config = _build_run_config(default_selections, checkpoint=False)
        stats_handler = StatsCallbackHandler()

        # Elemző gráf inicializálása
        graph = TradingAgentsGraph(config=config, callbacks=[stats_handler])
        
        # Mai dátum lekérése formázva (YYYY-MM-DD)
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Futtatás a wrapper hivatalos propagate() metódusával
        analysis_result = await asyncio.to_thread(
            graph.propagate,
            company_name=symbol,
            trade_date=today_str
        )
        
        if isinstance(analysis_result, dict):
            action = analysis_result.get("action", analysis_result.get("decision", "HOLD")).upper()
            quantity = int(analysis_result.get("quantity", 1))
        else:
            action = "HOLD"
            quantity = 0

        return {
            "symbol": symbol,
            "action": action,
            "quantity": quantity
        }
        
    except Exception as e:
        log_error(f"Hiba az LLM szignál lekérése során: {e}")
        traceback.print_exc()
        return {"symbol": symbol, "action": "HOLD", "quantity": 0}

async def run_trading_cycle(engine: TradingStrategyEngine, agent: ExecutionAgent):
    """Egyetlen kereskedési ciklus végrehajtása."""
    try:
        log_info("--- ÚJ KERESKEDÉSI CIKLUS INDÍTÁSA ---")
        
        signal = await fetch_llm_signal("AAPL")
        log_info(f"AI Elemzés kimenete: {signal}")
        
        if signal.get("action") != "HOLD" and signal.get("quantity", 0) > 0:
            await engine.process_signal(signal)
        else:
            log_info("A kapott jelzés HOLD vagy 0 mennyiség, nincs megbízás-küldés.")
        
        summary = await agent.get_account_summary()
        positions = await agent.get_positions()
        
        total_cash = float(summary.get('TotalCashBalance', 0.0))
        net_liq = float(summary.get('NetLiquidation', 0.0))
        open_positions_count = len(positions)
        
        log_performance(total_cash=total_cash, net_liquidation=net_liq, open_positions_count=open_positions_count)
        
    except Exception as e:
        log_error(f"Hiba a kereskedési ciklus során: {e}")
        traceback.print_exc()

async def main():
    agent = ExecutionAgent(client_id=1, max_quantity_per_order=100)
    engine = TradingStrategyEngine(execution_agent=agent)
    
    # 15 perces ciklusidő (900 mp)
    INTERVAL_SECONDS = 900 
    
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