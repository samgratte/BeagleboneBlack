#!/usr/bin/python
# -*- coding: utf-8 -*-
# --- hdl_dacs.py ---
# Author   : Samuel Bucquet
# Date     : 2014.10.27
# License  : GPLv2

import sys
from bbb_dac import DAC12
from shareddata import SharedMemory, DataDict, fatal_error
import plac


@plac.annotations(
    data_name="Nom de la data dans la SHM en écoute (elle doit avoir un champ value)",
    maximum=('Maximum que peuvent prendre les données', 'option', 'm', float),
    frequency=("À quelle fréquence on interroge le(s) AIN(s)", 'option', 'f', int),
    redis_server=("Nom ou @ IP de la cpu sur laquelle tourne Redis", 'option', 'r'),
    redis_port=("N° de port tcp pour se connecter à Redis", 'option', 'p', int),
    env_init=("Nom de la variable d'environnement qui contient la data d'init de la shm", 'option', 'i'),
    dac_nums=("Numéro du DAC utilisé en entrée", 'positional', None, int, None, 'DAC')
)
def main(data_name, maximum=100.0, frequency=-1, redis_server='redissrv',
         redis_port=6379, env_init=None, *dac_nums):

    # Initialisation du DAC
    if len(dac_nums) < 1:
        fatal_error("Il faut renseigner au mois un DAC !")
    DACs = []
    for dac_num in dac_nums:
        DACs.append(DAC12(dac_num, maximum))
    # Connexion à la SHM
    with SharedMemory(redis_server, redis_port, env_init) as shm:
        # Déclaration
        dd = DataDict(sys.argv[0], shm)
        data_listen = dd.listen_to_datas([data_name])
        # on attend que la donnée soit rafraichît
        for (data,) in data_listen:
            # envoi des valeurs vers les DACs
            for dac, value in zip(DACs, data[2:]):
                dac.set(value)

if __name__ == '__main__':
        plac.call(main)
