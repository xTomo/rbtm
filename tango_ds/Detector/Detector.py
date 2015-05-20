#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        Detector.py
## 
## Project :     Detector
##
## This file is part of Tango device class.
## 
## Tango is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Tango is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with Tango.  If not, see <http://www.gnu.org/licenses/>.
## 
##
## $Author :      diana.ichalova$
##
## $Revision :    $
##
## $Date :        $
##
## $HeadUrl :     $
##============================================================================
##            This file is generated by POGO
##    (Program Obviously used to Generate tango Object)
##
##        (c) - Software Engineering Group - ESRF
##############################################################################

"""Class for tomograph's detector.
It is used for getting an image of the object being observed

It is written according to
http://sourceforge.net/p/tango-ds/code/HEAD/tree/DeviceClasses/Acquisition/2D/PSCamera/trunk/PSCamera.py"""

__all__ = ["Detector", "DetectorClass", "main"]

__docformat__ = 'restructuredtext'

import PyTango
import sys
# Add additional import
# ----- PROTECTED REGION ID(Detector.additionnal_import) ENABLED START -----#
import numpy as np
import zlib
import json
from multiprocessing import Process, Value


def func(is_run):
    a = 0

    while is_run.value:
        a += 1


# ----- PROTECTED REGION END -----# //  Detector.additionnal_import

## Device States Description
## ON : detector is on
## OFF : detector is off
## FAULT : an error occurred
## RUNNING : detector is taking an image

class Detector (PyTango.Device_4Impl):

    #--------- Add you global variables here --------------------------
    #----- PROTECTED REGION ID(Detector.global_variables) ENABLED START -----#

    def _read_exposure(self):
        self.debug_stream("In _read_exposure()")

        self.debug_stream("Reading exposure...")
        try:
            exposure = self.detector.get_exposure()
        except PyTango.DevFailed as df:
            self.error_stream(str(df))
            raise
        except Exception as e:
            self.error_stream(str(e))
            raise
        self.debug_stream("exposure = {}".format(exposure))

        return exposure

    def _write_exposure(self, new_exposure):
        self.debug_stream("In _write_exposure()")

        self.debug_stream("Setting exposure = {}".format(new_exposure))
        try:
            self.detector.set_exposure(new_exposure)
        except PyTango.DevFailed as df:
            self.error_stream(str(df))
            raise
        except Exception as e:
            self.error_stream(str(e))
            raise
        self.debug_stream("Exposure has been set")

    #----- PROTECTED REGION END -----#  //  Detector.global_variables

    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.debug_stream("In __init__()")
        Detector.init_device(self)
        #----- PROTECTED REGION ID(Detector.__init__) ENABLED START -----#

        #----- PROTECTED REGION END -----#  //  Detector.__init__
        
    def delete_device(self):
        self.debug_stream("In delete_device()")
        #----- PROTECTED REGION ID(Detector.delete_device) ENABLED START -----#

        #----- PROTECTED REGION END -----#  //  Detector.delete_device

    def init_device(self):
        self.debug_stream("In init_device()")
        self.get_device_properties(self.get_device_class())
        self.attr_exposure_read = 0
        self.attr_image_read = ''
        #----- PROTECTED REGION ID(Detector.init_device) ENABLED START -----#

        self.set_state(PyTango.DevState.OFF)

        try:
            self.debug_stream("Creating link to detector driver...")
            self.debug_stream("Link created")
        except PyTango.DevFailed as df:
            self.error_stream(str(df))
            raise
        except Exception as e:
            self.error_stream(str(e))
            raise

        self.set_state(PyTango.DevState.ON)

        #----- PROTECTED REGION END -----#  //  Detector.init_device

    def always_executed_hook(self):
        self.debug_stream("In always_excuted_hook()")
        #----- PROTECTED REGION ID(Detector.always_executed_hook) ENABLED START -----#

        #----- PROTECTED REGION END -----#  //  Detector.always_executed_hook

    #-----------------------------------------------------------------------------
    #    Detector read/write attribute methods
    #-----------------------------------------------------------------------------
    
    def read_exposure(self, attr):
        self.debug_stream("In read_exposure()")
        # ----- PROTECTED REGION ID(Detector.exposure_read) ENABLED START -----#
        attr.set_value(self.attr_exposure_read)
        # ----- PROTECTED REGION END -----# //  Detector.exposure_read
        
    def write_exposure(self, attr):
        self.debug_stream("In write_exposure()")
        data=attr.get_write_value()
        #----- PROTECTED REGION ID(Detector.exposure_write) ENABLED START -----#

        new_exposure = data
        self.attr_exposure_read = new_exposure

        #----- PROTECTED REGION END -----#  //  Detector.exposure_write
        
    def read_image(self, attr):
        self.debug_stream("In read_image()")
        #----- PROTECTED REGION ID(Detector.image_read) ENABLED START -----#
        attr.set_value(self.attr_image_read)
        
        #----- PROTECTED REGION END -----#	//	Detector.image_read
        
    
    
        #----- PROTECTED REGION ID(Detector.initialize_dynamic_attributes) ENABLED START -----#

        #----- PROTECTED REGION END -----#  //  Detector.initialize_dynamic_attributes
            
    def read_attr_hardware(self, data):
        self.debug_stream("In read_attr_hardware()")
        #----- PROTECTED REGION ID(Detector.read_attr_hardware) ENABLED START -----#

        #----- PROTECTED REGION END -----#  //  Detector.read_attr_hardware


    #-----------------------------------------------------------------------------
    #    Detector command methods
    #-----------------------------------------------------------------------------
    
    def GetFrame(self):
        """ Returns image from detector
        
        :param : 
        :type: PyTango.DevVoid
        :return: 
        :rtype: PyTango.DevString """
        self.debug_stream("In GetFrame()")
        argout = ''
        #----- PROTECTED REGION ID(Detector.GetFrame) ENABLED START -----#

        prev_state = self.get_state()
        self.set_state(PyTango.DevState.RUNNING)

        is_run = Value("i", 1)
        p = Process(target=func, args=(is_run, ))
        p.start()

        self.debug_stream("Starting acquisition...")
        try:
            with open('Detector/data.txt') as f:
                # image = f.read()
                import csv
                reader = csv.reader(f, delimiter='\t')
                your_list = list(reader)
                image = np.asarray(your_list, dtype=np.int16)
        except PyTango.DevFailed as df:
            self.set_state(PyTango.DevState.FAULT)
            self.error_stream(str(df))
            raise
        except Exception as e:
            self.set_state(PyTango.DevState.FAULT)
            self.error_stream(str(e))
            raise
        self.debug_stream("Image returned")

        is_run.value = 0
        p.join()

        self.set_state(prev_state)

        #image = json.dumps(image.tolist())
        #image = zlib.compress(image, 6)
        #print(len(image))

        #self.attr_image_read = image

        #return ('image', image)

        with open('Detector/DATA_14') as f:
            argout = f.read()
        # print(argout)

        # ----- PROTECTED REGION END -----# //  Detector.GetFrame
        return argout
        

class DetectorClass(PyTango.DeviceClass):
    #--------- Add you global class variables here --------------------------
    #----- PROTECTED REGION ID(Detector.global_class_variables) ENABLED START -----#

    #----- PROTECTED REGION END -----#  //  Detector.global_class_variables

    def dyn_attr(self, dev_list):
        """Invoked to create dynamic attributes for the given devices.
        Default implementation calls
        :meth:`Detector.initialize_dynamic_attributes` for each device
    
        :param dev_list: list of devices
        :type dev_list: :class:`PyTango.DeviceImpl`"""
    
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                import traceback
                dev.warn_stream("Failed to initialize dynamic attributes")
                dev.debug_stream("Details: " + traceback.format_exc())
        #----- PROTECTED REGION ID(Detector.dyn_attr) ENABLED START -----#

                #----- PROTECTED REGION END -----#  //  Detector.dyn_attr

    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        }


    #    Command definitions
    cmd_list = {
        'GetFrame':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevString, "none"]],
        }


    #    Attribute definitions
    attr_list = {
        'exposure':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label': "exposure time",
                'unit': "0,1 ms",
                'standard unit': "10E-4",
                'max value': "160000",
                'min value': "1",
                'description': "exposure time",
            } ],
        'image':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ]],
        }


def main():
    try:
        py = PyTango.Util(sys.argv)
        py.add_class(DetectorClass,Detector,'Detector')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e

if __name__ == '__main__':
    main()
