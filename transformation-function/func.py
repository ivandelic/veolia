import io
import json
import logging
from fdk import response
import collections
import os
import osmanager
import datetime

logging.basicConfig(level=logging.DEBUG)

defargs = {'url': 'https://api.hnb.hr/tecajn/v1?valuta=EUR'}
args = collections.ChainMap(os.environ, defargs)

def handler(ctx, data: io.BytesIO = None):
    try:
        eventbody = json.loads(data.getvalue())
        eventtype = eventbody.get("eventType")

        if eventtype is not None and eventtype == "com.oraclecloud.objectstorage.createobject":
            stageobj = osmanager.readobject(eventbody["data"]["additionalDetails"]["bucketName"], eventbody["data"]["resourceName"])
        else:
            stageobj = osmanager.readobject(args.get("bucketNameStaging"), args.get("objectNameStaging"))

        if stageobj.status == 200:
            stagejson = json.loads(stageobj.data.text)
            logging.getLogger().info("Found an exchange rate: " + stagejson["rate"])
            lakeobj = osmanager.readobject(args.get("bucketNameLake"), args.get("objectNameLake"))
            
            if lakeobj is None:
                lakeobj = osmanager.putobject(args.get("bucketNameLake"), args.get("objectNameLake"), {"values": []})
            lakejson = json.loads(lakeobj.data.text)
            lakejson.get("values").append({"time": str(datetime.datetime.utcnow().isoformat()), "rate": stagejson["rate"]})
            osmanager.putobject(args.get("bucketNameLake"), args.get("objectNameLake"), lakejson)
            return response.Response(ctx, response_data=json.dumps({"Lake updated": str(lakejson)}), headers={"Content-Type": "application/json"})
        else:
            logging.getLogger().info("Unable to find staging object")
            return response.Response(ctx, response_data=json.dumps({"message": "Unable to find staging object"}), headers={"Content-Type": "application/json"})
    except (Exception, ValueError) as ex:
        logging.getLogger().error("error parsing json payload: " + str(ex))
        return response.Response(ctx, response_data=json.dumps({"message": "Error" + str(ex)}), headers={"Content-Type": "application/json"})