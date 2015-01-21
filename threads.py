# -*- coding: utf-8 -*-
# --- threads.py ---
# Author  : perhan.scudeller@gmail.com
# Date    : 19.01.2015

#imports 
from threading import Event as event, Condition as cond 
from bbb_gpio import BBB_GPIO_IN, BBB_GPIO_OUT
from bbb_ain import BBB_AIN
from shareddata import SharedMemory, DataDict

gpio_in = BBB_GPIO_IN(73,'rising')  #l'entrée de la led verte #pin73 #fond montant
tension_ttl = BBB_GPIO_IN(71,'rising') # l'entrée Tout Ou RIen pour le seuil de tension de 1,4V
gpio_out = BBB_GPIO_OUT(72) #commande du relais d'alimentation #pin74
tension_ana = BBB_AIN(4) # lecture analogique de la tension (prop. au courant) #indice4

data_name1 = 'PARASAS__onoff'
redis_server='redissrv'
redis_port=6379
app_name=None
env_init=None

# LED verte 
while True : 
	cond.wait() # en attente de la fin de #corps# 
	gpio_in.wait() # en attente d'un changement de valeur
	event.set() # déclanche #corps# après un changement de valeur 

#Tension TTL 
while True : 
	cond.wait()
	tension_ttl.wait()
	event.set()

#SHM
while True: 
	cond.wait()
	with SharedMemory(redis_server, redis_port, env_init) as shm:
		dd = DataDict(app_nam,shm)
		dd.listen_to_data([data_name1]) #en attente de changement de valaur
	event.set()

#Corps 
event.wait(1000) # en attente d'un déclanchement par #SHM# ou #TensionTTL# ou #LEDverte# ou de 1 seconde 
cond.acquire() # prend la main

green_led=gpio_in.value 
tens_ttl=tension_ttl.value
tens_ana=tension_ana.next # lit la tension analogique
PARASAS__onoff= dd.set_data_to_read([data_name1]) # lecture des données qui nous intéressent sur la SHM

if event.is_set()==True : # exécuté seulement si l'orde vient de #SHM# ou #TensionTTL# ou #LEDverte#
	if PARASAS__onoff==True:
		if green_led==False and tens_ttl == False and tens_ana < 1.4 : 
			relais = True 

	elif tens_ttl ==True or tens_ana > 1.4 or PARASAS__onoff== False: 
		relais = False 

	if relais == False : 
		gpio_out.unset()
	elif relais == True : 
		gpio_out.set()

with SharedMemory(redis_server, redis_port, env_init) as shm : 
		DD = DataDict(app_nam,shm)         #renvoie des données vers la SHM
		data1,data2=DD.set_data_to_write(['PARASAS__presencetension','PARASAS__microcourant'])
		data1.set('green_led')
		data2.set('tens_ana','tens_ttl')
		DD.write #écriture des données 

cond.notify_all()
cond.release()