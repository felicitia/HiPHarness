
class MPModel:
    def __init__(self,m,n,policy,dependency_threshold,frequency_of_change_threshold):
        self.m = m
        self.n = n
        self.policy = policy
        self.dependency_threshold = dependency_threshold
        self.frequency_of_change_threshold = frequency_of_change_threshold
        self.trained = False
        self.urls = []
        self.url_popularity_list = {}

    def feed(self,url):
        self.urls.append(url)

    def train(self):
        # for every request in client's training log data
        for idx,current_url in enumerate(self.urls):
            
            # set client's current requests as active
            active_url = current_url

            # for each client's requests within n requests after active
            for url in self.urls[idx+1:idx+1+self.n]:

                if active_url in self.url_popularity_list:
                    self.url_popularity_list[active_url] = {}
                

                acitve_popularity_list = self.url_popularity_list[active_url] 
                # if request not in active requests' n-next popularity list
                if url not in acitve_popularity_list:
                    # insert request in active request's n-next popularity list
                    # request popularity = 1
                    acitve_popularity_list[url] = 1
                else:
                    # if request in active request's n-next popularity list
                    # request popularity ++
                    acitve_popularity_list[url] += 1
            
        # sort active request's n-next popularity list by popularity
        for  key,popularity_list in self.url_popularity_list.items():
            self.url_popularity_list[key] = sorted(popularity_list.items(),key=lambda _:_[1],reverse=True)
        self.trained = True

    def predict(self,history):
        if not self.trained:
            self.train()
            
        results = []
        
        # set client's current request as active
        active_url = history[0]

        # for each of ** m most ** popular requests in active request's n-next popularity list
        for url,popularity in self.url_popularity_list[active_url][0:self.m]:
            if self.policy == "aggressive":
                results.append(url)
            # size whose size ??
            # elif policy == "strict":
            #     if 
            # if (policy == strict) && (size > average size):
            #if (dependency > dependency threshold) && (frequency of change < frequency
            #of change threshold):
            #add request in set of predicted pages



    