owfw2influx
===========

A small script used to read Dallas OneWire sensors and submit the data into
an InfluxDB. Easily configured with a yaml config file. 

Setup
-----
- Install pyownet, pyyaml and influxdb_client with pip. 
- Adapt config file to reflect your OneWire network.
- If you want the script to run a system startup, create apropriate init or service file.


