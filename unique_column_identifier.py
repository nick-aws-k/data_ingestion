import boto3
import time
import json
import ast
def check_validation(database_name, table_name,query):
    # Initialize Athena client
    client = boto3.client('athena')

    # Define Athena query
    query=query
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
    try:
    # Get query results
        query_results = client.get_query_results(QueryExecutionId=query_execution_id)
    except Exception as e:
    # Handle any other exceptions
        print("An error occurred:", e)
        return 0

    return 1
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
    # List to store unique columns
    unique_columns = []
    print(columns_query_results['ResultSet']['Rows'])
    v=columns_query_results['ResultSet']['Rows']
    if len(v)>1:
        print("records exist please find the unique columns")
            # Extract column names
        column_names = [col['Name'] for col in columns_query_results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        columns_info = columns_query_results['ResultSet']['ResultSetMetadata']['ColumnInfo']
        column_names_with_types = [(col['Name'], col['Type']) for col in columns_info]
        
        # Format column names and types as "name:type" strings
        column_names_with_types_str = [f"{col_name}:{col_type}" for col_name, col_type in column_names_with_types]
        print(column_names_with_types_str)
    
        
        
        
        # Iterate over each column and check if it contains unique values
        for column_name in column_names_with_types_str:
            # Check if column is unique
            if is_column_unique(database_name, table_name, column_name.split(':')[0]):
                unique_columns.append(column_name)
    
        return unique_columns
    else:
        return 0
def unique_validation(database_name, table_name,query):
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
    # List to store unique columns
    unique_columns = []
    print(columns_query_results['ResultSet']['Rows'])
    v=columns_query_results['ResultSet']['Rows']
    if len(v)>1:
        print("Not eligible for unique combination")
        return "False"
    else:
        return "True"
def append_to_line(input_string, line_number, text_to_append):
    
    lines = input_string.splitlines()

    
    if line_number < 0 or line_number >= len(lines):
        print("Error: Invalid line number.")
        return input_string

    
    lines[line_number] += text_to_append

    
    modified_string = '\n'.join(lines)

    return modified_string
def generate_select_queries(input_string):
    stu = ""
    in_s=input_string
    # Iterate over each line in the input string
    for i,line in enumerate(in_s.splitlines()):
        parts = line.split('|')  # Split the line by pipe delimiter

        # Check if the third value is not 0 and the line has three parts
        if len(parts) == 3 and parts[2] != '0':
            database_name = parts[0]
            table_name = parts[1]
            columns_info = ast.literal_eval(parts[2])  # Parse the third field as a list

            # Prepare SELECT query
            select_query = f"SELECT concat("
            for column_info in columns_info:
                column_name, column_type = column_info.split(':')
                if column_type.strip() == 'bigint':
                    column_name = f"CAST({column_name} AS varchar(255))"
                select_query += f"{column_name}, "
            select_query = select_query.rstrip(', ')  # Remove trailing comma
            select_query += f"),count(*) FROM {database_name}.{table_name} group by 1 having count(*) >1 limit 5;"
            proceed_val=unique_validation(database_name, table_name,select_query)
            modified_string=append_to_line(input_string, i, f"|{proceed_val}")
            input_string=modified_string
            
            # Append the SELECT query to the output string
            stu += f"****** {database_name} .{table_name}*********\n"
            stu += select_query + "\n"
            stu += "************************\n"
    
    return modified_string
if __name__ == "__main__":
    # Input database name and table name
    # "new_database"."ss_samplee_reco"
    # validate=check_validation(database_name="a", table_name="b")
    # print(val)
    # print(1/0)
    table_exist_query=f"SELECT * FROM dup_recooo.dupp_dup_recoo LIMIT 1"
    unique_valid_query = f"select concat(cast(id as varchar(255)),cast(age as varchar(255)),cast(percentage as varchar(255))) ,count(*) from new_database.ss_samplee_reco group by 1 having count(*) >1 limit 5"
    
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
        table_exist_query=f"SELECT * FROM {database_name}.{table_name} LIMIT 1"
        validate=check_validation(database_name, table_name,table_exist_query)
        if validate==1:
            # Get unique columns for the specified table
                unique_columns = get_unique_columns(database_name, table_name)
                print(unique_columns)
                unique_col=unique_col+database_name+"|"+table_name+"|"+str(unique_columns)
                unique_col=unique_col+"\n"
        else:
            unique_col=unique_col+database_name+"|"+table_name+"|"+str(validate)
            unique_col=unique_col+"\n"
    modified_string=generate_select_queries(unique_col)
    # Write unique columns to output file in S3
    s3.put_object(Body=str(modified_string), Bucket='project-test-bucket-xyz', Key='unique_columns.txt')
    
    # Print unique columns
