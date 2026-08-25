import config
from phew import logging

DEFAULT_USB_POWER_TEMPERATURE_OFFSET = 4.5


def add_missing_config_settings():
  # no ca file means don't use SSL
  if not hasattr(config, "mqtt_broker_ca_file"):
    warn_missing_config_setting("mqtt_broker_ca_file")
    config.mqtt_broker_ca_file = None

  if not hasattr(config, "usb_power_temperature_offset"):
    warn_missing_config_setting("usb_power_temperature_offset")
    config.usb_power_temperature_offset = DEFAULT_USB_POWER_TEMPERATURE_OFFSET

  if not hasattr(config, "wifi_country"):
    warn_missing_config_setting("wifi_country")
    config.wifi_country = "GB"

def warn_missing_config_setting(setting):
    logging.warn(f"> config setting '{setting}' missing, please add it to config.py")
