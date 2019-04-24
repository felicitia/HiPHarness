import os
import pdb
import json
import collections
import networkx as nx
import time

from itertools import islice


class DGModel:
    def __init__(self, window_size=5, weight_threshold=0.5):

        self.G = nx.DiGraph()
        self.window_size = window_size
        self.weight_threshold = weight_threshold
        self.url_buffer = []
        self.line_count = 0

    def feed(self, url):
        url_buffer = self.url_buffer
        if self.line_count < self.window_size:
            url_buffer.append(url)
            if self.line_count == self.window_size - 1:
                # print('url buffer: ', url_buffer, line_count)
                self.update()
            # update the buffer
        else:
            url_buffer.pop(0)
            url_buffer.append(url)
            # print('url buffer: ', url_buffer, line_count)
            self.update()
        self.line_count += 1

    def update(self):
        DG = self.G
        url_buffer = self.url_buffer
        head_node = url_buffer[0]
        successors = set()
        i = 1
        while i < len(url_buffer):
            if url_buffer[i] != head_node:
                successors.add(url_buffer[i])
            i += 1
        for suc in successors:
            if DG.has_edge(head_node, suc):
                old_weight = DG[head_node][suc]['weight']
                head_count = DG.nodes[head_node]['count']
                new_weight = (old_weight * head_count + 1) / (head_count + 1)
                DG[head_node][suc]['weight'] = new_weight
            else:  # edge doesn't exist
                if DG.has_node(head_node):
                    DG.add_edge(head_node, suc)
                    # head_node has outgoing edges
                    if 'count' in DG.nodes[head_node]:
                        DG[head_node][suc]['weight'] = 1 / \
                            (DG.nodes[head_node]['count'] + 1)
                    else:
                        DG[head_node][suc][
                            'weight'] = 1  # initial weight for new edge (old_weight*head_count + 1) / (head_count + 1)
                        # initial count for new node
                        DG.nodes[head_node]['count'] = 0
                else:
                    DG.add_edge(head_node, suc)
                    DG[head_node][suc][
                        'weight'] = 1  # initial weight for new edge (old_weight*head_count + 1) / (head_count + 1)
                    # initial count for new node
                    DG.nodes[head_node]['count'] = 0

        # when the whole url_buffer has the same url, then head_node might not have 'count' attribute
        if not DG.has_node(head_node):
            DG.add_node(head_node)
        if len(successors) == 0 and 'count' not in DG.nodes[head_node]:
            DG.nodes[head_node]['count'] = 0

        DG.nodes[head_node]['count'] += 1

    def predict(self, url):
        result = []
        if self.G.has_node(url):
            for suc in self.G.successors(url):
                if self.G[url][suc]['weight'] > self.weight_threshold:
                    result.append(url)
        return result


class ModelTester:
    cacheset = set()
    hitset = set()
    hitcount = 0
    misscount = 0
    prefetchcount = 0
    model = None
    train_ratio = 0
    idx_begin_test = 0
    urls = []

    def __init__(self, model, train_ratio):
        self.model = model
        self.train_ratio = train_ratio
        self.cacheset = set()
        self.hitset = set()

    def load_urls(self, urls):
        self.urls = urls
        self.idx_begin_test = len(self.urls) * self.train_ratio

    def train_and_test(self):
        for idx, url in enumerate(self.urls):
            if idx < self.idx_begin_test:
                self.model.feed(url)
                if idx == self.idx_begin_test - 1:
                    history_url = url
            else:
                # prefetch engine here
                predicted_urls = self.model.predict(history_url)
                for predicted_url in predicted_urls:
                    if not (predicted_url in self.cacheset):
                        self.cacheset.add(predicted_url)
                        self.prefetchcount += 1
                if url in self.cacheset:
                    self.hitcount += 1
                    self.hitset.add(url)
                else:
                    self.misscount += 1
                history_url = url
                self.model.feed(url)

        return len(self.cacheset), len(self.hitset), self.hitcount, self.misscount, self.prefetchcount


DG_WINDOW_SIZE = 5
DG_WEIGHT_THRESHOLD = 0.8
TRAIN_RATIO = 0.8
print("window_size={} url_buffer={} train_ratio={}\n".format(
    DG_WINDOW_SIZE, DG_WEIGHT_THRESHOLD, TRAIN_RATIO))


count = 0
prefix = "./url_records7"
for dirname in os.listdir(prefix):
    if dirname.startswith("account="):
        count += 1
        for filename in os.listdir(prefix+"/"+dirname):
            if filename.endswith("crc"):
                continue
            file = open(prefix+"/"+dirname+"/"+filename, "rb")

            urls = []
            try:
                dg = DGModel(DG_WINDOW_SIZE, DG_WEIGHT_THRESHOLD)
                urls = []
                for line in file.readlines():
                    try:
                        record = json.loads(str(line.decode("utf-8").strip()))
                    except Exception as e:
                        print(e)
                    url = record["host"] + record["URL"]
                    urls.append(url)

                t0 = time.time()
                # for all urls
                tester = ModelTester(dg, TRAIN_RATIO)
                tester.load_urls(urls)
                cachesize, histsize, hitcount, misscount, prefetchcount = tester.train_and_test()
                precision = histsize / (cachesize or 1)
                recall = tester.hitcount / len(urls)
                precision_differ_sizes = []
                recall_differ_sizes = []

                # for first xxx url records
                for size in [50, 100, 200, 300, 400, 500]:
                    tester2 = ModelTester(
                        DGModel(DG_WINDOW_SIZE, DG_WEIGHT_THRESHOLD), TRAIN_RATIO)
                    tester2.load_urls(urls[0:size])
                    tester2.train_and_test()
                    if len(tester2.cacheset) < 1:
                        precision_differ_sizes.append("NO CACHE")
                    else:
                        precision_differ_sizes.append((len(
                            tester2.hitset) / (len(tester2.cacheset) or 1)))
                    recall_differ_sizes.append(tester2.hitcount / size)

                timecost = time.time() - t0
                print(dirname, len(urls), cachesize, histsize,
                      hitcount, misscount, prefetchcount, precision, recall, precision_differ_sizes, recall_differ_sizes, timecost)
            except Exception as e:
                print(e)