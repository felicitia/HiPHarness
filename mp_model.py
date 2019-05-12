
class MPModel:
    def __init__(self,m=5,n=5):
        self.m = m
        self.n = n
        # self.policy = policy
        # self.dependency_threshold = dependency_threshold
        # self.frequency_of_change_threshold = frequency_of_change_threshold
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

                if active_url not in self.url_popularity_list:
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
        if active_url in  self.url_popularity_list:
            for url,popularity in self.url_popularity_list[active_url][0:self.m]:
                results.append(url)

            # Update model
            self.url_popularity_list[active_url] =  [(pair[0],pair[1]+1) if pair[0]==url else pair for pair in self.url_popularity_list[active_url]]

        # return results
        return results



class DomainSplitMPModel:
    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.instances = {}

    def get_mp_instance(self, domain):
        if domain not in self.instances:
            self.instances[domain] = MPModel(self.m, self.n)
        return self.instances[domain]

    def feed(self, url):
        domain = url.split("/", 1)[0]
        self.get_mp_instance(domain).feed(url)

    def predict(self, history):
        grouped_urls = {}
        for his_url in history:
            domain = his_url.split("/", 1)[0]
            if domain not in grouped_urls:
                grouped_urls[domain] = []
            grouped_urls[domain].append(his_url)
        result = []
        for domain, urls in grouped_urls.items():
            result = result + self.get_mp_instance(domain).predict(urls[-1])
        return result




    