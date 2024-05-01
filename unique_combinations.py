import sys
from pyspark.sql import SparkSession
from itertools import combinations
from pyspark.sql.functions import concat_ws
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
import boto3


# from awswrangler import Session, Pandas
# from pyspark.sql import SparkSession

# # Initialize SparkSession
# spark = SparkSession.builder \
#     .appName("Read from Athena to Spark DataFrame") \
#     .getOrCreate()

# Initialize AWS Wrangler Session
import awswrangler as wr

# Define your Athena SQL query
sql_query = """
    SELECT *
    FROM "new_database"."ss_samplee_reco"
"""

# Read data from Athena into a Pandas DataFrame
df1 = wr.athena.read_sql_query(sql_query,database='dup_recooo')
date_columns=[]
df = spark.createDataFrame(df1)
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
# Display the DataFrame
print(df)
job.commit()
