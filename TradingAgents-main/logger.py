import logging
import csv
import os
from datetime import datetime

# --- LOGGING BEÁLLÍTÁSA ---
logger = logging.getLogger("TradingAgent")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Fájlba író handler
file_handler = logging.FileHandler("trading.log", encoding="utf-8")
file_handler.setFormatter(formatter)

# Konzolra író handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_info(msg: str):
    logger.info(msg)

def log_warning(msg: str):
    logger.warning(msg)

def log_error(msg: str):
    logger.error(msg)

# --- CSV PERFORMANCE DATA LOGGING ---
CSV_FILE = "daily_performance.csv"

def log_performance(total_cash: float, net_liquidation: float, open_positions_count: int):
    """Elmenti a számla pillanatnyi állapotát CSV fájlba a szakdolgozati mérésekhez."""
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp', 'total_cash', 'net_liquidation', 'open_positions'])
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, total_cash, net_liquidation, open_positions_count])
    
    log_info(f"Teljesítmény adatok rögzítve CSV-ben: NetLiq={net_liquidation} USD")