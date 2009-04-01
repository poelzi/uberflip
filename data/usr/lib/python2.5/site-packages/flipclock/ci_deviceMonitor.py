#!/usr/bin/python2.5

import dbus
import dbus.glib
import dbus.service
import gobject, time, thread, os


import ci_init as ci
import ci_eventHandlers


# BME = Battery Monitor Events?
BME_REQ_PATH="/com/nokia/bme/request"
BME_REQ_IFC ="com.nokia.bme.request"

class BMERequest(dbus.service.Object):
    def __init__(self, bus_name, object_path=BME_REQ_PATH):
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.signal(BME_REQ_IFC)
    def status_info_req(self):
        print "sent"


class BatteryMonitor:
  def __init__(self):
    self.bus = dbus.SystemBus(private=True)
    self.bus.add_signal_receiver(self.handle_charging_off,"charger_charging_off")
    #self.bus.add_signal_receiver(self.handle_charging_on ,"charger_charging_on" )
    self.bus.add_signal_receiver(self.handle_charging_off,"charger_disconnected")
    self.bus.add_signal_receiver(self.handle_charging_on ,"charger_connected" )
    self.name = dbus.service.BusName(BME_REQ_IFC, bus=self.bus)
    self.charging = 0
    ci.charging = 0
    #We assume by default that charger is attached, since this is the only possible time when we
    #won't get a BME response
    self.handle_charging_on(self)
	
    e = BMERequest(self.name)
    e.status_info_req()

  def handle_charging_on(self,sender=None):
	print "ac connected"
	self.charging = 1
	ci.charging = 1
	if (ci.inactive == 1):
		ci_eventHandlers.drawClockEvent()


  def handle_charging_off(self,sender=None):
	print "ac disconnected"
	self.charging = 0
	ci.charging = 0



class ScreenMonitor:
  def __init__(self):
    self.bus = dbus.SystemBus(private=True)
    obj = self.bus.get_object('com.nokia.mce', '/com/nokia/mce/signal')
    iface = dbus.Interface(obj, 'com.nokia.mce.signal')
    iface.connect_to_signal("display_status_ind", self.handler)

  def handler(self,sender=None):
    status = "%s" % (sender,)
    print "screen is %s" % (status,)

def maemo_helper(*args):
	batterymon = BatteryMonitor()
	screenmon  = ScreenMonitor()
	
	
#thread.start_new_thread(maemo_helper, (None,))


