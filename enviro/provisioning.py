import network, os, json, time, machine, sys

import enviro.helpers as helpers
import enviro
from phew import logging, server, redirect, serve_file, render_template, access_point

DOMAIN = "pico.wireless"

# create fresh config file if missing
if not helpers.file_exists("config.py"):
  helpers.copy_file("enviro/config_template.py", "config.py")

# write the current values in config to the config.py file
def write_config():
  with open("config.py", "r") as infile:
    with open("config.py.new", "w") as outfile:
      for line in infile:
        try:
          key, value = line.split("=", 1)
        except ValueError:
          outfile.write(line)
        else:
          key = key.strip()
          try:
            value = getattr(config, key)
          except AttributeError:
            outfile.write(line)
          else:
            outfile.write(f"{key} = {repr(value)}\n")
  os.rename("config.py.new", "config.py")

import config


# detect which board type we are provisioning
model = enviro.model
logging.info("> auto detecting board type")
logging.info("  -", model)


# put board into access point mode
logging.info("> going into access point mode")
ap = access_point("Enviro " + model[:1].upper() + model[1:] + " Setup")
logging.info("  -", ap.ifconfig()[0])


# dns server to catch all dns requests
logging.info("> starting dns server...")
from phew import dns
dns.run_catchall(ap.ifconfig()[0])

logging.info("> creating web server...")


@server.route("/wrong-host-redirect", methods=["GET"])
def wrong_host_redirect(request):
  # if the client requested a resource at the wrong host then present 
  # a meta redirect so that the captive portal browser can be sent to the correct location
  body = "<!DOCTYPE html><head><meta http-equiv=\"refresh\" content=\"0;URL='http://" + DOMAIN + "/provision-welcome'\" /></head>"
  return body


@server.route("/provision-welcome", methods=["GET"])
def provision_welcome(request):
  response = render_template("enviro/html/welcome.html", board=model)
  return response


@server.route("/provision-step-1-nickname", methods=["GET", "POST"])
def provision_step_1_nickname(request):
  if request.method == "POST":
    config.nickname = request.form["nickname"]
    write_config()
    return redirect("http://" + DOMAIN + "/provision-step-2-wifi")
  else:
    return render_template("enviro/html/provision-step-1-nickname.html", board=model)


@server.route("/provision-step-2-wifi", methods=["GET", "POST"])
def provision_step_2_wifi(request):
  if request.method == "POST":
    config.wifi_ssid = request.form["wifi_ssid"]
    config.wifi_password = request.form["wifi_password"]
    write_config()
    return redirect("http://" + DOMAIN + "/provision-step-3-logging")
  else:
    return render_template("enviro/html/provision-step-2-wifi.html", board=model)
  

@server.route("/provision-step-3-logging", methods=["GET", "POST"])
def provision_step_3_logging(request):
  if request.method == "POST":
    config.reading_frequency = int(request.form["reading_frequency"])
    config.upload_frequency = int(request.form["upload_frequency"]) if request.form["upload_frequency"] else None
    write_config()
    return redirect("http://" + DOMAIN + "/provision-step-4-destination")
  else:
    return render_template("enviro/html/provision-step-3-logging.html", board=model)
    

@server.route("/provision-step-4-destination", methods=["GET", "POST"])
def provision_step_4_destination(request):
  if request.method == "POST":
    config.destination = request.form["destination"]

    # custom http endpoint
    config.custom_http_url = request.form["custom_http_url"]
    config.custom_http_username = request.form["custom_http_username"]
    config.custom_http_password = request.form["custom_http_password"]

    # mqtt
    config.mqtt_broker_address = request.form["mqtt_broker_address"]
    config.mqtt_broker_username = request.form["mqtt_broker_username"]
    config.mqtt_broker_password = request.form["mqtt_broker_password"]

    # adafruit io
    config.adafruit_io_username = request.form["adafruit_io_username"]
    config.adafruit_io_key = request.form["adafruit_io_key"]

    # influxdb
    config.influxdb_org = request.form["influxdb_org"]
    config.influxdb_url = request.form["influxdb_url"]
    config.influxdb_token = request.form["influxdb_token"]
    config.influxdb_bucket = request.form["influxdb_bucket"]
    
    write_config()

    return redirect("http://" + DOMAIN + "/provision-step-5-done")
  else:
    return render_template("enviro/html/provision-step-4-destination.html", board=model)
    

@server.route("/provision-step-5-done", methods=["GET", "POST"])
def provision_step_5_done(request):
  config.provisioned = True
  write_config()

  # a post request to the done handler means we're finished and
  # should reset the board
  if request.method == "POST":
    machine.reset()
    return

  return render_template("enviro/html/provision-step-5-done.html", board=model)
    

@server.route("/networks.json")
def networks(request):
  networks = []
  for network in ap.scan():
    network = network[0].decode("ascii").strip()
    if network != "":
      networks.append(network)
  networks = list(set(networks)) # remove duplicates
  return json.dumps(networks), 200, "application/json"


@server.catchall()
def catchall(request):
  # requested domain was wrong
  if request.headers.get("host") != DOMAIN:
    return redirect("http://" + DOMAIN + "/wrong-host-redirect")

  # check if requested file exists
  file = "enviro/html{}".format(request.path)
  if helpers.file_exists(file):
    return serve_file(file)

  return "404 Not Found Buddy!", 404
  

# wait for a client to connect
logging.info("> waiting for a client to connect")
enviro.pulse_activity_led(5)
while len(ap.status("stations")) == 0:
  time.sleep(0.01)
logging.info("  - client connected!", ap.status("stations")[0])

logging.info("> running provisioning application...")
server.run(host="0.0.0.0", port=80)
