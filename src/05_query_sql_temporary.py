from pyspark.sql import SparkSession 
from dotenv import load_dotenv
import sys 
import os 

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

RAW_LOG_FILE = os.getenv("RAW_LOG_FILE")

print("=== RAW LOG FILE ===")
print(RAW_LOG_FILE)

if not RAW_LOG_FILE:
    raise ValueError("RAW_LOG_FILE is not set in the env")

spark = (
    SparkSession.builder
    .appName('query_sql')
    .master('local[5]')
    .getOrCreate()
)

spark.sparkContext.setLogLevel('ERROR')

print("=== QUERY SQL ===")

log_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(RAW_LOG_FILE)
)

log_df.createOrReplaceTempView("clickstream")

result = spark.sql("""
    SELECT MAX(category_code
    FROM clickstream
""")
