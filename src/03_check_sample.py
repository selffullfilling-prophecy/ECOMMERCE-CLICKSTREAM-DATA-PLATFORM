import os
import sys
from pyspark.sql import SparkSession 
from dotenv import load_dotenv

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

SAMPLE_DIR = os.getenv("SAMPLE_DIR")

if not SAMPLE_DIR:
    raise ValueError("SAMPLE_DIR is not set in the env")

sample_100k_path = os.path.join(SAMPLE_DIR, "log_tracking_100k.csv")
sample_1m_path = os.path.join(SAMPLE_DIR, "log_tracking_1m.csv")

if not os.path.exists(sample_100k_path):
    raise FileNotFoundError(f"Sample file not found: {sample_100k_path}")

if not os.path.exists(sample_1m_path):
    raise FileNotFoundError(f"Sample file not found: {sample_1m_path}")

spark = (
    SparkSession.builder
    .appName("CheckSample")
    .master("local[5]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

def check_sample_data(file_path: str, sample_name: str) -> None:
    print(f"=== CHECKING SAMPLE: {sample_name} ===")
    print(f"File Path: {file_path}")

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(file_path)
    )

    print("=== SCHEMA ===")
    df.printSchema()

    print("=== COLUMNS ===")
    print(df.columns)

    print("=== ROW COUNT ===")
    print(df.count())

    print("=== EVENT TYPE DISTRIBUTION ===")
    df.groupBy("event_type").count().show()

    print("=== SAMPLE DATA")
    df.show(5, truncate=False)


check_sample_data(sample_100k_path, "log_tracking_100k.csv")
check_sample_data(sample_1m_path, "log_tracking_1m.csv")

spark.stop()
