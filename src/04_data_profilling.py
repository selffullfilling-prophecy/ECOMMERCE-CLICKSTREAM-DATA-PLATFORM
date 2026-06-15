import os
import sys
from dotenv import load_dotenv
from pyspark.sql import SparkSession 
from pyspark.sql.functions import (
    col, count, countDistinct, min, max, avg, stddev, sum as spark_sum,
    when, trim, lower
)

os.environ["PYSPARK_PYTHON"] = sys.executable 
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable 

load_dotenv()

SAMPLE_DIR = os.getenv("SAMPLE_DIR")

if not SAMPLE_DIR: 
    raise ValueError("SAMPLE_DIR is not set in the env")

sample_1m_path = os.path.join(SAMPLE_DIR, "log_tracking_1m.csv")

if not os.path.exists(sample_1m_path):
    raise FileNotFoundError(f"Sample file not found: {sample_1m_path}")

spark = (
    SparkSession.builder
    .appName("DataProfiling")
    .master("local[5]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("=== READING SAMPLE 1M FILE ===")
print(sample_1m_path)

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(sample_1m_path)
)

df.cache()

'''
- Tổng số dòng
- Số user khác nhau
- Số product khác nhau
- Số session khác nhau
- Khoảng thời gian dữ liệu
- Phân phối event_type
- Null report
- Price statistics
- Duplicate report
'''
print("=== SCHEMA ===")
df.printSchema()

print("\n=== BASIC OVERVIEW ===")

total_rows = df.count()

overview_df = df.select(
    count("*").alias("total_rows"),
    countDistinct("user_id").alias("unique_users"),
    countDistinct("product_id").alias("unique_products"),
    countDistinct("user_session").alias("unique_sessions"),
    countDistinct("category_id").alias("unique_categories"),
    countDistinct("brand").alias("unique_brand")
)

overview_df.show(truncate=False)

print("\n===EVENT TIME RANGE ===")
df.select(
    min("event_time").alias("min_event_time"),
    max("event_time").alias("max_event_time")
).show(truncate=False)

print("\n=== EVENT TYPE DISTRIBUTION ===")
event_type_dist = (
    df.groupBy("event_type")
    .count()
    .withColumn("percentage", col("count") / total_rows * 100)
    .orderBy(col("count").desc())
)

event_type_dist.show(truncate=False)

print("\n=== PRICE STATISTICS ===")
price_stats = (
    df.select(
        count("price").alias("price_count"),
        min("price").alias("min_price"),
        max("price").alias("max_price"),
        avg("price").alias("avg_price"),
        stddev("price").alias("stddev_price")
    )
)

price_stats.show(truncate=True)

print("\n === INVALID PRICE CHECK ===")
price_nulls = (
    df.select(
        spark_sum(when(col("price").isNull(), 1).otherwise(0)).alias("price_null_count"),
        spark_sum(when(col("price") <= 0, 1).otherwise(0)).alias("price_zero_or_negative_count")
    )
)

price_nulls.show(truncate=False)

print("\n=== NULL / MISSING VALUE REPORT ===")

null_exprs = []

for c in df.columns:
    null_exprs.append(
        spark_sum(when(
            col(c).isNull()
            | (trim(col(c).cast("string")) == "")
            | (lower(col(c).cast("string")) == "null")
        , 1).otherwise(0)).alias(c)
    )

null_report = df.select(null_exprs)
null_report.show(truncate=False)

print("\n=== NULL / MISSING VALUE PERCENTAGE ===")

null_percentage_exprs = []
for c in df.columns:
    null_percentage_exprs.append(
        (spark_sum(
            when(
                col(c).isNull()
                | (trim(col(c).cast("string")) == "")
                | (lower(trim(col(c)).cast("string")) == "null"),
                1
            ).otherwise(0)
        ) / total_rows * 100
    ).alias(c) 
)

null_percentage_reports = df.select(null_percentage_exprs)
null_percentage_reports.show(truncate=False)

print("\n === DUPLICATE CHECK ===")

duplicate_key = [
    "event_time",
    "event_type",
    "product_id",
    "user_id",
    "user_session"
]

distinct_key_count = df.select(duplicate_key).distinct().count()
duplicate_count = total_rows - distinct_key_count

print(f"Total rows: {total_rows:,}")
print(f"Distinct rows by duplicate key: {distinct_key_count:,}")
print(f"Duplicate rows: {duplicate_count:,}")
print(f"Duplicate percentage: {duplicate_count / total_rows * 100:.4f}%")

print("\n=== Top 20 BRANDS BY EVENT COUNT ===")
df.groupBy("brand").count().orderBy(col("count").desc()).show(20, truncate=False)

print("\n=== TOP 20 CATEGORIES BY EVENT COUNT ===")
df.groupBy("category_code").count().orderBy(col("count").desc()).show(20, truncate=False)

df.unpersist()
spark.stop()
