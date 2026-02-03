# micropython-ft24cxxa

A MicroPython driver for the [FT24CxxA I2C EEPROM family](https://www.fremont-micro.com/products/serial-eeprom-i2c-eeprom/) (1KB-8KB)

## Installation

### Using mip (recommended)
```python
import mip
mip.install("github:planetinnovation/micropython-ft24cxxa")
```

### Manual installation
Download `micropython_ft24cxxa.py` and copy it to your MicroPython device.

## Usage

```python
from micropython_ft24cxxa import Ft2408A
from machine import I2C, Pin

# Initialize I2C and write protect pin
i2c = I2C(1, freq=100_000)
write_protect_pin = Pin(10, Pin.OUT)

# Create EEPROM instance
eeprom = Ft2408A(
    i2c=i2c,
    write_protect_pin=write_protect_pin,
    chip_address=Ft2408A.address_from_pin(a2=0)
)

# Write data to EEPROM
data = bytearray(b"Hello, EEPROM!")
eeprom.enable_write(True)
eeprom.write(data)
eeprom.enable_write(False)

# Read data from EEPROM
buffer = bytearray(14)
eeprom.read_into(buffer, eeprom_offset=0)
print(buffer)  # b'Hello, EEPROM!'
```

## Supported Devices

This driver supports the FT24CxxA EEPROM family:
- FT2408A (1KB / 8Kbit)

The driver can be extended to support other devices in the family with different capacities and page sizes.

## License

MIT License - Copyright (c) 2020, Planet Innovation
