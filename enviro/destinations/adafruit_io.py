from enviro import logging
import urequests, ujson, os, time
import config

def upload_readings():
  username = config.adafruit_io_username
  headers = {'X-AIO-Key': config.adafruit_io_key, 'Content-Type': 'application/json'}

  nickname = config.nickname

  for cache_file in os.ilistdir("uploads"):
    cache_file = cache_file[0]
    try:
      with open(f"uploads/{cache_file}", "r") as f:
        timestamp = cache_file.split(".")[0]
        data = ujson.load(f)

        timestamp = timestamp.replace(" ", "T") + "Z"
        payload = {
          "created_at": timestamp,
          "feeds": []
        }
        for key, value in data.items():
          key = key.replace("_", "-")
          payload["feeds"].append({
            "key": f"{nickname}-{key}",
            "value": value
          })

        url = f"http://io.adafruit.com/api/v2/{username}/groups/enviro/data"
        result = urequests.post(url, json=payload, headers=headers)
        if result.status_code == 429:
          result.close()
          logging.info(f"  - rate limited, cooling off for thirty seconds")
          time.sleep(30)
          # try the request again
          result = urequests.post(url, json=payload, headers=headers)
          # TODO currently if this fails a second time it carrys on to the next file. Is this what we want?

        if result.status_code == 200:
          os.remove(f"uploads/{cache_file}")
          logging.info(f"  - uploaded {cache_file}")
        else:
          logging.error(f"! failed to upload '{cache_file}' ({result.status_code} {result.reason})", cache_file)
          # TODO should this break out of the file loop to avoid uploading files out-of-order?

        result.close()
    except OSError as e:
      logging.error(f"  - failed to upload '{cache_file}'")
