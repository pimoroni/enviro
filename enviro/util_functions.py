import machine

# cpu temperature declaration
CPU_TEMP = machine.ADC(machine.ADC.CORE_TEMP)
ADC_VOLT_CONVERSATION = 3.3 / 65535


def set_pad(gpio, value):
  machine.mem32[0x4001c000 | (4 + (4 * gpio))] = value


def get_pad(gpio):
  return machine.mem32[0x4001c000 | (4 + (4 * gpio))]


def get_battery_voltage():
  old_pad = get_pad(29)
  set_pad(29, 128)  # no pulls, no output, no input

  sample_count = 10
  battery_voltage = 0
  for i in range(0, sample_count):
    battery_voltage += _read_vsys_voltage()
  battery_voltage /= sample_count
  battery_voltage = round(battery_voltage, 3)
  set_pad(29, old_pad)
  return battery_voltage


def _read_vsys_voltage():
  adc_Vsys = machine.ADC(3)
  return adc_Vsys.read_u16() * 3.0 * ADC_VOLT_CONVERSATION


def stop_wifi():
  pass
