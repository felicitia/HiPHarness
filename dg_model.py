import networkx as nx

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

    def predict(self, history):
        url = history[0]
        result = []
        if self.G.has_node(url):
            for suc in self.G.successors(url):
                if self.G[url][suc]['weight'] > self.weight_threshold:
                    result.append(url)
        return result