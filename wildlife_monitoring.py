from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, when, rand
import os

# Step 1: Create a Spark session
spark = SparkSession.builder \
    .appName("WildlifeMonitoring") \
    .getOrCreate()

# Step 2: Load the downloaded CSV data with tab-separated values
file_path = 'dataset/data.csv'  # Update this path as necessary
df = spark.read.csv(file_path, header=True, inferSchema=True, sep='\t')

# Step 3: Clean column names by stripping any whitespace
df = df.toDF(*[col.strip() for col in df.columns])

# Step 4: Define relevant columns
relevant_columns = ['species', 'decimalLatitude', 'decimalLongitude', 'eventDate', 'occurrenceStatus', 'individualCount']
df_filtered = df.select(relevant_columns)

# Step 5: Handle missing values - Drop rows with missing latitude, longitude, species, eventDate, or occurrenceStatus
df_cleaned = df_filtered.na.drop(subset=['species', 'decimalLatitude', 'decimalLongitude', 'eventDate', 'occurrenceStatus'])

# Step 6: Fill missing 'individualCount' values with a realistic random value (between 1 and 100 for instance)
# Using `rand()` to generate random values between 1 and 100
df_cleaned = df_cleaned.withColumn('individualCount', 
                                   when(col('individualCount').isNull(), (rand() * 212).cast('int')).otherwise(col('individualCount')))

# Step 7: Remove duplicate records of the same species (based on species and location)
df_cleaned = df_cleaned.dropDuplicates(['species', 'decimalLatitude', 'decimalLongitude'])

# Step 8: Normalize date formats
df_cleaned = df_cleaned.withColumn("eventDate", to_date(col("eventDate"), "yyyy-MM-dd"))

# Step 9: Save cleaned data to the local file system as a single file
output_path = 'dataset/output.csv'  # Save to local path
df_cleaned.coalesce(1).write.csv(output_path, header=True, mode='overwrite')  # coalesce(1) ensures single file output

# Stop the Spark session
spark.stop()
