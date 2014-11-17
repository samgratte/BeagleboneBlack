#!/usr/bin/python
# -*- coding: utf-8 -*-
# --- hdl_ains.py ---
# Author   : Samuel Bucquet
# Date     : 2014.10.27
# License  : GPLv2

from itertools import izip
from bbb_ain import BBB_AIN
from shareddata import SharedMemory, DataDict, Waiting, fatal_error
import plac


@plac.annotations(
    data_name="Nom de la data dans la SHM",
    ain_max=('Valeur max de lecture de(s) AIN(s)', 'option', 'm', float),
    frequency=("À quelle fréquence on interroge le(s) AIN(s)", 'option', 'f',
               int),
    redis_server=("Nom ou @ IP de la cpu sur laquelle tourne Redis", 'option',
                  'r'),
    redis_port=("N° de port tcp pour se connecter à Redis", 'option', 'p', int),
    app_name=("Nom de l'application pour la SHM", 'option', 'a'),
    env_init=("Nom de la variable d'environnement qui contient la data d'init"
              + " de la shm", 'option', 'i'),
    adc_nums=("Numéro de l'ADC utilisé en entrée (de 0 à 7) (plusieurs peuvent"
              + "être indiqués)", 'positional', None, int, None, 'AIN')
)
def main(data_name, ain_max=4096, frequency=1, redis_server='redissrv',
         redis_port=6379, app_name=None, env_init=None, *adc_nums):

    # Initialisation des AINs
    if len(adc_nums) < 1:
        fatal_error("Il faut renseigner au moins un AIN !")
    AINs = []
    for adc_num in adc_nums:
        if adc_num > 7:
            fatal_error("Mauvaise valeur d'AIN (%d) !\n" % adc_num
                        + "Les AINs vont de zéro à sept inclus !")
        AINs.append(BBB_AIN(adc_num, valeurmax=ain_max))
    periode = Waiting(frequency)
    # Connexion à la SHM
    with SharedMemory(redis_server, redis_port, env_init) as shm:
        # Déclaration
        dd = DataDict(app_name, shm)
        shm_ains, = dd.set_datas_to_write([data_name])
        # À chaque cycle, lecture des infos capteur
        for ains in izip(*AINs):
            periode.set_start()
            # envoi des données ains vers la SHM
            shm_ains.set(*ains, ts=periode.start_time)
            dd.write()
            periode.wait_next()

if __name__ == '__main__':
        plac.call(main)
