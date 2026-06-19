import os 
import sys
from dotenv import load_dotenv
from pyspark.sql import SparkSession 

from pyspark.sql.functions import (
    col,
    lower,
    trim,
    when,
    to_date,
    split
)

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

BRONZE_DIR = os.getenv("BRONZE_DIR")
SLIVER_DIR = os.getenv("SLIVER_DIR")

if not BRONZE_DIR: 
    raise ValueError("BRONZE DIR is not set in env.")

if not SLIVER_DIR:
    raise ValueError("SLIVER DIR is not set in env.")

bronze_input_path = os.path.join(BRONZE_DIR, "log_tracking_1m")
sliver_output_path = os.path.join(SLIVER_DIR, "log_tracking_1m_cleaned")

if not os.path.exists(bronze_input_path):
    raise FileNotFoundError(f"BRONZE FILE NOT FOUND: {bronze_input_path}")

os.makedirs(SLIVER_DIR, exist_ok=True)

spark = (
    SparkSession.builder
    .appName("BuilderSliverLayer")
    .master("local[5]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("=== BUILDING SLIVER LAYER ===")
print(f"Input: {bronze_input_path}")
print(f"Outpur: {sliver_output_path}")

bronze_df = spark.read.parquet(bronze_input_path)

print("\n=== BRONZE ROW COUNT ===")
bronze_count = bronze_df.count()
print(bronze_count)

# 1. Chuaan hóa data type và text
sliver_df = (
    bronze_df
    .withColumn("event_type", lower(trim(col("event_type"))))
    .withColumn("brand", lower(trim(col("brand"))))
    .withColumn()
)