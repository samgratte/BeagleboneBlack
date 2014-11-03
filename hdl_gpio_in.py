#!/usr/bin/python
# -*- coding: utf-8 -*-
# --- hdl_gpio.py ---
# Author   : Samuel Bucquet
# Date     : 2014.10.27
# License  : GPLv2

from bbb_gpio import BBB_GPIO_IN
from shareddata import SharedMemory, DataDict
from shareddata import Waiting, fatal_error
import plac


@plac.annotations(
    data_name="Nom de la data dans la SHM",
    gpio_num=("numéro de GPIO", 'positional', None, int),
    active_low=("Si le GPIO est actif à l'état bas", 'flag', 'l'),
    gpio_edge=("sur quel front se fait la détection ('none' non bloquant)",
               'option', 'e', str, ['none', 'rising', 'falling', 'both']),
    frequency=("À quelle fréquence on interroge le GPIO (lorsque on est non"
               + " bloquant)", 'option', 'f', int),
    redis_server=("Nom ou @ IP de la cpu sur laquelle tourne Redis",
                  'option', 'r'),
    redis_port=("N° de port tcp pour se connecter à Redis", 'option', 'p', int),
    app_name=("Nom de l'application pour la SHM", 'option', 'a'),
    env_init=("Nom de la variable d'environnement qui contient la data d'init"
              + " de la shm", 'option', 'i')
)
def main(data_name, gpio_num, active_low, gpio_edge='both', frequency=-1,
         redis_server='redissrv', redis_port=6379, app_name=None, env_init=None):

    if not (gpio_edge is 'none') and frequency != -1:
        fatal_error("Impossible de satisfaire 'edge' à '%s' " % gpio_edge +
                    "(bloquant)\net 'frequency' à %d (non bloquant) !" % frequency)
    # Connexion à la SHM et Initialisation du GPIO
    with SharedMemory(redis_server, redis_port, env_init) as shm,\
            BBB_GPIO_IN(gpio_num, gpio_edge, active_low) as gpio_in:
        # Déclaration
        dd = DataDict(app_name, shm)
        shm_gpio, = dd.set_datas_to_write([data_name])
        # À chaque cycle, lecture des infos capteur
        periode = Waiting(frequency)
        for state in gpio_in:
            periode.set_start()
            # envoi des données ains vers la SHM
            shm_gpio.set(state, ts=periode.start_time)
            dd.flush()
            periode.wait_next()

if __name__ == '__main__':
    plac.call(main)
