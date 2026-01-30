# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#   Copyright (c) 2020, Planet Innovation
#   436 Elgar Road, Box Hill VIC 3128 Australia
#   Phone: +61 3 9945 7510
#
#   The copyright to the computer program(s) herein is the property of
#   Planet Innovation, Australia.
#   The program(s) may be used and/or copied only with the written permission
#   of Planet Innovation or in accordance with the terms and conditions
#   stipulated in the agreement/contract under which the program(s) have been
#   supplied.
#
#   @file drivers for FT24CxxA EEPROM family

"""Drivers for the FT24CxxA EEPROM family"""

from machine import I2C, Pin
from time import sleep_ms  # type: ignore[attr-defined]
from micropython import const


class Ft2408A:
    """Interface for the Ft2408A 8K-bit (i.e. 1KB) EEPROM chip."""

    CAPACITY = const(1024)
    PAGE_SIZE = const(16)
    T_WC_ms = const(5)

    def __init__(self, i2c: I2C, write_protect_pin: Pin, chip_address: int):
        """Initialise an EEPROM interface.

        Args:
            i2c: A referemnce to the I2C bus to use
            write_protect_pin: A Pin wired up the the WP input on the EEPROM
                chip
            chip address: The I2C chip address to use when commuinicating with
                the EEPROM chip.
        """
        self.i2c = i2c
        self.write_protect_pin = write_protect_pin
        self.chip_address = chip_address
        self.page_buffer = bytearray(self.PAGE_SIZE)
        self.enable_write(False)

    def write(self, data: bytearray):
        """Write an arbitrary amount of data to the EEPROM chip, starting at
        offset 0.

        The write is performed in PAGE_SIZE chunks, with a write cycle delay
        (of milliseconds per page) in between. Be warned that this is *not*
        instantaneous.
        """
        assert len(data) < self.CAPACITY, "Write would overflow storage"
        data = memoryview(data)  # type: ignore[assignment]
        offset = 0

        # write the bulk of the data in page-sized chunks
        while len(data) >= self.PAGE_SIZE:
            page = data[0 : self.PAGE_SIZE]
            self._write_page_starting_at(offset, page)
            offset = offset + self.PAGE_SIZE
            data = data[self.PAGE_SIZE :]

        # for the remainder, we need to read the target page in, overwrite with
        # the remaining bytes and write it back out in order to preserve the
        # existing contents of the EEPROM page
        if len(data) > 0:
            self.read_into(self.page_buffer, offset)
            self.page_buffer[0 : len(data)] = data[:]
            self._write_page_starting_at(offset, self.page_buffer)

    def enable_write(self, value: bool = True):
        """Enables or disables write protecion on the EEPROM"""
        # The write protect pin should be "high" to disable writes, so we need
        # to invert the "enable write" logic when deciding how to set the pin.
        self.write_protect_pin.value(int(not bool(value)))

    def _io_address(self, offset: int) -> int:
        """Constructs a chip address for writing to the EEPROM. The EEPROM chip
        used the low-order bits of the chip address as the high-order bits of
        the write offset.

        In this case the chip address is composed of the configured address of
        the EEPROM chip, plus the two MSBs of the data read/write offset.
        """
        offset_high_bits = (offset >> 8) & 0b11
        return self.chip_address | offset_high_bits

    def _write_page_starting_at(self, offset: int, page: bytearray):
        """Write a whole 16-byte page to the EEPROM and wait for the write
        cycle time to elapse.

        Args:
            offset: The address of the first byte in the page
        """
        assert len(page) == self.PAGE_SIZE, "Input buffer must be exactly one page"
        assert (offset % self.PAGE_SIZE) == 0, "Offset must be a page boundary"

        chip_addr = self._io_address(offset)
        offset_low = offset & 0xFF
        self.i2c.writeto_mem(chip_addr, offset_low, page)
        sleep_ms(self.T_WC_ms)

    def read_into(self, buf: bytearray, eeprom_offset: int = 0):
        """Read len(buf) bytes from the EEPROM into `buf`, starting at
        `eeprom_offset`."""
        # perform an empty write to set the current address
        chip_addr = self._io_address(eeprom_offset)
        offset_low = eeprom_offset & 0xFF
        self.i2c.writeto_mem(chip_addr, offset_low, bytearray(0))

        # read back an arbitrary amount of data from the eeprom, starting at
        # the address we set in the fake write above
        self.i2c.readfrom_into(self.chip_address, buf)

    @staticmethod
    def address_from_pin(a2: int) -> int:  # pylint: disable=invalid-name
        """Construct the chip address for an FT2C08A given the value of the
        `a2` address pin.
        """
        return 0b1010000 | (a2 << 2)
