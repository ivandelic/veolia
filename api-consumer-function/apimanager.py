import urllib.request
import json
import logging

logging.basicConfig(level=logging.DEBUG)

def getApi(address):
    exrate = 0
    try:
        response = urllib.request.urlopen(address).read()
        obj = json.loads(response)
        exrate = obj[0]["Prodajni za devize"]
        logging.getLogger().info("Exchange rate is " + exrate)
    except Exception as e:
        logging.getLogger().error("Unable to load data from " + address)
        logging.getLogger().error(str(e.message))
    return exrate