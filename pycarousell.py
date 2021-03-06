import requests
import json

import myconfigurations as config


class CarousellSearch(object):
    def __init__(self, query_string=None, results=30):
        self.base_url = (config.url)
        self.fields = {
            "count": results,
            "sort": 'recent',
            "query": query_string,
            "lattitude": '',
            "longitdue": '',
            "lte": '',
            "unit": '',
            "country_id": '1880251',
            "country_code": "SG"
        }
        query_fields = json.dumps(self.fields)
        self.query_url = self.base_url + query_fields

    def send_request(self):
        r = requests.get(self.query_url)
        data = json.loads(r.text)
        return data['products']
