import csv
import pandas
# import ast
import pandas as pd

# Function to read new.csv and return data types for specified columns
def get_data_types(file_path, table_schema, table_name, column_name):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Filter the DataFrame based on the specified table schema and table name
    filtered_df = df[(df['table_schema'] == table_schema) & (df['table_name'] == table_name)]
    
    # Get the data types for the specified column names
    data_types = filtered_df.loc[filtered_df['column_name'].isin(column_name), 'data_type']
    
    return data_types.tolist()

# Example usage
# file_path = r"path\to\new.csv"
# table_schema = "schema_name"
# table_name = "table_name"
# column_name = ["column1", "column2", "column3"]

# data_types = get_data_types(file_path, table_schema, table_name, column_name)
# print(data_types)

# Function to read unique_column.txt and process the data
def read_unique_column(file_path):
    queries = []
    with open(file_path, 'r') as file:
        for line in file:
            print(line)
            # print(1/0)
            parts = line.split('|')
            print(type(parts))

            if len(parts) == 4 and parts[2] != '0' and parts[3] != 'false':
                database_name = parts[0]
                table_name = parts[1]
                column_list = parts[2][1:-1].split(', ')
                column_combination = parts[3]
                if column_list:
                    query = (database_name, table_name, column_list, column_combination)
                    queries.append(query)
    return queries

# Function to generate the select query pattern
def generate_select_query(database_name, table_name, column_list, column_combination):
    select_queries = []
    for columns in column_list:
        casted_columns = ', '.join(f'CAST("{col}" AS varchar(255))' for col in columns)
        select_query = f"""
            SELECT 'CDO-Missing in PROD', COUNT(*) FROM (
                SELECT CONCAT({casted_columns}) FROM {database_name}.{table_name}
                WHERE gl_period = '202402P'
                GROUP BY 1
            )
        """
        select_queries.append(select_query)
    return select_queries

# Function to read new.csv and process the data
def read_new_csv(file_path):
    queries = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            table_schema = row['table_schema']
            table_name = row['table_name']
            column_name = row['column_name']
            data_type = row['data_type']
            column = f'"{column_name}"'  # Enclose column name in double quotes
            # Cast the column name as varchar(255) if the data type is not varchar
            if data_type != 'varchar':
                column = f'CAST("{column_name}" AS varchar(255))'
            queries.append((table_schema, table_name, column))
    return queries

# Main function to generate the select queries
def main():
    unique_column_queries = read_unique_column(r"C:\Users\Nitin104180\Downloads\unique_columns.txt")
    new_csv_queries = read_new_csv(r"C:\Users\Nitin104180\Downloads\new.csv")
    print(unique_column_queries)
    # for i,line in enumerate(unique_column_queries.splitlines()):
    #     parts = line.split('|')
    #     print(parts)

    # print(1/0)
    file_path=r"C:\Users\Nitin104180\Downloads\new.csv"
    column_query_preparation=""
    for query in unique_column_queries:
        database_name, table_name, column_list, column_combination = query
        database_name_2=database_name.replace('r3','r7')
        column_query_preparation=column_query_preparation+f"""**********{database_name}_{table_name}***************"""+"\n"      
        print(database_name, table_name, column_list, column_combination)
        print(column_combination)
        print(type(column_combination))
        tuple_result = eval(column_combination)

        # Convert the tuple to a list
        list_result = list(tuple_result)
        list_result=list_result+['name','age']
        print(list_result)
        conc_val="concatenate("
        # new_database_table_string=f"""select 'CDO' * from (
        #     (select {} from {database_name}.{table_name} where gl_period='202402P'
        #     group by 1 )
        #     except
        #     (select {} from {database_name_2}.{table_name} where gl_period='202402P'
        #     group by 1)) X
        #     union all
        #     select 'CDO' * from (
        #     (select {} from {database_name}.{table_name} where gl_period='202402P'
        #     group by 1 )
        #     except
        #     (select {} from {database_name_2}.{table_name} where gl_period='202402P'
        #     group by 1)) Y
        #     order by 2 """
        
        for i,val in enumerate(list_result):
            list_r=[]
            list_r.append(val)
            data_types = get_data_types(file_path, database_name, table_name, list_r)
            print(data_types[0])
            if i==1:
                conc_val=conc_val+f""","""
            if data_types[0]!='varchar':
                conc_val=conc_val+f"""cast({val} as varchar(255))"""
            else:
                conc_val=conc_val+f"""{val}"""
            print("########",i)
            
            if i!=0:
                if i!=(len(list_result)-1):
                    conc_val=conc_val+f""","""
            
                # column_query_preparation=column_query_preparation+f"""cast({val} as varchar(255))"""
        conc_val=conc_val+")"

        new_database_table_string=f"""select 'CDO',count(*) from (
            (select {conc_val} from {database_name}.{table_name} where gl_period='202402P'
            group by 1 )
            except
            (select {conc_val} from {database_name_2}.{table_name} where gl_period='202402P'
            group by 1)) X
            union all
            select 'CDO',count(*) from (
            (select {conc_val} from {database_name}.{table_name} where gl_period='202402P'
            group by 1 )
            except
            (select {conc_val} from {database_name_2}.{table_name} where gl_period='202402P'
            group by 1)) Y
            order by 2 """
        # print(new_database_table_string)
        # for column in ast.literal(column_combination):
        #     print(column_list.append(column))
        # print(1/0)
        # select_queries = generate_select_query(database_name, table_name, column_list, column_combination)
        # for select_query in select_queries:
        #     print(select_query)
    column_query_preparation=column_query_preparation+new_database_table_string+"\n"

    print(column_query_preparation)
if __name__ == "__main__":
    main()
