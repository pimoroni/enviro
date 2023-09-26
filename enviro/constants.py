# version
ENVIRO_VERSION = "0.0.10" 
 
# modules
ENVIRO_UNKNOWN                = None
ENVIRO_INDOOR                 = 1
ENVIRO_GROW                   = 2
ENVIRO_WEATHER                = 3
ENVIRO_URBAN                  = 4
ENVIRO_CAMERA                 = 5

# common pins
HOLD_VSYS_EN_PIN              = 2
EXTERNAL_INTERRUPT_PIN        = 3
I2C_SDA_PIN                   = 4
I2C_SCL_PIN                   = 5
ACTIVITY_LED_PIN              = 6
BUTTON_PIN                    = 7
RTC_ALARM_PIN                 = 8
RAIN_PIN                      = 10

# system pins
WIFI_CS_PIN                   = 25

# wake reasons
WAKE_REASON_UNKNOWN           = None
WAKE_REASON_PROVISION         = 1
WAKE_REASON_BUTTON_PRESS      = 2
WAKE_REASON_RTC_ALARM         = 3
WAKE_REASON_EXTERNAL_TRIGGER  = 4
WAKE_REASON_RAIN_TRIGGER      = 5
WAKE_REASON_USB_POWERED       = 6

# warning led states
WARN_LED_OFF = 0
WARN_LED_ON = 1
WARN_LED_BLINK = 2

# upload status
UPLOAD_SUCCESS = 0
UPLOAD_FAILED = 1
UPLOAD_RATE_LIMITED = 2
UPLOAD_LOST_SYNC = 3
UPLOAD_SKIP_FILE = 4

# humidity
WATER_VAPOR_SPECIFIC_GAS_CONSTANT = 461.5
CRITICAL_WATER_TEMPERATURE = 647.096
CRITICAL_WATER_PRESSURE = 22064000
