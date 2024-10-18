from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max as spark_max, row_number
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml import Pipeline

# Step 1: Create a Spark session
spark = SparkSession.builder \
    .appName("Wildlife Monitoring - Decision Tree") \
    .getOrCreate()

# Step 2: Load the cleaned data from the CSV file
file_path = 'dataset/output.csv/part-00000-f8f7d0bc-a5bc-40e3-a806-dc5dfb385e15-c000.csv'  # Update this path to your cleaned data file
df = spark.read.csv(file_path, header=True, inferSchema=True)

# Step 3: Select relevant columns
df = df.select('species', 'decimalLatitude', 'decimalLongitude', 'individualCount')

# Step 4: Find the maximum count for each species and the corresponding latitude/longitude
window_spec = Window.partitionBy("species").orderBy(col("individualCount").desc())
ranked_df = df.withColumn("rank", row_number().over(window_spec))
max_count_per_species = ranked_df.filter(col("rank") == 1) \
    .select('species', 'decimalLatitude', 'decimalLongitude', 'individualCount')

# Step 5: Create a binary classification target (1 if count > threshold, else 0)
threshold = 10  # Define a threshold for individual count
df = df.withColumn('label', (col('individualCount') > threshold).cast('integer'))

# Step 6: Remove existing 'features' column if it exists
if 'features' in df.columns:
    df = df.drop('features')

# Step 7: Assemble features for the decision tree
feature_cols = ['decimalLatitude', 'decimalLongitude']
assembler = VectorAssembler(inputCols=feature_cols, outputCol='features')
df = assembler.transform(df)

# Step 8: Split data into training and test sets
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# Step 9: Initialize and fit the decision tree model
dt = DecisionTreeClassifier(labelCol='label', featuresCol='features')
pipeline = Pipeline(stages=[dt])  # Remove assembler from pipeline since we've already transformed the DataFrame
model = pipeline.fit(train_data)

# Step 10: Make predictions on test data
predictions = model.transform(test_data)

# Step 11: Display results
predictions.select('species', 'decimalLatitude', 'decimalLongitude', 'individualCount', 'label', 'prediction').show(truncate=False)

# Step 12: Save the max individual count per species to a new CSV file
output_path = 'dataset/max_individual_count_per_species.csv'  # Specify your output path
max_count_per_species.coalesce(1).write.csv(output_path, header=True, mode='overwrite')

# Stop the Spark session
spark.stop()
