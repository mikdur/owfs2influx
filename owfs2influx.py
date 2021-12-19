#!/usr/bin/env python3

import pyownet, yaml, sys, time

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import argparse


parser = argparse.ArgumentParser()

parser.add_argument("--config", "-c", help="Config file (owfs2influx.yaml)",
                        default="owfs2influx.yaml")

args = parser.parse_args()


# Read config file

with open("owfs2influx.yaml") as conf:
    config = yaml.load(conf, Loader=yaml.FullLoader)

# Extract server/port and delete keys from config
server = config.pop("server", "localhost")
port = config.pop("port", 4304 )
influx_server = config.pop("influx_server", None)
token = config.pop("token")
bucket = config.pop("bucket")
org = config.pop("influx_org")
report_interval = float(config.pop("report_interval", "30"))





# Connect to owfs server
ow = pyownet.protocol.proxy(server, port=port)

# Connect to influxdb
client = InfluxDBClient(url=influx_server, token=token)
write_client = client.write_api()

while True:
    start_time = time.perf_counter()
    ow.write("/uncached/simultaneous/temperature", b"1")
    time.sleep(2)
    # Query all defined
    for sensor in config.keys():
        for attr in config[sensor]:
            try:
                val = float(ow.read( "/uncached/" + sensor + attr["attribute"] ))
                ow_type = ow.read( "/" + sensor + "/type")
                if val == 85:
                    raise Exception("Sensor failure")
                point = Point("owfs_data")
                point = point.tag("ow_type", ow_type)
                point = point.tag("ow_id", sensor)
        
                for t,v in attr.get("tags", dict()).items():
                    point = point.tag(t, v)
                    point = point.field(attr.get("field", "val"), val)

                    point = point.time(datetime.utcnow(), WritePrecision.NS)
            except:
                print("Sensor %s failed" % (sensor), file=sys.stderr)
            write_client.write(bucket, org, point)
    end_time = time.perf_counter()
    
    #print("Sleeping {} seconds".format(report_interval - ( end_time - start_time) ))
    if end_time - start_time < report_interval:
        time.sleep(report_interval - (end_time - start_time))
        
write_client.close()

