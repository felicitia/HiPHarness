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

        dir = self.base + "/account=" + account
        for filename in os.listdir(dir):
            if filename.endswith("crc"):
                continue
            file = open(dir + "/" + filename, "rb")

            urls = []
            for line in file.readlines():
                record = None
                try:
                    record = json.loads(str(line.decode("utf-8").strip()))
                except Exception as e:
                    print(e)

                url = record["host"] + record["URL"]
                urls.append(url)

            return urls

    def accounts(self):
        for dirname in os.listdir(self.base):
            if dirname.startswith("account="):
                yield dirname[8:]
