#this code is sent by vineet and it has species recorded individually
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.sql.functions import col
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder.appName("KMeansWildlifeClustering").getOrCreate()

# Load cleaned data from the previous step
file_path = 'dataset/output.csv/part-00000-f8f7d0bc-a5bc-40e3-a806-dc5dfb385e15-c000.csv'  # Path to cleaned CSV data
df_cleaned = spark.read.csv(file_path, header=True, inferSchema=True)

# Step 1: Assemble the features (latitude and longitude)
assembler = VectorAssembler(inputCols=['decimalLatitude', 'decimalLongitude'], outputCol='features')
df_features = assembler.transform(df_cleaned)

# Step 2: Create and train the KMeans model
k = 6  # Example value, you can adjust based on your elbow plot analysis
kmeans = KMeans(k=k, seed=1, featuresCol='features', predictionCol='prediction')
model = kmeans.fit(df_features)

# Step 3: Make predictions
df_predictions = model.transform(df_features)

# Step 4: Select relevant columns (including species and cluster prediction)
df_result = df_predictions.select('species', 'decimalLatitude', 'decimalLongitude', 'prediction')

# Step 5: Save the result to a new CSV file
output_path = 'dataset/kmeans_specieswise.csv'
df_result.coalesce(1).write.csv(output_path, header=True, mode='overwrite')

# Stop Spark session
spark.stop()
