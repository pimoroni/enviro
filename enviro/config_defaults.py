import config
from phew import logging

DEFAULT_USB_POWER_TEMPERATURE_OFFSET = 4.5
DEFAULT_UTC_OFFSET = 0
DEFAULT_UK_BST = True


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
    config.wunderground_id
  except AttributeError:
    warn_missing_config_setting("wunderground_id")
    config.wunderground_id = None
  
  try:
    config.wunderground_key
  except AttributeError:
    warn_missing_config_setting("wunderground_key")
    config.wunderground_key = None
  
  try:
    config.sea_level_pressure
  except AttributeError:
    warn_missing_config_setting("sea_level_pressure")
    config.sea_level_pressure = False

  try:
    config.height_above_sea_level
  except AttributeError:
    warn_missing_config_setting("height_above_sea_level")
    config.height_above_sea_level = 0
  
  try:
    config.uk_bst
  except AttributeError:
    warn_missing_config_setting("uk_bst")
    config.uk_bst = DEFAULT_UK_BST

  try:
    config.utc_offset
  except AttributeError:
    warn_missing_config_setting("utc_offset")
    config.utc_offset = DEFAULT_UTC_OFFSET

def warn_missing_config_setting(setting):
    logging.warn(f"> config setting '{setting}' missing, please add it to config.py")