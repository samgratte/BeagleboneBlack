# -*- coding: utf-8 -*-
# --- bbb_gpio.py ---
# Author  : samuel.bucquet@gmail.com
# Date    : 20.02.2014
# License : GPLv2

from select import epoll, EPOLLPRI, EPOLLERR


class BBB_GPIO(object):

    _sysfs_path = '/sys/class/gpio/'

    def __init__(self, gpio_number, gpio_edge='rising', active_low=False):
        open(self._sysfs_path+'unexport', 'w').write(str(gpio_number))
        open(self._sysfs_path+'export', 'w').write(str(gpio_number))
        self.path = self._sysfs_path + 'gpio%d/' % gpio_number
        open(self.path+'direction', 'w').write('in')
        open(self.path+'edge', 'w').write(gpio_edge)
        if active_low:
            open(self.path+'active_low', 'w').write('1')
        self.ep = epoll()
        self.read()

    def read(self):
        self.value = int(open(self.path+'value', 'r').read())

    def get(self):
        return self.value

    def next(self):
        self.wait()
        return bool(self.value)

    def __iter__(self):
        return self

    def wait(self):
        # we don't want buffering on this one
        fd = open(self.path+'value', 'r', 0)
        self.ep.register(fd, EPOLLPRI | EPOLLERR)
        self.ep.poll()
        self.ep.unregister(fd)
        self.value = int(fd.read())
        fd.close()
