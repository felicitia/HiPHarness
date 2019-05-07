import os
import json
import argparse

from prefetch_everything_model import PrefetchEverythingModel
from sliding_window_model_tester import SlidingWindowModelTester
from url_record_reader import URLRecordReader
from sliding_window_every_tester import e_test_user



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DG Prefetch~')
    parser.add_argument('--data-dir', type=str, default="./data")
    parser.add_argument('--train-ratio', type=float, default=0.8)
    parser.add_argument('--sliding-window-size', type=int, default=50)

    args = parser.parse_args()
    reader = URLRecordReader(args.data_dir)
    model_build_func = lambda :PrefetchEverythingModel()
    print("user_id,#url,cache_size_array,hit_set_size_array,miss_set_size_array,hit_array,miss_array,prefetch_array,precision_array,recall_array,running_time_array")
    for account in reader.accounts():
        r = e_test_user(reader,account,model_build_func,args.sliding_window_size,args.train_ratio)
        if r:
            print(r)









#
#
#
#
# print("Use args", args)
# model_build_func = lambda: DGModel(args.dg_window_size, args.dg_weight_threshold)
# prefix = "./data"
# for dirname in os.listdir(prefix):
#     if dirname.startswith("account="):
#
#         for filename in os.listdir(prefix + "/" + dirname):
#             if filename.endswith("crc"):
#                 continue
#             file = open(prefix + "/" + dirname + "/" + filename, "rb")
#
#             urls = []
#             try:
#                 urls = []
#                 for line in file.readlines():
#                     record = None
#                     try:
#                         record = json.loads(str(line.decode("utf-8").strip()))
#                     except Exception as e:
#                         print(e)
#
#                     url = record["host"] + record["URL"]
#                     urls.append(url)
#
#                 if len(urls) > 1000 or len(urls)  < args.sliding_window_size:
#                     continue
#
#                 tester = SlidingWindowModelTester(args.sliding_window_size, model_build_func, history_count=1)
#                 tester.load_urls(urls)
#                 line = [dirname, str(len(urls)), [], [], [], [], [], [], [], [], []]
#                 for stage in tester.train_and_test(args.train_ratio):
#                     if stage is not False:
#                         for idx, col in enumerate(stage):
#                             line[idx + 2].append(str(col))
#
#
#                 for i in range(2, 11):
#                     line[i] = " ".join(line[i])
#                 print(",".join(line))
#
#             except Exception as e:
#                 raise e
