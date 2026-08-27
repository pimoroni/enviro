# Pimoroni Enviro - Raspberry Pi Pico W based environmental monitoring boards

set(PICO_BOARD "pico_w")

# The C malloc is needed by cyw43-driver Bluetooth and the Pimoroni Pico modules
set(MICROPY_C_HEAP_SIZE 4096)

set(MICROPY_PY_LWIP ON)
set(MICROPY_PY_NETWORK_CYW43 ON)

set(MICROPY_PY_BLUETOOTH ON)
set(MICROPY_BLUETOOTH_BTSTACK ON)
set(MICROPY_PY_BLUETOOTH_CYW43 ON)

set(MICROPY_HW_FLASH_STORAGE_BYTES 868352)  # 848 * 1024

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
