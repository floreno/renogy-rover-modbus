#!/usr/bin/python
# -*- coding: utf-8 -*-

# Driver for the Renogy Rover Solar Controller using the Modbus RTU protocol

import sys
import string
import minimalmodbus

minimalmodbus.BAUDRATE = 9600
minimalmodbus.TIMEOUT = 1

BATTERY_TYPE = {
	1: 'open',
	2: 'sealed',
	3: 'gel',
	4: 'lithium',
	5: 'self-customized',
}

CHARGING_STATE = {
	0: 'deactivated',
	1: 'activated',
	2: 'mppt',
	3: 'equalizing',
	4: 'boost',
	5: 'floating',
	6: 'current limiting',
}

LOAD_MODES = {
	0: 'Sole light control, light control over on/off of load',
	1: 'Load is turned on by light control, and goes off after a time delay of 1 hour',
	2: 'Load is turned on by light control, and goes off after a time delay of 2 hours',
	3: 'Load is turned on by light control, and goes off after a time delay of 3 hours',
	4: 'Load is turned on by light control, and goes off after a time delay of 4 hours',
	5: 'Load is turned on by light control, and goes off after a time delay of 5 hours',
	6: 'Load is turned on by light control, and goes off after a time delay of 6 hours',
	7: 'Load is turned on by light control, and goes off after a time delay of 7 hours',
	8: 'Load is turned on by light control, and goes off after a time delay of 8 hours',
	9: 'Load is turned on by light control, and goes off after a time delay of 9 hours',
	10: 'Load is turned on by light control, and goes off after a time delay of 10 hours',
	11: 'Load is turned on by light control, and goes off after a time delay of 11 hours',
	12: 'Load is turned on by light control, and goes off after a time delay of 12 hours',
	13: 'Load is turned on by light control, and goes off after a time delay of 13 hours',
	14: 'Load is turned on by light control, and goes off after a time delay of 14 hours',
	15: 'Manual',
	16: 'Debugging',
	17: 'Normal on',
}

ERROR_CODES = {
	0: 'None',
	1: 'reserved',
	2: 'reserved',
	3: 'reserved',
	4: 'reserved',
	5: 'reserved',
	6: 'reserved',
	7: 'reserved',
	8: 'reserved',
	9: 'reserved',
	10: 'reserved',
	11: 'reserved',
	12: 'reserved',
	13: 'reserved',
	14: 'reserved',
	15: 'reserved',
	16: 'battery over-discharge',
	17: 'battery over-voltage',
	18: 'battery under-voltage warning',
	19: 'load short circuit',
	20: 'load overpower or load over-current',
	21: 'controller temperature too high',
	22: 'ambient temperature too high',
	23: 'photovoltaic input overpower',
	24: 'photovoltaic input side short circuit',
	25: 'photovoltaic input side over- voltage',
	26: 'solar panel counter-current',
	27: 'solar panel working point over-voltage',
	28: 'solar panel reversely connected',
	29: 'anti-reverse MOS short',
	30: 'circuit, charge MOS short',
	31: 'reserved',
}

SYS_VOLTAGE = {
	12: '12V',
	24: '24V',
	36: '36V',
	48: '48V',
}

MODEL_TYPE = {
	0: 'Controller',
	1: 'Inverter',
}
class RenogyRover(minimalmodbus.Instrument):

# Communicates using the Modbus RTU protocol (via provided USB<->RS232 cable)

	def __init__(self, portname, slaveaddress):
		minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
		register = self.read_register(0x000A)
		self.amps_charge = register & 255
		self.voltage = register >> 8
		register = self.read_register(0x000B)

		self.amps_discharge = register >> 8
		self.mtype = MODEL_TYPE.get(register & 255)


		register = self.read_register(0x0103)
		battery_temp_bits = register & 255
		temp_value = battery_temp_bits & 255
		sign = battery_temp_bits >> 7
		self.battery_temp = (-(temp_value - 128) if sign == 1 else temp_value)
		controller_temp_bits = register >> 8
		temp_value = controller_temp_bits & 255
		sign = controller_temp_bits >> 7
		self.controller_temp = (-(temp_value - 128) if sign == 1 else temp_value)

		self.serialno = self.read_mbyte4(0x0018)

		registers = self.read_registers(0x0014, 4)
		soft_major = registers[0] & 255
		soft_minor = registers[1] >> 8
		soft_patch = registers[1] & 255
		hard_major = registers[2] & 255
		hard_minor = registers[3] >> 8
		hard_patch = registers[3] & 255
		self.software_version = 'V{}.{}.{}'.format(soft_major, soft_minor, soft_patch)
		self.hardware_version = 'V{}.{}.{}'.format(hard_major, hard_minor, hard_patch)

		register = self.read_register(0xE00F)
		self.SOCcharge = register >> 8
		self.SOCdischarge = register & 255

	def read_voltage(self, register):
		if self.voltage == 24:
			return int(self.read_register(register)/10*2*10)/10
		else:
			return self.read_register(register)/10

	def read_mbyte4(self, register):
		registers = self.read_registers(register, 2)
		return '{}{}'.format(registers[0], registers[1])

if __name__ == '__main__':
	rover = RenogyRover('/dev/ttyAMA0', 1)
	rover.write_register(0x010A, False)
	print('Model.............................'+str(rover.read_string(0x000C, 6).strip()+rover.read_string(0x0012, 2).strip()))
	print(' Type.............................'+str(rover.mtype))
	print(' SerialNo.........................'+str(rover.serialno))
	print(' Software Version.................'+str(rover.software_version))
	print(' Hardware Version.................'+str(rover.hardware_version))
	print(' Rated Voltage....................'+str(rover.voltage)+'V')
	print(' Rated Max. Charge................'+str(rover.amps_charge)+'A')
	print(' Rated Max. Discharge.............'+str(rover.amps_discharge)+'A')
	print(' Data Device Address..............'+str(rover.read_register(0x010A)))
	print(' Load On/Off Mode.................'+LOAD_MODES.get(rover.read_register(0xE01D)))
	print(' Days Working.....................'+str(rover.read_register(0x0115)))
	print(' Over discharges..................'+str(rover.read_register(0x0116))+'x')
	print(' Full charges.....................'+str(rover.read_register(0x0117))+'x')
	print(' Error-Status.....................'+ERROR_CODES.get(int(rover.read_mbyte4(0x0121))))

	print('')
	print('Battery:')
	print(' SOC..............................'+str(rover.read_register(0x0100))+'%')
	print(' Voltage..........................'+str(rover.read_register(0x0101)/10)+'V')
	print(' Type.............................'+BATTERY_TYPE.get(rover.read_register(0xE004)))
	print(' Capacity.........................'+str(rover.read_register(0xE002))+'Ah')
	print(' Temperature......................'+str(rover.battery_temp)+'°C')

	print('')
	print('Load:')
	print(' Voltage..........................'+str(rover.read_register(0x0104)/10)+'V')
	print(' Current..........................'+str(rover.read_register(0x0105)/100)+'A')
	print(' Power............................'+str(rover.read_register(0x0106))+'W')
	print(' Temperatur.......................'+str(rover.controller_temp)+'°C')

	print('')
	print('Solar/Charging:')
	print(' Voltage..........................'+str(rover.read_register(0x0107)/10)+'V')
	print(' Current..........................'+str(rover.read_register(0x0108)/100)+'A')
	print(' Power............................'+str(rover.read_register(0x0109))+'W')
	print(' Status...........................'+CHARGING_STATE.get(rover.read_register(0x0120) & 255))

	print('')
	print('Today:')
	print(' min Volt.........................'+str(rover.read_register(0x010B)/10)+'V')
	print(' max Volt.........................'+str(rover.read_register(0x010C)/10)+'V')
	print(' max Charging.....................'+str(rover.read_register(0x010D)/100)+'A')
	print(' max Discharging..................'+str(rover.read_register(0x010E)/100)+'A')
	print(' max Charging.....................'+str(rover.read_register(0x010F))+'W')
	print(' max Discharging..................'+str(rover.read_register(0x0110))+'W')
	print(' Charging.........................'+str(rover.read_register(0x0111))+'AH')
	print(' Discharging......................'+str(rover.read_register(0x0112))+'AH')
	print(' Power generation.................'+str(rover.read_register(0x0113))+'W')
	print(' Power consumption................'+str(rover.read_register(0x0114))+'W')

	print('')
	print('Total:')
	print(' Charging.........................'+str(int(rover.read_mbyte4(0x0118)))+'AH')
	print(' Discharging......................'+str(int(rover.read_mbyte4(0x011A)))+'AH')
	print(' Power generation.................'+str(int(rover.read_mbyte4(0x011C))/1000)+'kW/H')
	print(' Power consumption................'+str(int(rover.read_mbyte4(0x011E))/1000)+'kW/H')
	print(' current day......................'+str(int(rover.read_register(0xF000))))
	print(' last day.........................'+str(rover.read_register(0xF001)))


	print('')
	print('LED-Load:')
	print('Light Delay.......................'+str(rover.read_register(0xE01E))+'Min')
	print('Light Voltage.....................'+str(rover.read_register(0xE01F))+'V')
	print('LED load current setting..........'+str(rover.read_register(0xE020)*10)+'mA')
	print('Dimming...........................'+str(rover.read_register(0xE001))+'%')
#	print('UNKNOWN..Special power control....'+str(rover.read_register(0xE021) & 255))
	print('')
	print('LED load current..................'+str(rover.read_register(0xE02C)*10)+'mA')
#	print('UNKNOWN..Special power control....'+str(rover.read_register(0xE02D)))

	print('')
	print('Charging-Parameters:')
	print(' Overvolt treshold................'+str(rover.read_voltage(0xE005))+'V')
	print(' Charge Limit.....................'+str(rover.read_voltage(0xE006))+'V')
	print(' Charge Equalize..................'+str(rover.read_voltage(0xE007))+'V')
	print(' Charge Boost.....................'+str(rover.read_voltage(0xE008))+'V')
	print(' Charge Float.....................'+str(rover.read_voltage(0xE009))+'V')
	print(' Charge Boost Recover.............'+str(rover.read_voltage(0xE00A))+'V')
	print(' Discharge Recover................'+str(rover.read_voltage(0xE00B))+'V')
	print(' Undervoltage warning level.......'+str(rover.read_voltage(0xE00C))+'V')
	print(' Over-discharge...................'+str(rover.read_voltage(0xE00D))+'V')
	print(' Discharging limit................'+str(rover.read_voltage(0xE00E))+'V')
	print(' SOCcharge........................'+str(rover.SOCcharge)+'%')
	print(' SOCdischarge.....................'+str(rover.SOCdischarge)+'%')
	print(' Over-discharge delay.............'+str(rover.read_register(0xE010))+'S')
	print(' Equalizing time..................'+str(rover.read_register(0xE011))+'Min')
	print(' Boost time.......................'+str(rover.read_register(0xE012))+'Min')
	print(' Equalizing intervall.............'+str(rover.read_register(0xE013))+'Day')
	print(' Temp. comp. factor (mV/°C/2V)....'+str(rover.read_register(0xE014)))

	print('')
	print('Stages:')
	print('1st-stage duration................'+str(rover.read_register(0xE015))+'H')
	print('1st-stage power...................'+str(rover.read_register(0xE016))+'%')
	print('2st-stage duration................'+str(rover.read_register(0xE017))+'H')
	print('2st-stage power...................'+str(rover.read_register(0xE018))+'%')
	print('3st-stage duration................'+str(rover.read_register(0xE019))+'H')
	print('3st-stage power...................'+str(rover.read_register(0xE01A))+'%')
	print('4st-stage duration................'+str(rover.read_register(0xE01B))+'H')
	print('4st-stage power...................'+str(rover.read_register(0xE01C))+'%')

	print('')
	print('Working Sense 1...................'+str(rover.read_register(0xE022))+'H')
	print('Power People Sense 1..............'+str(rover.read_register(0xE023))+'%')
	print('Power No People Sense 1...........'+str(rover.read_register(0xE024))+'%')
	print('Working Sense 2...................'+str(rover.read_register(0xE025))+'H')
	print('Power People Sense 2..............'+str(rover.read_register(0xE026))+'%')
	print('Power No People Sense 2...........'+str(rover.read_register(0xE027))+'%')
	print('Working Sense 3...................'+str(rover.read_register(0xE028))+'H')
	print('Power People Sense 3..............'+str(rover.read_register(0xE029))+'%')
	print('Power No People Sense 3...........'+str(rover.read_register(0xE02A))+'%')
	print('Sensing time delay................'+str(rover.read_register(0xE02B))+'S')
