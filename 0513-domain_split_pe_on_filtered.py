

import os
import json
import argparse

from prefetch_everything_model import DomainSplitPEModel
from sliding_window_model_tester import SlidingWindowModelTester
from url_record_reader import URLRecordReader



def every_test_user(reader, account, model_build_func,train_ratio):
    urls = reader.get_urls_by_account(account)
    total = len(urls)
    if total < 10 or total >= 3932:
        return None
    tester = SlidingWindowModelTester(len(urls), model_build_func, 1)
    tester.load_urls(urls)
    line = [account, str(len(urls)), [], [], [], [], [], [], [], [], []]
    for stage in tester.train_and_test(train_ratio):
        if stage is not False:
            for idx, col in enumerate(stage):
                line[idx + 2].append(str(col))

    for i in range(2, 11):
        line[i] = " ".join(line[i])
    return ",".join(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DG Prefetch~')
    parser.add_argument('--data-dir', type=str, default="./data")
    parser.add_argument('--train-ratio', type=float, default=0.8)
    # parser.add_argument('--sliding-window-size', type=int, default=50)

    args = parser.parse_args()
    reader = URLRecordReader(args.data_dir)
    model_build_func = lambda :DomainSplitPEModel()
    print("user_id,#url,cache_size_array,hit_set_size_array,miss_set_size_array,hit_array,miss_array,prefetch_array,precision_array,recall_array,running_time_array")
    for account in reader.accounts():

        r = every_test_user(reader,account,model_build_func,args.train_ratio)
        if r:
            print(r)



