if(NOT DEFINED PIMORONI_PICO_PATH)
set(PIMORONI_PICO_PATH ${CMAKE_CURRENT_LIST_DIR}/../pimoroni-pico)
endif()

include_directories(${PIMORONI_PICO_PATH})
include_directories(${PIMORONI_PICO_PATH}/micropython)

list(APPEND CMAKE_MODULE_PATH "${PIMORONI_PICO_PATH}")
list(APPEND CMAKE_MODULE_PATH "${PIMORONI_PICO_PATH}/micropython")
list(APPEND CMAKE_MODULE_PATH "${PIMORONI_PICO_PATH}/micropython/modules")

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Essential
include(pimoroni_i2c/micropython)
include(pimoroni_bus/micropython)

# Pico Graphics Essential
include(hershey_fonts/micropython)
include(bitmap_fonts/micropython)
include(picographics/micropython)

# Pico Graphics Extra
include(jpegdec/micropython)
include(qrcode/micropython/micropython)

# Sensors & Breakouts
include(micropython-common-breakouts)
include(pcf85063a/micropython)

# Utility
include(adcfft/micropython)
include(wakeup/micropython)

# Configure wakeup for Enviro
target_compile_definitions(usermod_wakeup INTERFACE
    -DWAKEUP_HAS_RTC=1
    -DWAKEUP_PIN_MASK=0b01000100
    -DWAKEUP_PIN_DIR=0b01000100
    -DWAKEUP_PIN_VALUE=0b01000100
)

# LEDs & Matrices
include(plasma/micropython)

# Servos & Motors
include(pwm/micropython)
include(servo/micropython)
include(encoder/micropython)
include(motor/micropython)

# C++ Magic Memory
include(cppmem/micropython)

# Misleadingly named: the four C++ flags it sets are already pico-sdk defaults via
# pico_cxx_options, and the -specs=nano.specs it adds does the work - 58KB, which
# is 42KB of C++ demangler pulled in by libsupc++'s verbose terminate handler and
# 16KB of newlib-nano. Dropping it puts the firmware at 99.6% of the region.
include(micropython-disable-exceptions)
