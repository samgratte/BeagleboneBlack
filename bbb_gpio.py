#!/usr/bin/python
# -*- coding: utf-8 -*-
# --- bbb_gpio.py ---
# Author  : samuel.bucquet@gmail.com
# Date    : 20.02.2014
# License : GPLv2

from select import epoll, EPOLLPRI, EPOLLERR
import plac


_sysfs_path = '/sys/class/gpio/'


def check_option(expected, option):
    if option not in expected:
        raise ValueError("%s is not in %s !" % (option, expected))


def export(gpio_number):
    open(_sysfs_path + 'export', 'w').write(str(gpio_number))


def unexport(gpio_number):
    open(_sysfs_path + 'unexport', 'w').write(str(gpio_number))


@plac.annotations(
    gpio_number=("Numéro de PIN GPIO", 'positional', None, int),
    action=("'export' ou 'unexport'", 'positional', None, str, ['export', 'unexport'])
)
def main(gpio_number, action):
    if action == 'export':
        export(gpio_number)
    else:  # unexport
        unexport(gpio_number)


class BBB_GPIO(object):

    def __init__(self, gpio_number, active_low=False, is_input=True):
        self.path = _sysfs_path + 'gpio%d/' % gpio_number
        direction = 'in' if is_input else 'out'
        # for direction 'out' it is set with the 'low' value by default
        open(self.path+'direction', 'w').write(direction)
        self._active_low = active_low
        access_mode = 'r' if is_input else 'w'
        self.fd = open(self.path+'value', access_mode, 0)

    @property
    def active_low(self):
        return self._active_low

    @active_low.setter
    def active_low(self, active_low=True):
        val = '1' if active_low else '0'
        open(self.path+'active_low', 'w').write(val)
        self._active_low = active_low

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class BBB_GPIO_OUT(BBB_GPIO):

    def __init__(self, gpio_number, active_low=False):
        BBB_GPIO.__init__(self, gpio_number, active_low, is_input=False)

    def set(self):
        self.fd.write('1')

    def unset(self):
        self.fd.write('0')


class BBB_GPIO_IN(BBB_GPIO):

    def __init__(self, gpio_number, edge='both', active_low=False):
        BBB_GPIO.__init__(self, gpio_number, active_low, is_input=True)
        self.read()
        self.edge = edge

    @property
    def edge(self):
        return self._edge

    @edge.setter
    def edge(self, edge):
        check_option(('none', 'rising', 'falling', 'both'), edge)
        open(self.path+'edge', 'w').write(edge)
        self._edge = edge
        self.blocking = not (edge is 'none')

    @property
    def blocking(self):
        return self._blocking

    @blocking.setter
    def blocking(self, blocking=True):
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


if __name__ == '__main__':
    plac.call(main)
