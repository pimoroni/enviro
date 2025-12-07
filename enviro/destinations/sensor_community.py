# Inspired by 
# https://github.com/sikorka/enviro/blob/main/micropython/pico/enviroplus/sensors/sensorcommunity/main.py

from enviro import logging
from enviro.constants import *
import urequests
import config
import ujson
      
def log_destination():
  logging.info(f"> uploading cached readings to sensor.community: {config.sensor_community_id}")


def process_upload(data, headers):
    url = "https://api.sensor.community/v1/push-sensor-data/"
    try:
        result = urequests.post(url, data=data, headers=headers, timeout=30)
        error_message = ""    
        try:
            error_message = result.json()['error']
        except (TypeError, KeyError):
            pass
        
        result.close()

    except Exception as exc:
        import sys, io
        buf = io.StringIO()
        sys.print_exception(exc, buf)
        logging.debug(f"  - an exception occurred when uploading.", buf.getvalue())
        return UPLOAD_FAILED
    
    return UPLOAD_SUCCESS


def upload_reading(wrapper):

    id = config.sensor_community_id
    reading = wrapper["readings"]
    pm_values = {}
    pm_values["P2"] = f"{reading['pm2_5']:.0f}"
    pm_values["P1"] = f"{reading['pm10']:.0f}"
    pm_values["P0"] = f"{reading['pm1']:.0f}"
    pm_values_json = [{"value_type": key, "value": val} for key, val in pm_values.items()]

    
    payload={
        "software_version": "enviro-plus 1.0.0",
        "sensordatavalues": pm_values_json
    }
    headers={
        "X-PIN": "1",
        "X-Sensor": id,
        "Content-Type": "application/json",
        "cache-control": "no-cache"
    }

    result = process_upload(ujson.dumps(payload).encode(), headers)
    if result != UPLOAD_SUCCESS:
        return result

    bme_values = {}
    bme_values["temperature"] = f"{reading['temperature']:.1f}"
    bme_values["pressure"] = f"{reading['pressure']*100:.0f}" # pressure in Pa (not hPa) in sensor.community
    bme_values["humidity"] = f"{reading['humidity']:.0f}"
    bme_values_json = [{"value_type": key, "value": val} for key, val in bme_values.items()]

    payload={
        "software_version": "enviro-plus 1.0.0",
        "sensordatavalues": bme_values_json
    }
    headers={
        "X-PIN": "11",
        "X-Sensor": id,
        "Content-Type": "application/json",
        "cache-control": "no-cache"
    }
    
    result = process_upload(ujson.dumps(payload).encode(), headers)
    if result != UPLOAD_SUCCESS:
        return result

    return UPLOAD_SUCCESS