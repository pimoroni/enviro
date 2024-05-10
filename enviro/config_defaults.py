import config
from phew import logging

DEFAULT_USB_POWER_TEMPERATURE_OFFSET = 4.5
DEFAULT_BME688_ADDRESS = None


def add_missing_config_settings():
  try:
    # check if ca file parameter is set, if not set it to not use SSL by setting to None
    config.mqtt_broker_ca_file
  except AttributeError:
    warn_missing_config_setting("mqtt_broker_ca_file")
    config.mqtt_broker_ca_file = None

  try:
    config.usb_power_temperature_offset
  except AttributeError:
    warn_missing_config_setting("usb_power_temperature_offset")
    config.usb_power_temperature_offset = DEFAULT_USB_POWER_TEMPERATURE_OFFSET

  try:
    config.wifi_country
  except AttributeError:
    warn_missing_config_setting("wifi_country")
    config.wifi_country = "GB"

  try:
    config.bme688_address
  except AttributeError:
    warn_missing_config_setting("bme688_address")
    config.bme688_address = DEFAULT_BME688_ADDRESS


def warn_missing_config_setting(setting):
    logging.warn(f"> config setting '{setting}' missing, please add it to config.py")
