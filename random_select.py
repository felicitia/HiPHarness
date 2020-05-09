import os
import json
DATAPATH = "./data/"
groups = [[], [], [], [], [], [], [], [], [], []]
for dirname in os.listdir(DATAPATH):
    f = open(DATAPATH+dirname, "r")
    urls = f.read().split("\n")
    n = len(urls)
    for i in range(0, 10):
        groups[i].append((dirname, n, abs(n - (i+1)*1000)))

for i in range(0, 10):
    groups[i].sort(key=lambda v: v[2])

json.dump(groups, open("./groups.json", "w"))
