import os 
import sys
from dotenv import load_dotenv

from pyspark.sql import SparkSession 
from pyspark.sql.functions import current_timestamp, input_file_name 

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

SAMPLE_DIR = os.getenv("SAMPLE_DIR")
BRONZE_DIR = os.getenv("BRONZE_DIR")

if not SAMPLE_DIR:
    raise ValueError("SAMPLE_DIR is not set in .env")

if not BRONZE_DIR: 
    raise ValueError("BRONZE_DIR is not set in .env")

sample_1m_file = os.path.join(SAMPLE_DIR, "log_tracking_1m.csv")
bronze_output_path = os.path.join(BRONZE_DIR, "log_tracking_1m")

if not os.path.exists(sample_1m_file):
    raise FileNotFoundError(f"Sample file not found: {sample_1m_file}")

os.makedirs(BRONZE_DIR, exist_ok=True)

spark = (
    SparkSession.builder
    .appName("BuildBronzer")
    .master("local[5]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("=== BUILDING BRONZE LAYER ===")
print(f"Input : {sample_1m_file}")
print(f"Output: {bronze_output_path}")

raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(sample_1m_file)
)

bronze_df = (
    raw_df
    .withColumn("ingestion_time", current_timestamp())
    .withColumn("source_file", input_file_name())
)

print("\n=== BRONZE SCHEMA ===")
bronze_df.printSchema()

print("\n=== BRONZE ROW COUNT ===")
print(bronze_df.count())

print("\n=== SAMPLE DATA ===")
bronze_df.show(5, truncate=False)

bronze_df.write.mode("overwrite").parquet(bronze_output_path)

print("\nBronze layer created successfully.")

spark.stop()



