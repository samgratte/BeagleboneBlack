# -*- coding: utf-8 -*-
# --- bbb_ain.py ---
# Author  : samuel.bucquet@gmail.com
# Date    : 28.02.2014
# License : GPLv2


class BBB_AIN(object):
    """
    Access to the sysfs interface of the AIN{0..6}
    of the BBB
    """
    _sysfs_path = '/sys/bus/iio/devices/iio:device0/'
    _to_milivolts = 1800.0/4096

    def __init__(self, ain_idx, coefficient=_to_milivolts, valeurmax=None):
        if not 0 <= ain_idx < 7:
            raise ValueError
        self.fsname = self._sysfs_path + 'in_voltage%d_raw' % ain_idx
        self.coeff = coefficient if valeurmax is None else valeurmax/4096.0

    def __iter__(self):
        return self

    def next(self):
        # we don't want buffering on this one
        with open(self.fsname, 'r', 0) as ain_file:
            while True:
                try:
                    line = ain_file.read()
                    break
                except IOError, e:
                    if e.errno != 11:
                        return None
                    # IO Error -- Resource temporarily unavailable --
                    # just retry and it will do !
                    continue
                self.raw_value = int(line)
                return self.raw_value * self.coeff
