import pandas as pd
# import csv
# def fetch_values(csv_file, filter_column1, filter_value1, filter_column2, filter_value2):
#     values_list = []

#     with open(csv_file, 'r') as file:
#         csv_reader = csv.reader(file)

#         # Read the header to get column indices
#         header = next(csv_reader)
#         col_indices = {col: idx for idx, col in enumerate(header)}

#         for row in csv_reader:
#             # Check if the row matches the filters
#             if (row[col_indices.get(filter_column1)] == filter_value1 and
#                     row[col_indices.get(filter_column2)] == filter_value2):
#                 # Append value from the third column to the list
#                 values_list.append(row[col_indices.get('ThirdColumn')])

#     return values_list
def fetch_values(csv_file, filter_column1, filter_value1, filter_column2, filter_value2):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Filter the DataFrame based on values in the first and second columns
    filtered_df = df[(df[filter_column1] == filter_value1) & (df[filter_column2] == filter_value2)]

    # Extract values from the third column and convert them to a list
    values_list = filtered_df.iloc[:, 2].tolist()

    return values_list
csv_file=r"C:\Users\Nitin104180\Downloads\new.csv"
filter_column1='table_schema'
# filter_value1='new_database'
filter_column2='table_name'
filter_value2='ss_samplee_reco'

# values_list=fetch_values(csv_file, filter_column1, filter_value1, filter_column2, filter_value2)
# values_list=['a']
# if len(values_list)<=1:
#     print("empty")
# print(values_list)

# print(1/0)
database_name_cdo='dtvr3_sms_datalake_hist_db'
table_name='ss_samplee_reco'
database_name_prod='dtvp_sms_datalake_hist_db'
col_name_prod=fetch_values(csv_file, filter_column1, database_name_prod, filter_column2, table_name)
col_name_cdo=fetch_values(csv_file, filter_column1, database_name_cdo, filter_column2, table_name)
l=(len(col_name_prod))
# print(l)
w=(len(col_name_cdo))
if l<1 or w<1:
    print('empty please change the database')

# print(1/0)
prod_val= ','.join([f"'{item}'" for item in col_name_prod])
cdo_val= ','.join([f"'{item}'" for item in col_name_cdo])
s=""
ll=""
for i in range(2,l+1):    
    if i>=2 and i<l:
        k=","
    else:
        k=""
    ll=ll+str(i)+k
# print(ll)
s="order by "+ll
s=s+" desc"
# print(s)
# print(1/0)
query_string=f"""select 'CDO', * from (
    select {prod_val} from {database_name_prod}.{table_name} where gl_period='202402P'
    except
    select {cdo_val} from {database_name_cdo}.{table_name} where gl_period='202402P') X
    union all 
select 'PROD', * from (
    select {cdo_val} from {database_name_cdo}.{table_name} where gl_period='202402P'
    except
    select {prod_val} from {database_name_prod}.{table_name} where gl_period='202402P') Y
    """
print(query_string+s)
# def fetch_values(csv_file, filter_column1, filter_value1, filter_column2, filter_value2):
#     values_list = []

#     with open(csv_file, 'r') as file:
#         csv_reader = csv.reader(file)

#         # Read the header to get column indices
#         header = next(csv_reader)
#         col_indices = {col: idx for idx, col in enumerate(header)}

#         for row in csv_reader:
#             # Check if the row matches the filters
#             if (row[col_indices.get(filter_column1)] == filter_value1 and
#                     row[col_indices.get(filter_column2)] == filter_value2):
#                 # Append value from the third column to the list
#                 values_list.append(row[col_indices.get(header[2])])

#     return values_list