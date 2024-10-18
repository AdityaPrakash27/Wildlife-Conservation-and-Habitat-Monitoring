from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum

# Step 1: Create a Spark session
spark = SparkSession.builder \
    .appName("Wildlife Monitoring - Summing Species Count") \
    .getOrCreate()

# Step 2: Load the cleaned data from the CSV file
file_path = 'dataset/output.csv/part-00000-f8f7d0bc-a5bc-40e3-a806-dc5dfb385e15-c000.csv'  # Update this path to your cleaned data file
df = spark.read.csv(file_path, header=True, inferSchema=True)

# Step 3: Group by species and sum the individual counts
species_count = df.groupBy('species').agg(spark_sum('individualCount').alias('totalCount'))

# Step 4: Show the result (optional, for verification)
species_count.show(truncate=False)

# Step 5: Save the result to a new CSV file
output_path = 'dataset/species_total_count.csv'  # Specify your output path
species_count.coalesce(1).write.csv(output_path, header=True, mode='overwrite')

# Step 6: Stop the Spark session
spark.stop()
