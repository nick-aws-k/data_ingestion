from pyspark.sql import SparkSession
from itertools import combinations
from pyspark.sql.functions import concat_ws

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("AutomatedUniqueKeyCombination") \
    .getOrCreate()

# Read data from Athena table into DataFrame
df = spark.read.format("jdbc") \
    .option("url", "jdbc:awsathena://athena.us-west-2.amazonaws.com:443") \
    .option("dbtable", "your_athena_table") \
    .option("user", "your_aws_access_key_id") \
    .option("password", "your_aws_secret_access_key") \
    .load()

# Define date columns to exclude
date_columns = ["date_column1", "date_column2"]  # Add your date column names here

# Filter out date columns from the list of columns
non_date_columns = [col for col in df.columns if col not in date_columns]

# Automate finding unique key combinations
unique_combination_found = False
num_columns = len(non_date_columns)
for r in range(2, num_columns + 1):  # Start from 2 columns
    for combination in combinations(non_date_columns, r):
        # Concatenate selected columns
        concatenated_columns = concat_ws("_", *combination)
        # Group by concatenated columns and count occurrences
        grouped_df = df.groupBy(concatenated_columns).count()
        # Filter groups where count is greater than 1
        filtered_df = grouped_df.filter(grouped_df["count"] > 1)
        # Check if any groups found
        if filtered_df.count() == 0:
            unique_combination_found = True
            print("Unique key combination found:", combination)
            break
    if unique_combination_found:
        break

# Stop SparkSession
spark.stop()
