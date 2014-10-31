#!/usr/bin/python
# -*- coding: utf-8 -*-
# --- bbb_dac.py ---
# Author   : Samuel Bucquet
# Date     : 2014.10.27
# License  : GPLv2
"""
module d'accès simplifié au MCP4725 sur bus i2c
on peut en utiliser jusqu'à 4, deux par bus.
"""
from math import ceil
from smbus import SMBus


WRITE_DAC = 0x40
WRITE_DAC_AND_EEPROM = 0x60


def get_dac_addr(num):
    # ici on encapsule le dictionnaire avec une fonction car
    # l'implémentation peut changer
    return {
        0: (0, 0x60),
        1: (0, 0x61),
        2: (1, 0x60),
        3: (1, 0x61)
    }.get(num)


class DAC12(object):

    def __init__(self, dac_num, maximum=100.0):
        bus, self.addr = get_dac_addr(dac_num)
        self.bus = SMBus(bus)
        self.coeff = 4096/float(maximum)

    def conv(self, valeur):
        return int(ceil(valeur * self.coeff)) & 0xFFFF

    def set_eeprom(self, valeur):
        self.bus.write_word_data(self.addr, WRITE_DAC_AND_EEPROM, self.conv(valeur))

    def set(self, valeur):
        self.bus.write_word_data(self.addr, WRITE_DAC, self.conv(valeur))
