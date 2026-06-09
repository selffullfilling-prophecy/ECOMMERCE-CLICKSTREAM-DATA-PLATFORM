import os 
from dotenv import load_dotenv
import sys 

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

RAW_PURCHASE_FILE = os.getenv("RAW_PURCHASE_FILE") # chưa dùng 
RAW_LOG_FILE = os.getenv("RAW_LOG_FILE")
SAMPLE_DIR = os.getenv("SAMPLE_DIR")

if not RAW_PURCHASE_FILE:
    raise ValueError("RAW_PURCHASE_FILE is not set in the env")

if not RAW_LOG_FILE:
    raise ValueError("RAW_LOG_FILE is not set in the env")

if not SAMPLE_DIR:
    raise ValueError("SAMPLE_DIR is not set in the env")

if not os.path.exists(RAW_LOG_FILE):
    raise FileNotFoundError(f"Raw log file not found: {RAW_LOG_FILE}")

os.makedirs(SAMPLE_DIR, exist_ok=True)

def create_head_sample(input_path: str, output_path: str, n_rows: int) -> None: 
    # copy the header and n_rows data rows from a large csv file 

    total_lines = n_rows + 1

    print(f"Create sample file: {output_path}")
    print(f"Rows: {n_rows}")

    with(open(input_path, "r", encoding="utf-8", errors="replace")) as src:
        with(open(output_path, "w", encoding="utf-8", newline="")) as dst:
            for i, line in enumerate(src):
                if i >= total_lines:
                    break
                dst.write(line)

        print(f"Done: {output_path}")

sample_100k_path = os.path.join(SAMPLE_DIR, "log_tracking_100k.csv")
sample_1m_path = os.path.join(SAMPLE_DIR, "log_tracking_1m.csv")

create_head_sample(RAW_LOG_FILE, sample_100k_path, 100_000)
create_head_sample(RAW_LOG_FILE, sample_1m_path, 1_000_000)

