import os 
import sys
from dotenv import load_dotenv
from pyspark.sql import SparkSession 
from pyspark.sql.functions import (
    col,
    countDistinct,
    min as sparkMin,
    max as sparkMax,
    sum as sparkSum,
    when,
    trim,
    lower
)

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

load_dotenv()

SILVER_DIR = os.getenv("SILVER_DIR")

if not SILVER_DIR:
    raise ValueError("SILVER DIR is not set in env.")

silver_path = os.path.join(SILVER_DIR, "log_tracking_1m_cleaned")

if not os.path.exists(silver_path):
    raise FileNotFoundError(f"Silver path not found: {silver_path}")

spark = (
    SparkSession.builder
    .appName("CheckSilverLayer")
    .master("local[5]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("\n=== CHECKING SILVER LAYERING ===")
print(f"Input: {silver_path}")

silver_df = spark.read.parquet(silver_path)

# --------------------------------------------------
# 1. Basic info
# --------------------------------------------------

print("\n==== SILVER SCHEMA ===")
silver_df.printSchema()

print("\n=== SILVER ROW COUNT ===")
total_rows = silver_df.count()
print(f"Total rows: {total_rows:,}")

# --------------------------------------------------
# 2. Expected columns check
# --------------------------------------------------

expected_columns = [
        "event_time",
    "event_type",
    "product_id",
    "category_id",
    "category_code",
    "brand",
    "price",
    "user_id",
    "user_session",
    "ingestion_time",
    "source_file",
    "event_date",
    "category_level_1",
    "category_level_2",
    "category_level_3",
]

actual_columns = silver_df.columns
missing_columns = [c for c in expected_columns if c not in actual_columns]

print("\n=== COLUMN CHECK ===")
if not missing_columns:
    print("PASS: All expected columns exist.")
else:
    print("FAIL: Missing columns:")
    for c in missing_columns:
        print(f"- {c}")

# --------------------------------------------------
# 3. Data type check
# --------------------------------------------------
schema_types = dict(silver_df.dtypes)
print(f"\n schema types: {schema_types}")

print("\n=== DATA TYPE CHECK ===")
event_time_type = schema_types.get("event_time")
event_date_type = schema_types.get("event_date")

if event_time_type == "timestamp":
    print("PASS: event_time is timestamp.")
else:
    print(f"FAIL: event_time should be timestamp, current type = {event_time_type}")

if event_date_type == "date":
    print("PASS: event_date is date.")
else:
    print(f"FAIL: event_date should be date, current type = {event_date_type}")

# --------------------------------------------------
# 4. Event type validation
# --------------------------------------------------
valid_events = ["view", "cart", "purchase"]

invalid_event_count = silver_df.filter(
    ~col("event_type").isin(valid_events)
    | col("event_type").isNull()
).count()

print("\n=== EVENT TYPE CHECK ===")
silver_df.groupBy("event_type").count().orderBy("count", ascending=False).show()

if invalid_event_count == 0:
    print("PASS: event_type only contains view/cart/purchase.")
else:
    print(f"FAIL: Invalid event_type rows = {invalid_event_count:,}")

# --------------------------------------------------
# 5. Null / missing check for important columns
# -------------------------------------------------
important_columns = [
    "event_time",
    "event_date",
    "event_type",
    "product_id",
    "category_id",
    "category_code",
    "brand",
    "price",
    "user_id",
    "user_session",
]

null_exprs = []

for c in important_columns:
    null_exprs.append(
        sparkSum(
            when(
                col(c).isNull()
                | (trim(col(c).cast("string")) == "")
                | (lower(trim(col(c).cast("string"))) == "null"),
                1
            ).otherwise(0)
        ).alias(c)
    )

print("\n=== NULL / MISSING VALUE CHECK ===")
silver_df.select(null_exprs).show(truncate=False)

# --------------------------------------------------
# 6. Price check
# --------------------------------------------------
invalid_price_count = silver_df.filter(
    col("price").isNull() | (col("price") <= 0)
).count()

print("\n=== PRICE CHECK ===")
if invalid_price_count == 0:
    print("PASS: No null or non-positive price.")
else: 
    print(f"FAIL: Invalid price rows = {invalid_price_count:,}")

silver_df.select(
    sparkMin("price").alias("min_price"),
    sparkMax("price").alias("max_price"),
).show()

# --------------------------------------------------
# 7. Duplicate check
# --------------------------------------------------
duplicate_key = [
    "event_time",
    "event_type",
    "product_id",
    "user_id",
    "user_session",
]

distinct_key_count = silver_df.dropDuplicates(duplicate_key).count()
duplicate_count = total_rows - distinct_key_count

print("\n=== DUPLICATE CHECK ===")
print(f"Total rows: {total_rows:,}")
print(f"Distinct key rows: {distinct_key_count:,}")
print(f"Duplicate rows: {duplicate_count:,}")

if duplicate_count == 0:
    print("PASS: No duplicate rows by defined duplicate key.")
else:
    print(f"FAIL: Duplicate rows still exist = {duplicate_count:,}")

# --------------------------------------------------
# 8. Category check
# --------------------------------------------------
print("\n=== CATEGORY CHECK ===")

unknown_category_count = silver_df.filter(col("category_code") == "unknown").count()
unknown_brand_count = silver_df.filter(col("brand") == "unknown").count()

print(f"Unknown category_code rows: {unknown_category_count:,}")
print(f"Unknown brand rows: {unknown_brand_count:,}")

silver_df.groupBy("category_level_1").count().orderBy("count", ascending=False).show(20, truncate=False)

# --------------------------------------------------
# 9. Time range check
# --------------------------------------------------
print("\n=== TIME RANGE CHECK ===")
silver_df.select(
    sparkMin("event_time").alias("min_event_time"),
    sparkMax("event_time").alias("max_event_time"),
    sparkMin("event_date").alias("min_event_date"),
    sparkMax("event_date").alias("max_event_date"),
).show(truncate=False)

# --------------------------------------------------
# 10. Basic cardinality check
# --------------------------------------------------
print("\n=== CARDINALITY CHECK ===")
silver_df.select(
    countDistinct("user_id").alias("unique_users"),
    countDistinct("product_id").alias("unique_products"),
    countDistinct("user_session").alias("unique_sessions"),
    countDistinct("category_id").alias("unique_categories"),
    countDistinct("brand").alias("unique_brands"),
).show(truncate=False)

# --------------------------------------------------
# Final summary
# --------------------------------------------------
print("\n=== SILVER CHECK SUMMARY ===")

all_passed = (
    not missing_columns
    and event_time_type == "timestamp"
    and event_date_type == "date"
    and invalid_event_count == 0
    and invalid_price_count == 0
    and duplicate_count == 0
)

if all_passed:
    print("SILVER DATA CHECK PASSED.")
else:
    print("SILVER DATA CHECK FAILED. Review the failed checks above.")

spark.stop()