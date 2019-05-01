import time


class SlidingWindowModelTester:
    urls = []

    def __init__(self, window_size, model_build_func, history_count=10):
        """
        Sliding Window Prefetching
        :param window_size:   (“URL size” = 50, 100, 200, 300, 400, 500)
        :param model_build_func: a function that builds a model without arguments.
        :param history_count: how many urls used for predict engine .It's 1 for DG.
        """
        self.window_size = window_size
        self.model_build_func = model_build_func

        self.history_count = history_count

    def load_urls(self, urls):
        """
        load urls
        :param urls:
        :return:
        """
        self.urls = urls

    def train_and_test(self, train_ratio=0.8):
        total_urls = len(self.urls)

        cache_set = set()
        hit_set = set()
        miss_set = set()
        hit_count = 0
        miss_count = 0
        prefetch_count = 0

        # train model with first (window_size * train_ratio) urls
        model = self.model_build_func()
        for url in self.urls[0:int(self.window_size * train_ratio)]:
            model.feed(url)

        begin = int(self.window_size * train_ratio)
        end = self.window_size
        t0 = time.time()

        while end < total_urls:
            while begin < end:
                # predict engine
                predict_urls = model.predict(self.urls[begin - self.history_count:begin])
                for predict_url in predict_urls:
                    if predict_url not in cache_set:
                        cache_set.add(predict_url)
                        prefetch_count += 1

                current_url = self.urls[begin]
                if current_url in cache_set:
                    hit_set.add(current_url)
                    hit_count += 1
                else:
                    # add miss set
                    miss_set.add(current_url)
                    miss_count += 1

                # continuous training
                model.feed(current_url)

                begin += 1

            precision = len(hit_set) / (len(hit_set) or 1)
            recall = (hit_count / miss_count + hit_count) if (miss_count + hit_count) else 0

            # yield stage result
            yield len(cache_set), len(hit_set), len(
                miss_set), hit_count, miss_count, prefetch_count, precision, recall, time.time() - t0

            # sliding
            end += int(self.window_size * train_ratio)

            # should I clear all set here ?
            # cache_set = set()
            # hi_set = set() ....

        return False
