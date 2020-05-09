

class DomainFilter:
    def __init__(self,source_file = "./domain_unique_percent_list.csv",default_max_percent = 0.9):
        self.domain_unique_percent_map = {}
        self.max_percent = default_max_percent
        f = open(source_file,"r")
        
        for l in f.readlines():
            [domain,p] = l.split(",")
            self.domain_unique_percent_map[domain] = float(p)
        f.close()

    def set_max_percent(self,percent):
        self.max_percent = percent
    
    def filter(self,url):
        domain = url.split("/", 1)[0]
        if domain in self.domain_unique_percent_map:
            return self.domain_unique_percent_map[domain] < self.max_percent
        return True
            
