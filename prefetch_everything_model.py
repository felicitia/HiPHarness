class PrefetchEverythingModel:
    """
     Add "prefetch everything" algorithm (training ratio = 0.8): 
     (1) cache set is initialized as all the unique URLs in the training set. 
     (2) as you iterate the test set (e.g., request 
        i), first compare if it's in the cache 
        (to calculate hit, miss, hit set, miss set),
         then put request i in the cache set. 
         You should run this "prefetch everything" algorithm with the same dataset 
         as the new DG sliding window in 1 
         (i.e., users 50 <= #URL < 3932, window sizes: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)
    """
    
    def __init__(self):
        self.cacheset = set()

    def feed(self,url):
        self.cacheset.add(url)

    def predict(self,history):
        return list(self.cacheset)

class DomainSplitPEModel:
    def __init__(self):
        self.instances = {}

    def get_pe_instance(self, domain):
        if domain not in self.instances:
            self.instances[domain] = PrefetchEverythingModel()
        return self.instances[domain]

    def feed(self, url):
        domain = url.split("/", 1)[0]
        self.get_pe_instance(domain).feed(url)

    def predict(self, history):
        grouped_urls = {}
        for his_url in history:
            domain = his_url.split("/", 1)[0]
            if domain not in grouped_urls:
                grouped_urls[domain] = []
            grouped_urls[domain].append(his_url)
        result = []
        for domain, urls in grouped_urls.items():
            result = result + self.get_pe_instance(domain).predict(urls[-1])
        return result

