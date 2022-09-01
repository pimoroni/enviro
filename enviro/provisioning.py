import network, os, json, time, machine

import enviro.helpers as helpers
import enviro
from phew import logging, server, redirect, serve_file, render_template, access_point

DOMAIN = "pico.wireless"


model = enviro.detect_model()

# detect which board type we are provisioning
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
  config = helpers.get_config()
  response = render_template("enviro/html/welcome.html", **config, board=model)
  return response


@server.route("/provision-step-1-nickname", methods=["GET", "POST"])
def provision_step_1_nickname(request):
  if request.method == "POST":
    helpers.set_config(["nickname"], request.form)
    return redirect("http://" + DOMAIN + "/provision-step-2-wifi")
  else:
    config = helpers.get_config()
    return render_template("enviro/html/provision-step-1-nickname.html", **config, board=model)


@server.route("/provision-step-2-wifi", methods=["GET", "POST"])
def provision_step_2_wifi(request):
  if request.method == "POST":
    helpers.set_config(["wifi_ssid", "wifi_password"], request.form)
    return redirect("http://" + DOMAIN + "/provision-step-3-logging")
  else:
    config = helpers.get_config()
    return render_template("enviro/html/provision-step-2-wifi.html", **config, board=model)
  

@server.route("/provision-step-3-logging", methods=["GET", "POST"])
def provision_step_3_logging(request):
  if request.method == "POST":
    helpers.set_config(["reading_frequency", "upload_frequency"], request.form)
    return redirect("http://" + DOMAIN + "/provision-step-4-destination")
  else:
    config = helpers.get_config()
    return render_template("enviro/html/provision-step-3-logging.html", **config, board=model)
    

@server.route("/provision-step-4-destination", methods=["GET", "POST"])
def provision_step_4_destination(request):
  if request.method == "POST":
    helpers.set_config(
      [
        "destination", 
        "custom_http_url", 
        "custom_http_username", 
        "custom_http_password", 
        "mqtt_broker_address", 
        "mqtt_broker_username", 
        "mqtt_broker_password",
        "adafruit_io_username", 
        "adafruit_io_key"
      ], 
      request.form
    )
    return redirect("http://" + DOMAIN + "/provision-step-5-done")
  else:
    config = helpers.get_config()
    return render_template("enviro/html/provision-step-4-destination.html", **config, board=model)
    

@server.route("/provision-step-5-done", methods=["GET", "POST"])
def provision_step_5_done(request):
  # a post request to the done handler means we're finished and
  # should reset the board
  if request.method == "POST":
    helpers.set_config("provisioned", True)
    enviro.sleep(helpers.get_config("reading_frequency"))
    return

  config = helpers.get_config()
  return render_template("enviro/html/provision-step-5-done.html", **config, board=model)
    

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