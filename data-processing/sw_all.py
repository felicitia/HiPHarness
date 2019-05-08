import csv
import os
import math
import time

#index of the headers
user_id_idx = 0
url_num_idx = 1
cache_size_array_idx = 2
hit_set_size_array_idx = 3
miss_set_size_array_idx = 4
hit_array_idx = 5
miss_array_idx = 6
prefetch_array_idx = 7
precision_array_idx = 8
recall_array_idx = 9
runtime_array_idx = 10

def write_csv(line_list, output):
    with open(output, mode='a') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',')
        csv_writer.writerow(line_list)


def read_csv(input, output):
    sw_size = os.path.basename(input).split('.')[1]
    with open(input) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if(row[0] != 'None'):
                    user_id = row[user_id_idx]
                    url_num = int(row[url_num_idx])
                    cache_array = list(map(int, row[cache_size_array_idx].split()))
                    hit_set_array = list(map(int, row[hit_set_size_array_idx].split()))
                    miss_set_array = list(map(int, row[miss_set_size_array_idx].split()))
                    hit_num_array = list(map(int, row[hit_array_idx].split()))
                    miss_num_array = list(map(int, row[miss_array_idx].split()))
                    static_precision_array = list(map(float, row[precision_array_idx].split()))
                    dynamic_recall_array = list(map(float, row[recall_array_idx].split()))
                    runtime_array = list(map(float, row[runtime_array_idx].split()))

                    #unfold the multiple runs when sliding the window
                    for i in range(len(cache_array)):

                        cache = cache_array[i]
                        hit_set = hit_set_array[i]
                        miss_set = miss_set_array[i]
                        hit_num = hit_num_array[i]
                        miss_num = miss_num_array[i]
                        runtime = runtime_array[i]
                        static_precision = hit_set / cache if cache != 0 else 0.0
                        dynamic_recall = hit_num / (hit_num + miss_num)

                        if not math.isclose(static_precision, static_precision_array[i], abs_tol=0.01):
                            print(f'static precision is wrong!!!!!! user id = {user_id}')
                            print(static_precision)
                            print(static_precision_array[i])
                        if not math.isclose(dynamic_recall, dynamic_recall_array[i], abs_tol=0.01):
                            print(f'dynamic recall is wrong!!!!!! user id = {user_id}')

                        # add new metrics
                        dynamic_precision = hit_num / (hit_num + cache - hit_set) if (hit_num + cache - hit_set) != 0 else 0.0
                        static_recall = hit_set / (hit_set + miss_set)
                        hit_importance = hit_num / hit_set if hit_set != 0 else 0.0
                        miss_importance = miss_num / miss_set if miss_set != 0 else 0.0

                        csv_line = []
                        csv_line.append(user_id)
                        csv_line.append(url_num)
                        csv_line.append(sw_size)
                        csv_line.append(cache)
                        csv_line.append(hit_set)
                        csv_line.append(miss_set)
                        csv_line.append(hit_num)
                        csv_line.append(miss_num)
                        csv_line.append(static_precision)
                        csv_line.append(dynamic_precision)
                        csv_line.append(static_recall)
                        csv_line.append(dynamic_recall)
                        csv_line.append(hit_importance)
                        csv_line.append(miss_importance)
                        csv_line.append(runtime)

                        write_csv(csv_line, output)
                    line_count += 1

        print(f'Processed {line_count} users in {input}.')

if __name__ == "__main__":
    # input_file =  '/Users/felicitia/Documents/Research/ASE2019/ASE_data_sheets/SW_DG_0.8new/50.0.8.csv'
    print('please specify the directory:')
    directory = input()
    print('please specify the output file')
    output_file = input()
    print('please specify the prefix of the input files')
    prefix = input()
    # read_csv('/Users/felicitia/Documents/Research/ASE2019/Final_SW/DG0.8/dg.500.0.8.csv', output_file)
    headers = []
    headers.append('user.id')
    headers.append('url')
    headers.append('sw.size')
    headers.append('cache.size')
    headers.append('hit.set')
    headers.append('miss.set')
    headers.append('hit.num')
    headers.append('miss.num')
    headers.append('static.precision')
    headers.append('dynamic.precision')
    headers.append('static.recall')
    headers.append('dynamic.recall')
    headers.append('hit.importance')
    headers.append('miss.importance')
    headers.append('runtime')
    write_csv(headers, output_file)
    for input_file in os.listdir(directory):
        if input_file.startswith(prefix):
            print(f'processing {os.path.join(directory, input_file)}')
            before = time.time()
            read_csv(os.path.join(directory, input_file), output_file)
            after = time.time()
            print(f'processing time = {after-before}')
            # continue
