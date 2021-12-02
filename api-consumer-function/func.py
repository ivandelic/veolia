import io
import sys
import urllib.request
import json
import logging
from fdk import response
import argparse
import collections
import os
import apimanager
import osmanager

logging.basicConfig(level=logging.DEBUG)

defargs = {'url': 'https://api.hnb.hr/tecajn/v1?valuta=EUR'}
args = collections.ChainMap(os.environ, defargs)

def handler(ctx, data: io.BytesIO = None):
    exrate = apimanager.getApi(args.get("url"))
    jsonobj = {}
    jsonobj["rate"] = str(exrate)
    content = json.dumps(jsonobj)
    if args.get("OCI_RESOURCE_PRINCIPAL_VERSION") is not None:
        osmanager.putobject(bucketName=args.get("bucketNameStaging"), objectName=args.get("objectNameStaging"), content=content)
    return response.Response(ctx, response_data=json.dumps({"NationalExchangeRate": str(exrate)}), headers={"Content-Type": "application/json"})

if __name__ == "__main__":
    handler(None)