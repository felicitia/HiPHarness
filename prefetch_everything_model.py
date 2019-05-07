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