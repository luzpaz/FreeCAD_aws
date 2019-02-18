#!/usr/bin/env python3
# coding: utf-8
# 
# Command template 

from PySide import QtGui, QtCore
import FreeCAD, FreeCADGui, Part, os, math, re

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )


class newLCS:
	"My tool object"

	def GetResources(self):
		return {"MenuText": "Create a new LCS in the Model",
				"ToolTip": "Create a new LCS in the Model",
				"Pixmap" : os.path.join( iconPath , 'CoordinateSystem.svg')
				}

	def IsActive(self):
		if FreeCAD.ActiveDocument == None:
			return False
		else:
			return True

	def Activated(self):
		# do something here...
		# input dialog to ask the user the name of the LCS:
		lcsName = 'LCS_0'
		text,ok = QtGui.QInputDialog.getText(None,'Create new coordinate system','Enter Local Coordinate System name :                              ', text = lcsName)
		# if everything went well:
		if ok and text:
			FreeCAD.activeDocument().getObject('Model').newObject( 'PartDesign::CoordinateSystem', text )



 
FreeCADGui.addCommand( 'newLCSCmd', newLCS() )
