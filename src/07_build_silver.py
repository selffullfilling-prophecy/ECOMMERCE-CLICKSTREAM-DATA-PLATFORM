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
    split,
    expr
)

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

BRONZE_DIR = os.getenv("BRONZE_DIR")
SILVER_DIR = os.getenv("SILVER_DIR")

if not BRONZE_DIR: 
    raise ValueError("BRONZE DIR is not set in env.")

if not SILVER_DIR:
    raise ValueError("SLIVER DIR is not set in env.")

bronze_input_path = os.path.join(BRONZE_DIR, "log_tracking_1m")
silver_output_path = os.path.join(SILVER_DIR, "log_tracking_1m_cleaned")

if not os.path.exists(bronze_input_path):
    raise FileNotFoundError(f"BRONZE FILE NOT FOUND: {bronze_input_path}")

os.makedirs(SILVER_DIR, exist_ok=True)

spark = (
    SparkSession.builder
    .appName("BuilderSliverLayer")
    .master("local[5]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("=== BUILDING SILVER LAYER ===")
print(f"Input: {bronze_input_path}")
print(f"Outpur: {silver_output_path}")

bronze_df = spark.read.parquet(bronze_input_path)

print("\n=== BRONZE ROW COUNT ===")
bronze_count = bronze_df.count()
print(bronze_count)

# 1. Chuaan hóa data type và text
silver_df = (
    bronze_df
    .withColumn("event_type", lower(trim(col("event_type"))))
    .withColumn("brand", lower(trim(col("brand"))))
    .withColumn("category_code", lower(trim(col("category_code"))))
    .withColumn("event_date", to_date(col("event_time")))
)

# 2. Xử lý missing dạng null / chuỗi null / chuỗi rỗng 
silver_df = (
    silver_df
    .withColumn(
        "brand", 
        when (
            col("brand").isNull()
            | (trim(col("brand")) == "")
            | (lower(trim(col("brand"))) == "null"),
            "unknown"
        ).otherwise(col("brand"))
    )

    .withColumn(
        "category_code", 
        when(
            col("category_code").isNull()
            | (trim(col("category_code")) == "")
            | (lower(trim(col("category_code"))) == "null"), 
            "unknown"
        ).otherwise(col("category_code"))
    )
)

# 3. Lọc dữ liệu không hợp lệ 
silver_df = silver_df.filter(
    col("event_type").isNotNull()
    & col("product_id").isNotNull()
    & col("user_id").isNotNull()
    & col("price").isNotNull()
    & col("category_id").isNotNull()
    & col("user_session").isNotNull()
    & (col("price") > 0)
    & col("event_time").isNotNull()
    & col("event_type").isin("view", "cart", "purchase")
)

# 4. Drop duplicate theo key đã định nghĩa 
duplicate_key = [
    "event_time",
    "event_type",
    "product_id",
    "user_id",
    "user_session"
]

silver_df = silver_df.dropDuplicates(duplicate_key)

# 5. Tách category_code theo nhiều cấp 
silver_df = (
    silver_df
    .withColumn("category_level_1", expr("get(split(category_code, '\\\\.'), 0)"))
    .withColumn("category_level_2", expr("get(split(category_code, '\\\\.'), 1)"))
    .withColumn("category_level_3", expr("get(split(category_code, '\\\\.'), 2)"))
)

print("\n=== SILVER SCHEMA ===")
silver_df.printSchema()

print("\n=== SILVER ROW COUNT ===")
sliver_count = silver_df.count()
print(sliver_count)

removed_rows = bronze_count - sliver_count
removed_percentage = removed_rows / bronze_count * 100

print("\n=== CLEANING SUMMARY ===")
print(f"Bronze rows: {bronze_count:,}")
print(f"Silver rows: {sliver_count:,}")
print(f"Removed rows: {removed_rows:,}")
print(f"Removed percentage: {removed_percentage:.4f}%")

print("\n=== EVENT TYPE DISTRIBUTION AFTER CLEANING ===")
silver_df.groupBy("event_type").count().show()

print("\n=== SAMPLE SILVER DATA ===")
silver_df.show(5, truncate=False)

silver_df.write.mode("overwrite").parquet(silver_output_path)

print("\nSilver layer created successfully.")

spark.stop()
