# -*- coding: utf-8 -*-
# --- bbb_gpio.py ---
# Author  : samuel.bucquet@gmail.com
# Date    : 20.02.2014
# License : GPLv2

from select import epoll, EPOLLPRI, EPOLLERR


def check_option(expected, option):
    if option not in expected:
        raise ValueError("%s is not in %s !" % (option, expected))


class BBB_GPIO(object):

    _sysfs_path = '/sys/class/gpio/'

    def __init__(self, gpio_number, active_low=False):
        self.path = self._sysfs_path + 'gpio%d/' % gpio_number
        self._active_low = active_low

    @property
    def active_low(self):
        return self._active_low

    @active_low.setter
    def set_active_low(self, active_low=True):
        val = '1' if active_low else '0'
        open(self.path+'active_low', 'w').write(val)
        self._active_low = active_low

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class BBB_GPIO_IN(object):

    def __init__(self, gpio_number, edge='both', active_low=False):
        super().__init__(gpio_number, active_low)
        open(self.path+'direction', 'w').write('in')
        self.fd = open(self.path+'value', 'r', 0)
        self.read()
        self.edge = edge

    @property
    def edge(self):
        return self._edge

    @edge.setter
    def set_edge(self, edge):
        check_option(('none', 'rising', 'falling', 'both'), edge)
        open(self.path+'edge', 'w').write(edge)
        self._edge = edge
        self.blocking = not (edge is 'none')

    @property
    def blocking(self):
        return self._blocking

    @blocking.setter
    def set_blocking(self, blocking=True):
        if blocking:
            self.ep = epoll()
            self.ep.register(self.fd, EPOLLPRI | EPOLLERR)
        else:
            if hasattr(self, 'ep'):
                self.ep.unregister(self.fd)
                del self.ep
        self._blocking = blocking

    def read(self):
        self.fd.seek(0)
        self.value = int(self.fd.read())

    def next(self):
        if self.blocking:
            self.wait()
        else:
            self.read()
        return bool(self.value)

    def __iter__(self):
        return self

    def wait(self):
        if not self.blocking:
            return
        self.ep.poll()
        self.read()

    def close(self):
        self.ep.unregister(self.fd)
        self.fd.close()
