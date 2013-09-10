#!/usr/bin/python
# -*- coding: utf-8 -*-
#==========================================================================
#
#          FILE:  i2c_mcp4725.py
# 
#         USAGE:  ---
# 
#   DESCRIPTION:  ---
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Samuel Bucquet
#       COMPANY:  DGA/GESMA
#       LICENSE:  GPL see 'LICENSE.TXT'
#       VERSION:  ---
#       CREATED:  10-09-2013
#      MODIFIED:  ---
#      REVISION:  1
#==========================================================================


from math import ceil

class MCP4725(object):

	_WRITE_DAC = 0x40
	_WRITE_DAC_AND_EEPROM = 0x60

	def __init__(self,bus,address=0x60,vRef=3.3):
		self.bus = bus
		self.address = address
		self.vRef = vRef
		self.read_dac_and_eeprom()

	def	read_dac_and_eeprom(self):
		buff = self.bus.read_i2c_block_data(self.address,0x00,5)
		self.lastread = ' '.join('%02X'%d for d in buff)
		self.ready = bool(buff[0] & 0x80)
		self.power_on_reset = bool(buff[0] & 0x40)
		# powerdown : voir page 20, table 5-2
		self.powerdown = (buff[0] & 0x06) >> 1
		self.dac_register = ((buff[1] << 4)&0x0FF0) | ((buff[2]>>4)&0x0F)
		self.eeprom_data = ((buff[3]<<8)&0x0F00) | buff[4]

	def write_dac_fast(self,value):
		if not 0<=value<4096:
			raise ValueError
		self.bus.write_byte_data(self.address,(value>>8)&0x0F,value&0xFF)

	def write_dac_and_eeprom(self,value,do_store_value=True):
		if not 0<=value<4096:
			raise ValueError
		cmd = self._WRITE_DAC_AND_EEPROM if do_store_value else self._WRITE_DAC
		buff = [(value>>4)&0xFF,(value<<4)&0xFF]
		self.bus.write_i2c_block_data(self.address,cmd,buff)
	
	def __call__(self,value=None):
		if value == None:
			self.read_dac_and_eeprom()
			return self.dac_register
		else:
			self.write_dac_fast(value)

	@property
	def register(self):
		return self()
		#self.read_dac_and_eeprom()
		#return self.dac_register

	@register.setter
	def register(self,value):
		#self.write_dac_fast(value)
		self(value)
		self.read_dac_and_eeprom()
		
	def __str__(self):
		return  """\t%s
	Ready=%s|PowerOnReset=%s|PowerDown=%d
	DAC_Register=%d|EEPROM_Data=%d\n""" % (self.lastread,str(self.ready),
			str(self.power_on_reset),self.powerdown,self.dac_register,
			self.eeprom_data)
	
	def voltage2register(self,voltage):
		return None if voltage>self.vRef else int(ceil(voltage*(4096.0/self.vRef)))

