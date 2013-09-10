# MCP_4725

## Utilisation de i2c_MCP4725.py (Python):

```python
dac = MCP4725(SMBus(bus),int(address,16),vRef)
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
```
## Utilisation de test_dac.py (shell):

```bash
 $ ./test_dac.py -h
usage: test_dac.py [-h] [-p] [-b 1] [-a 0x60] [-vRef 3.3] {read,write} [value]

positional arguments:
  {read,write}          Action à réaliser sur le DAC
  value                 Valeur sur 12 bits à écrire sur le DAC

optional arguments:
  -h, --help            show this help message and exit
  -p, --persistent      Sauver la valeur écrite dans l'EEPROM du DAC
  -b 1, --bus 1         Indice du bus i2c à utiliser
  -a 0x60, --address 0x60
                        Adresse du DAC sur le bus i2c
  -vRef 3.3             Tension de référence envoyée au DAC
 $ ./test_dac.py read
        C0 1C B0 01 CB
        Ready=True|PowerOnReset=True|PowerDown=0
        DAC_Register=459|EEPROM_Data=459

 $ ./test_dac.py write 1567
 $ ./test_dac.py read
        C0 61 F0 01 CB
        Ready=True|PowerOnReset=True|PowerDown=0
        DAC_Register=1567|EEPROM_Data=459

 $ ./test_dac.py write 1567 -p
 $ ./test_dac.py read
        C0 61 F0 06 1F
        Ready=True|PowerOnReset=True|PowerDown=0
        DAC_Register=1567|EEPROM_Data=1567

```
