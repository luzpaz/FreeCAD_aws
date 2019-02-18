#!/usr/bin/env python3
# coding: utf-8
# 
# Command template 

from PySide import QtGui, QtCore
import FreeCAD, FreeCADGui, Part, os, math, re

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )


class newModel:
	"My tool object"

	def GetResources(self):
		return {"MenuText": "Create a new Model",
				"Accel": "Ctrl+M",
				"ToolTip": "Create a new Model",
				"Pixmap" : os.path.join( iconPath , 'Model.svg')
				}

	def IsActive(self):
		if FreeCAD.ActiveDocument == None:
			return False
		else:
			return True

	def Activated(self):
		# create a new App::Part called 'Model'
		FreeCAD.activeDocument().Tip = FreeCAD.activeDocument().addObject('App::Part','Model')
		FreeCAD.activeDocument().getObject('Model').newObject('App::DocumentObjectGroup','Constraints')
		FreeCAD.activeDocument().getObject('Model').newObject('PartDesign::CoordinateSystem','LCS_0')


FreeCADGui.addCommand( 'newModelCmd', newModel() )
