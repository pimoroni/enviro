# enviro config file

# you may edit this file by hand but if you enter provisioning mode
# then the file will be automatically overwritten with new details

provisioned = False

# enter a nickname for this board
nickname = None

# network access details
wifi_ssid = None
wifi_password = None

# how many log files to keep
log_count = 20

# how often to wake up and take a reading (in minutes)
reading_frequency = 15

# where to upload to ("web_hook", "mqtt", "adafruitio")
destination = None

# how often to upload data (number of cached readings)
upload_frequency = 5

# web hook settings
custom_http_url = None
custom_http_username = None
custom_http_password = None

# mqtt broker settings
mqtt_broker_address = None
mqtt_broker_username = None
mqtt_broker_password = None

# adafruit ui settings
adafruit_io_username = None
adafruit_io_key = None