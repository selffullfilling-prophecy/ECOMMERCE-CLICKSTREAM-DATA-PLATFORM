from pyspark.sql import SparkSession 

spark = (
    SparkSession.builder
    .appName('SparkTest')
    .getOrCreate()
)

data = [
    (1, 'view'),
    (2, 'cart'),
    (3, 'purchase') 
]

df = spark.createDataFrame(data, ["id", "event_type"])

df.show()

spark.stop()