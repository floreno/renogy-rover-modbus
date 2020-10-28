#!/usr/bin/python
# -*- coding: utf-8 -*-

# Driver for the Renogy Rover Solar Controller using the Modbus RTU protocol

import string
import minimalmodbus
from decimal import Decimal

PRODUCT_TYPE = {
	0: 'Controller',
	1: 'Inverter',
}
CHARGE_MODE = {
	0: 'DEACTIVATED',
	1: 'ACTIVATED',
	2: 'MPPT',
	3: 'EQUALIZING',
	4: 'BOOST',
	5: 'FLOATINGE',
	6: 'current limiting (overpower)',
}
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


# Battery settings
# Example for a 7s14P 18650 DIY-lithium pack

#	Battery capacity (ignored for now)
BCAP = 30
#	No of batterycells in pack
BCELLS = 7
#	Max. Voltage of one cell (from datasheet)
BCMAXVOLTAGE = 4.2
#	Min. Voltage of one cell (from datasheet)
BCMINVOLTAGE = 2.8

#	Battery safe voltage space
#	per cell decrease max.-V. and increase min.-V. by this Voltage
#	it is for battery save!
BSAFE = 0.1

# Battery calculations
SAFE = (BCELLS*10)*(BSAFE*10)/100
BMAXVOLT = ((BCMAXVOLTAGE*10)*(BCELLS*10))/100
BMINVOLT = ((BCMINVOLTAGE*10)*(BCELLS*10))/100
OVERLIMIT = int( ( BMAXVOLT - ( float( BSAFE ) * 2 ) ) * 100 ) / 100
CHARGELIMIT = OVERLIMIT - 0.2
OVERCHARGE = int( ( BMAXVOLT - ( BSAFE * BCELLS ) ) * 100 ) / 100#CHARGELIMIT - ( BSAFE * 2 )
OVERCHARGE_RECOVER = OVERCHARGE-0.5  #CHARGELIMIT#int( ( OVERCHARGE - ( BSAFE * 3 ) ) * 10 ) / 10
BOOST = CHARGELIMIT
BOOST_RECOVER = int( ( CHARGELIMIT - ( ( BSAFE * BCELLS ) * 3 ) - 0.2 ) * 10 ) / 10
DISCHARGE_RECOVER = (int(((BCMINVOLTAGE+BSAFE) * BCELLS)*10)/10)+5
UNDERVOLTAGE = round((BCMINVOLTAGE+(BSAFE*4)) * BCELLS * 10)/10
OVERDISCHARGE = (BCMINVOLTAGE+BSAFE) * BCELLS + 1
DISCHARGELIMIT = (BCMINVOLTAGE+BSAFE) * BCELLS
#FLOAT = int( ( BOOST - ( ( BOOST - BOOST_RECOVER) / 2 ) ) * 10 ) / 10


class RenogyRover(minimalmodbus.Instrument):

	def __init__(self, portname, slaveaddress):
		minimalmodbus.Instrument.__init__(self, portname, slaveaddress)

  def setregistervolt(self, reg, volt):
		if self.voltage == 24:
			return self.write_registers(reg, [int(volt*10/2)])
		else:
			return self.write_registers(reg, [int(volt*10)])



if __name__ == '__main__':
	rover = RenogyRover('/dev/ttyAMA0', 1)

## Over limit
  rover.setregistervolt(0xE005, OVERLIMIT)
  print("Overlimit " + str(OVERLIMIT))
#	Chargelimit
  rover.setregistervolt(0xE006, CHARGELIMIT)
  print("Chargelimit " + str(CHARGELIMIT))
#	Overcharge
  rover.setregistervolt(0xE007, OVERCHARGE)
  print("Overcharge " + str(OVERCHARGE))
#	Float or Overcharge Recovery
  rover.setregistervolt(0xE009, OVERCHARGE_RECOVER)
  print("Float or Overcharge Recovery" + str(OVERCHARGE_RECOVER))
#	Boost
  rover.setregistervolt(0xE008, BOOST)
  print("Boost " + str(BOOST))
#	Boost-recover
  rover.setregistervolt(0xE00A, BOOST_RECOVER)
  print("Boost Recover" + str(BOOST_RECOVER))
#	Discharge-recover
  rover.setregistervolt(0xE00B, DISCHARGE_RECOVER)
  print("Discharge Recover" + str(DISCHARGE_RECOVER))
#	Undervoltage
  rover.setregistervolt(0xE00C, UNDERVOLTAGE)
  print("Undervoltage" + str(UNDERVOLTAGE))
#	Overdischarge
  rover.setregistervolt(0xE00D, OVERDISCHARGE)
  print("Overdischarge" + str(OVERDISCHARGE))
#	Discharge Limit
  rover.setregistervolt(0xE00E, DISCHARGELIMIT)
  print("Discharge Limit" + str(DISCHARGELIMIT))

