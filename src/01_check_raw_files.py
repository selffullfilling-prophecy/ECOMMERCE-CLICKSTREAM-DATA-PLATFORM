from pyspark.sql import SparkSession 
from dotenv import load_dotenv
import os 
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

RAW_PURCHASE_FILE = os.getenv("RAW_PURCHASE_FILE")
RAW_LOG_FILE = os.getenv("RAW_LOG_FILE")

print("=== RAW PURCHASE FILE ===")
print(RAW_PURCHASE_FILE)
print("=== RAW LOG FILE ===")
print(RAW_LOG_FILE)

if not RAW_PURCHASE_FILE: 
    raise ValueError("RAW_PURCHASE_FILE is not set in the env")

if not RAW_LOG_FILE:
    raise ValueError("RAW_LOG_FILE is not set in the env")

spark = (
    SparkSession.builder
    .appName('CheckRawFiles')
    .master('local[5]')
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("=== CHECKING RAW PURCHASE FILE")

purchase_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(RAW_PURCHASE_FILE)
)

print("=== SCHEAM ===")
purchase_df.printSchema()

print("=== COLUMNS ===") 
print(purchase_df.columns)

print("=== SAMPLE DATA ===")
print(purchase_df.show(5, truncate=False))

print("=== ROW COUNT ===")
print(purchase_df.count())

if "event_type" in purchase_df.columns:
    print("\n=== EVENT TYPE DISTRIBUTION ===")
    purchase_df.groupBy("event_type").count().show()

print("\n=== CHECKING ROW LOG FILE ===")

log_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(RAW_LOG_FILE)
)

print("=== SCHEMA ===")
log_df.printSchema()

print("=== COLUMNS ===")
print(log_df.columns)

print("=== SAMPLE DATA ===") 
log_df.show(5, truncate=False)

print("=== ROW COUNT ===")
print(log_df.count())

spark.stop()