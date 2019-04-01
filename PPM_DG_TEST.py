import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import networkx as nx
import os
import json


class PPMModel:
    def __init__(self, order, cache_when_hits):
        self.cache_when_hits = cache_when_hits
        self.max_order = order
        self.G = nx.DiGraph()
        self.G.add_node("/", hit_count=0, label="[[root]]", order=0)
        self.current_nodes = ["/"]

    def feed(self, url):
        self.add_node(url)

    def cache_size(self):
        counter = 0
        G = self.G
        for node in [G.node[x] for x in G]:
            _url = node['label']
            hit_count = node['hit_count']
            if hit_count >= self.cache_when_hits:
                counter = counter + 1
        return counter

    def predict(self, url):
        G = self.G
        for node in [G.node[x] for x in G]:
            _url = node['label']
            hit_count = node['hit_count']
            if url == _url and hit_count >= self.cache_when_hits:
                return True
        return False

    def add_node(self, label):
        G = self.G
        current_nodes_count = len(self.current_nodes)
        for i in range(0, current_nodes_count):
            current_node = self.current_nodes[i]
            node = None
            for sub_node in G[current_node]:
                if G.node[sub_node]["label"] == label:
                    G.node[sub_node]["hit_count"] += 1
                    node = sub_node
                    break
            else:
                current_node_order = G.node[current_node]["order"]
                if current_node_order < self.max_order:
                    node = current_node + label + "/"
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


class DGModel:
    def __init__(self, window_size=5, weight_threshold=0.5):

        self.G = nx.DiGraph()
        self.window_size = window_size
        self.weight_threshold = weight_threshold
        self.url_buffer = []
        self.line_count = 0
        self.cache = set()

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
                        DG[head_node][suc]['weight'] = 1 / (DG.nodes[head_node]['count'] + 1)
                    else:
                        DG[head_node][suc][
                            'weight'] = 1  # initial weight for new edge (old_weight*head_count + 1) / (head_count + 1)
                        DG.nodes[head_node]['count'] = 0  # initial count for new node
                else:
                    DG.add_edge(head_node, suc)
                    DG[head_node][suc][
                        'weight'] = 1  # initial weight for new edge (old_weight*head_count + 1) / (head_count + 1)
                    DG.nodes[head_node]['count'] = 0  # initial count for new node

        # when the whole url_buffer has the same url, then head_node might not have 'count' attribute
        if len(successors) == 0 and 'count' not in DG.nodes[head_node]:
            DG.nodes[head_node]['count'] = 0

        DG.nodes[head_node]['count'] += 1
    def cache_size(self):
        return len(self.cache)
    def predict(self, url):
        if url in self.cache:
            return True
        if self.G.has_node(url):
            for suc in self.G.successors(url):
                if self.G[url][suc]['weight'] > self.weight_threshold:
                    self.cache.add(url)
                    return False
        return False


PPM_ORDER = 2
PPM_CACHE_WHEN_HITS = 10
DG_WINDOW_SIZE = 5
DG_WEIGHT_THRESHOLD = 0.8
TRAIN_RATIO = 0.6
print("window_size={} url_buffer={} train_ratio={}\n".format(DG_WINDOW_SIZE, DG_WEIGHT_THRESHOLD,TRAIN_RATIO))
print("filename,count,DG_CACHE_SIZE,DG_HITS,DG_PRECISION,DG_RECALL")
for filename in os.listdir("."):
    if filename.endswith(".json"):
        file = open(filename, 'r')
        rows = json.load(file)
        if(len(rows)) == 0:
            continue
        idx_begin_test = len(rows) * TRAIN_RATIO
        try:
            ppm = PPMModel(PPM_ORDER, PPM_CACHE_WHEN_HITS)
            dg= DGModel(DG_WINDOW_SIZE, DG_WEIGHT_THRESHOLD)
            # ppm_hit = 0
            dg_hit = 0
            # ppm_hit_set = set()
            dg_hit_set = set()

            for idx, row in enumerate(rows):
                url = row[1] + row[2]
                if not ('GET' in row[2]):
                    continue
                if idx > idx_begin_test:
                    if dg.predict(url):
                        dg_hit = dg_hit + 1
                        dg_hit_set.add(url)
                    # if ppm.predict(url):
                        # ppm_hit = ppm_hit + 1
                        # ppm_hit_set.add(url)
                # ppm.feed(url)
                dg.feed(url)

            print(
                "{} ,{} ," \
                # "PPM_CACHE_SIZE:{} PPM_HITS:{} PPM_PRECISION:{} PPM_RECALL:{}" \
            "{},{},{},{}"
                .format(
                filename, len(rows),
                # ppm.cache_size(), ppm_hit, len(ppm_hit_set) / ppm.cache_size(), ppm_hit / len(rows),
                dg.cache_size(), dg_hit, len(dg_hit_set) /( dg.cache_size() or 1), dg_hit / len(rows), # fix div by zero
            ))

        except Exception as e:
            print(e)
            pass
        finally:
            file.close()
