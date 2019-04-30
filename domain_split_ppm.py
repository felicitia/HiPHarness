import networkx as nx
import os
import json
import time


class PPMModel:
    def __init__(self, order, threshold):
        self.threshold = threshold
        self.max_order = order
        self.G = nx.DiGraph()
        self.G.add_node("/", hit_count=0, label="[[root]]", order=0)
        self.current_nodes = ["/"]

    def feed(self, url):
        self.add_node(url)

    def predict(self, history):
        G = self.G
        cur_ctx = "/"
        t = 0
        for his_url in history:
            for node in G[cur_ctx]:
                if G.node[node]["label"] == his_url:
                    t += G.node[node]["hit_count"]
                    cur_ctx = node
                    break
            else:
                cur_ctx = "/"
                t = 0
        result = []
        for node in G[cur_ctx]:
            if t + G.node[node]["hit_count"] > self.threshold:
                result.append(G.node[node]["label"])
        return result

    def add_node(self, label):
        G = self.G
        current_nodes_count = len(self.current_nodes)
        for i in range(0, current_nodes_count):
            current_node = self.current_nodes[i]
            node = None
            # current_node_leaf_count = 0
            # current_node_fist_leaf = None
            for sub_node in G[current_node]:
                # if len(G[sub_node]) == 0:
                #     # current_node_leaf_count += 1
                #     # if not current_node_fist_leaf:
                #     current_node_fist_leaf = sub_node
                if G.node[sub_node]["label"] == label:
                    G.node[sub_node]["hit_count"] += 1
                    node = sub_node
                    break
            else:
                current_node_order = G.node[current_node]["order"]
                if current_node_order < self.max_order:
                    node = current_node + label + "/"
                    # if current_node_leaf_count > self.node_max_leaf_count:
                    #     G.remove_node(current_node_fist_leaf)
                    #     self.current_nodes.remove(current_node_fist_leaf)
                    G.add_node(node, hit_count=1, label=label, order=current_node_order + 1)
                    G.add_edge(current_node, node)
            if node:
                if current_node == "/":
                    self.current_nodes.append(node)
                else:
                    self.current_nodes[i] = node

    def readable_labels(self):
        G = self.G
        result = {}
        for node in G.nodes:
            result[node] = G.node[node]["label"] + "/" + str(G.node[node]["hit_count"])
        return result


class DomainSplitPPMModel:
    def __init__(self, order, threshold):
        self.order = order
        self.threshold = threshold
        self.instances = {}

    def get_ppm_instance(self, domain):
        if domain not in self.instances:
            self.instances[domain] = PPMModel(self.order, self.threshold)
        return self.instances[domain]

    def feed(self, url):
        domain = url.split("/", 1)[0]
        self.get_ppm_instance(domain).add_node(url)

    def predict(self, history):
        grouped_urls = {}
        for his_url in history:
            domain = his_url.split("/", 1)[0]
            if domain not in grouped_urls:
                grouped_urls[domain] = []
            grouped_urls[domain].append(his_url)
        result = []
        for domain, urls in grouped_urls.items():
            result = result + self.get_ppm_instance(domain).predict(urls)
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
        # history_url = None
        for idx, url in enumerate(self.urls):
            # if idx < self.idx_begin_test:
            #     self.model.feed(url)
            #     if idx == self.idx_begin_test - 1:
            #         history_url = url
            # else:
            # prefetch engine here
            predicted_urls = self.model.predict(self.urls[idx - 10:10])
            for predicted_url in predicted_urls:
                if not (predicted_url in self.cacheset):
                    self.cacheset.add(predicted_url)
                    self.prefetchcount += 1
            if url in self.cacheset:
                self.hitcount += 1
                self.hitset.add(url)
            else:
                self.misscount += 1
            # history_url = url
            self.model.feed(url)

        return len(self.cacheset), len(self.hitset), self.hitcount, self.misscount, self.prefetchcount


PPM_ORDER = 5
PPM_THRESHOLD = 3
TRAIN_RATIO = 0.8

count = 0
prefix = "/home/yinsiwei/url_cleanup_xxx_json"
for dirname in os.listdir(prefix):
    if dirname.startswith("account="):
        count += 1
        for filename in os.listdir(prefix + "/" + dirname):
            if filename.endswith("crc"):
                continue
            file = open(prefix + "/" + dirname + "/" + filename, "rb")

            urls = []
            try:
                ppm = DomainSplitPPMModel(PPM_ORDER, PPM_THRESHOLD)
                urls = []
                for line in file.readlines():
                    record = None
                    try:
                        record = json.loads(str(line.decode("utf-8").strip()))
                    except Exception as e:
                        print(e)

                    url = record["host"] + record["URL"]
                    urls.append(url)

                t0 = time.time()
                # for all urls
                tester = ModelTester(ppm, TRAIN_RATIO)
                tester.load_urls(urls)
                cachesize, histsize, hitcount, misscount, prefetchcount = tester.train_and_test()
                precision = histsize / (cachesize or 1)
                recall = (hitcount / misscount + hitcount) if (misscount + hitcount) else 0

                # for first xxx url records

                timecost = time.time() - t0
                print(",".join([dirname, str(len(urls)), str(cachesize), str(histsize),
                      str(hitcount), str(misscount), str(prefetchcount), str(precision), str(recall), str(timecost)]))
            except Exception as e:
                print(e)
