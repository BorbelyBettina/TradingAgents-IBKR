import csv
import logging
import os
from pathlib import Path
from datetime import datetime

# Abszolút útvonal meghatározása a Path használatával
# __file__ -> .../my_agent/src/logger.py
# .parent -> .../my_agent/src
# .parent.parent -> .../my_agent
MY_AGENT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = MY_AGENT_DIR / "logs"

# Hozzuk létre a mappát abszolút útvonalon, ha nem létezik
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "trading.log"
CSV_FILE = LOG_DIR / "daily_performance.csv"

# --- LOGGING BEÁLLÍTÁSA ---
logger = logging.getLogger("TradingAgent")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Töröljük a korábbi handler-eket, ha voltak, a duplikáció elkerülése miatt
if logger.hasHandlers():
    logger.handlers.clear()

# Fájlba író handler (kifejezetten az abszolút str(LOG_FILE) útvonalra!)
file_handler = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
file_handler.setFormatter(formatter)

# Konzolra író handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log_info(msg: str):
    logger.info(msg)

def log_warning(msg: str):
    logger.warning(msg)

def log_error(msg: str):
    logger.error(msg)

# --- CSV PERFORMANCE DATA LOGGING ---
def log_performance(total_cash: float, net_liquidation: float, open_positions_count: int):
    """Elmenti a számla pillanatnyi állapotát CSV fájlba a szakdolgozati mérésekhez."""
    file_exists = CSV_FILE.exists()
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp', 'total_cash', 'net_liquidation', 'open_positions'])
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, total_cash, net_liquidation, open_positions_count])
        file.flush() # Azonnali lemezre írás kikényszerítése