import boto3
import time
import json
def wait_for_query_completion(client, query_execution_id):
    while True:
        response = client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(5)

def is_column_unique(database_name, table_name, column_name):
    # Initialize Athena client
    client = boto3.client('athena')

    # Define Athena query
    query = f"SELECT COUNT(DISTINCT {column_name}) AS unique_count, COUNT(*) AS total_count FROM {database_name}.{table_name}"

    # Execute Athena query
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database_name
        },
        ResultConfiguration={
            'OutputLocation': 's3://project-test-bucket-xyz/sample_record/athena_output/'
        }
    )

    # Get query execution ID
    query_execution_id = response['QueryExecutionId']

    # Wait for query execution to complete
    wait_for_query_completion(client, query_execution_id)

    # Get query results
    query_results = client.get_query_results(QueryExecutionId=query_execution_id)

    # Parse results to check if column is unique
    unique_count = int(query_results['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])
    total_count = int(query_results['ResultSet']['Rows'][1]['Data'][1]['VarCharValue'])

    return unique_count == total_count

def get_unique_columns(database_name, table_name):
    # Initialize Athena client
    client = boto3.client('athena')

    # Define Athena query to get column names
    columns_query = f"SELECT * FROM {database_name}.{table_name} LIMIT 1"
    
    # Execute Athena query to get column names
    response = client.start_query_execution(
        QueryString=columns_query,
        QueryExecutionContext={
            'Database': database_name
        },
        ResultConfiguration={
            'OutputLocation': 's3://project-test-bucket-xyz/sample_record/athena_output/'
        }
    )

    # Get query execution ID
    query_execution_id = response['QueryExecutionId']

    # Wait for query execution to complete
    wait_for_query_completion(client, query_execution_id)

    # Get query results
    columns_query_results = client.get_query_results(QueryExecutionId=query_execution_id)
    
    # Extract column names
    column_names = [col['Name'] for col in columns_query_results['ResultSet']['ResultSetMetadata']['ColumnInfo']]

    # List to store unique columns
    unique_columns = []
    
    # Iterate over each column and check if it contains unique values
    for column_name in column_names:
        # Check if column is unique
        if is_column_unique(database_name, table_name, column_name):
            unique_columns.append(column_name)

    return unique_columns

if __name__ == "__main__":
    # Input database name and table name
    # "new_database"."ss_samplee_reco"
    unique_col=""
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket='project-test-bucket-xyz', Key='nit/input.json')
    json_content = response['Body'].read().decode('utf-8')

    # Parse JSON content
    data = json.loads(json_content)
    for key,val in data.items():
        # Initialize Athena client
        database_name = val
        table_name = key

    # Get unique columns for the specified table
        unique_columns = get_unique_columns(database_name, table_name)
        unique_col=unique_col+database_name+"|"+table_name+"|"+str(unique_columns)
        unique_col=unique_col+"\n"
    # Write unique columns to output file in S3
    
    s3.put_object(Body=str(unique_col), Bucket='project-test-bucket-xyz', Key='unique_columns.txt')
    
    # Print unique columns
