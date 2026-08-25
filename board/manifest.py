include("$(PORT_DIR)/boards/manifest.py")

# https://github.com/micropython/micropython-lib/blob/master/micropython/bundles/bundle-networking/manifest.py
require("bundle-networking")
require("umqtt.simple")

require("aioble")

freeze("$(PIMORONI_PICO_PATH)/micropython/modules_py", "pimoroni.py")
freeze("$(PIMORONI_PICO_PATH)/micropython/modules_py", "boot.py")
