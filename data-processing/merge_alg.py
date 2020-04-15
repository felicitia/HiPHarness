from csv import writer
from csv import reader
import os

input_dir = '/Users/yixue/Documents/Research/LessIsMore/R/实验'

def add_column_in_csv(input_file, output_file, alg):
    # Open the input_file in read mode and output_file in write mode
    with open(input_file, 'r') as read_obj, \
            open(output_file, 'a') as write_obj:
        csv_reader = reader(read_obj)
        csv_writer = writer(write_obj)
        # Read each row of the input csv file as list
        next(csv_reader) # skip header
        for row in csv_reader:
            # Append the default text in the row / list
            row.append(alg)
            # Add the updated row / list to the output file
            csv_writer.writerow(row)

if __name__ == "__main__":
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            alg = filename.split('_')[0]
            output = filename.replace(alg, 'all')
            # Add column with same text in all rows
            add_column_in_csv(os.path.join(input_dir, filename),
            os.path.join(input_dir, output), alg)
        else:
            continue
