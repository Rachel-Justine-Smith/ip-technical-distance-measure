import pandas as pd

def split_csv_by_year(input_file_path, output_directory):
    # Load the dataset
    data = pd.read_csv(input_file_path)
    # Assuming 'year' is the column based on which you want to split the data
    # Adjust the column name if it's different
    years = data['publn_year'].unique()
    
    for year in years:
        # Filter data for the specific year
        data_for_year = data[data['publn_year'] == year]
        
        # Define the output file name based on the year
        output_file_path = f'{output_directory}{year}.csv'
        
        # Save the filtered data to a new CSV file
        data_for_year.to_csv(output_file_path, index=False)
        print(f'Saved data for {year} to {output_file_path}')

# Replace 'your_data.csv' with the path to your input CSV file
input_file_path = 'MainfilrARS2_share.csv'
output_directory = 'csv_files/'
split_csv_by_year(input_file_path, output_directory)
