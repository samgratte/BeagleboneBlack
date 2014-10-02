# -*- coding: utf-8 -*-
# --- gpsd_client.py ---
# Author  : samuel.bucquet@gmail.com
# Date    : 27.03.2014
# License : GPLv2

import gps
from collections import namedtuple


class GPSd_client(object):

    def __init__(self, gpsd_host):
        self.host = gpsd_host
        self.GPS = namedtuple('GPS', 'time latitude longitude altitude sog cog ept mode')

    def __iter__(self):
        return self

    def next(self):
        session = gps.gps(host=self.host)
        session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        for report in session:
            if report['class'] == 'TPV' and report['tag'] == 'RMC':
                trame = dict(report)
                break
        session.close()
        return self.GPS(*[trame[k] for k in ('time', 'lat', 'lon', 'alt',
            'speed', 'track', 'ept', 'mode')])
