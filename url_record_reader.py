import os
import json
from domain_filter import DomainFilter
import itertools


class URLRecordReader:
    # An auxiliary class for reading data produced by spark.

    def __init__(self, base, max_domain_unique_percent=1, use_top_domain=False, use_most_domain=False, use_top_url=False, use_time_split=False, group=False):
        """

        :param base: the location of the spark output dir
        """
        self.base = base
        self.filter = DomainFilter()
        self.filter.set_max_percent(max_domain_unique_percent)
        self.use_top_domain = use_top_domain
        self.use_most_domain = use_most_domain
        self.use_top_url = use_top_url
        self.use_time_split = use_time_split
        self.group = group

    def get_urls_by_account(self, account):
        urls = []
        result = []
        with open(self.base + "/" + account, "r") as f:
            urls = list(
                filter(lambda url: self.filter.filter(url), f.read().split("\n")))
        # print(len(urls),end=",")
        if self.use_time_split:
            n = int(len(urls)/3)
            if self.use_time_split == "old":
                return urls[:n]
            elif self.use_time_split == "mid":
                return urls[n:2*n]
            elif self.use_time_split == "recent":
                return urls[2*n:]
        if self.use_top_domain:
            domains = dict()
            for url in urls:
                domain = url.split("/", 1)[0]
                if domain in domains:
                    domains[domain] += 1
                else:
                    domains[domain] = 1
            d = sorted(domains.items(), key=lambda v: v[1], reverse=True)
            n = int(len(d)*self.use_top_domain)
            if n < 1:
                n = 1
            domains = list(map(lambda v: v[0], d[:n]))
            for url in urls:
                domain = url.split("/", 1)[0]
                if domain in domains:
                    result.append(url)
            return result
        if self.use_most_domain:

            domains = dict()
            for url in urls:
                domain = url.split("/", 1)[0]
                if domain in domains:
                    domains[domain].append(url)
                else:
                    domains[domain] = [url]
            domain_unique = []
            for domain, urlsx in domains.items():
                domain_unique.append((domain, len(set(urlsx))/len(urlsx)))
            d = sorted(domain_unique, key=lambda v: v[1])
            n = int(len(d)*self.use_most_domain)

            if n < 1:
                n = 1
            domains = list(map(lambda v: v[0], d[:n]))

            for url in urls:
                domain = url.split("/", 1)[0]

                if domain in domains:

                    result.append(url)
            return result
        if self.use_top_url:
            t = dict()
            for url in urls:
                if url in t:
                    t[url] += 1
                else:
                    t[url] = 1
            d = sorted(t.items(), key=lambda v: v[1], reverse=True)
            n = int(len(d)*self.use_top_url)

            if n < 1:
                n = 1
            t = list(map(lambda v: v[0], d[:n]))
            # print(len(t))
            for url in urls:
                if url in t:
                    result.append(url)
            return result
        return urls

    def accounts(self):
        c = 0
        if self.group:
            self.group = self.group - 1
            groups = json.load(open("./groups.json", "r"))
            for x in groups[self.group]:
                if c == 50:
                    return
                c += 1
                yield x[0]
        else:
            for dirname in os.listdir(self.base):
                yield dirname
