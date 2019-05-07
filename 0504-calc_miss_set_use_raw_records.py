

import os
import json
import argparse

from dg_model import DGModel
from sliding_window_model_tester import SlidingWindowModelTester
from url_record_reader2 import URLRecordReader



def dg_test_user(reader, account, model_build_func,train_ratio):
    urls = reader.get_urls_by_account(account)
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
    parser.add_argument('--dg-window-size', type=float, default=5)
    parser.add_argument('--dg-weight-threshold', type=int, default=0.8)
    parser.add_argument('--train-ratio', type=float, default=0.8)
    # parser.add_argument('--sliding-window-size', type=int, default=50)

    args = parser.parse_args()
    reader = URLRecordReader(args.data_dir)
    model_build_func = lambda :DGModel(args.dg_window_size,args.dg_weight_threshold)
    for account in reader.accounts():
        print(dg_test_user(reader,account,model_build_func,args.train_ratio))



