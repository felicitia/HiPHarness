import os
import json


class URLRecordReader:
    # An auxiliary class for reading data produced by spark.

    def __init__(self, base):
        """

        :param base: the location of the spark output dir
        """
        self.base = base

    def get_urls_by_account(self, account):
        with open(self.base + "/" + account,"r") as f:
            return f.read().split("\n")


    def accounts(self):
        for dirname in os.listdir(self.base):
            yield dirname
