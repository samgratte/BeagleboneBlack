#!/usr/bin/python
# -*- coding: utf-8 -*-
#==========================================================================
#
#          FILE:  test_dac.py
# 
#         USAGE:  ---
# 
#   DESCRIPTION:  ---
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Samuel Bucquet - samuel.bucquet@gmail.com
#       COMPANY:  DGA/GESMA
#       LICENSE:  GPLv2 see 'LICENSE.TXT'
#       VERSION:  ---
#       CREATED:  10-09-2013
#      MODIFIED:  ---
#      REVISION:  1
#==========================================================================



from smbus import SMBus
from i2c_mcp4725 import MCP4725
import plac

@plac.annotations(
action=("Action à réaliser sur le DAC",'positional',None,str,['read','write']),
value=("Valeur sur 12 bits à écrire sur le DAC",'positional',None,int),
persistent=("Sauver la valeur écrite dans l'EEPROM du DAC",'flag','p'),
bus=("Indice du bus i2c à utiliser",'option','b',int),
address=("Adresse du DAC sur le bus i2c",'option','a',str),
vRef=("Tension de référence envoyée au DAC",'option',None,float)
)
def main(action,persistent,value=0,bus=1,address='0x60',vRef=3.3):


	dac = MCP4725(SMBus(bus),int(address,16),vRef)
	if action == 'write':
		if persistent:
			dac.write_dac_and_eeprom(value,True)
		else:
			# Pour affecter la valeur on effectue :
			dac.write_dac_fast(value)
			# ou bien
			dac(value)
			# ou bien
			dac.register = value # mais là /!\ on fait un appel à 'read_dac_and_eeprom'
								 # afin de vérifier la cohérence de la donnée

			# ensuite pour la lire on peut faire :
			print dac()
			# ou bien
			print dac.register
			# ou bien 
			print dac.dac_register # mais /!\ c'est la valeur historisée
			
	else: # READ
		dac.read_dac_and_eeprom()
		print dac

if __name__ == '__main__':

	plac.call(main)
