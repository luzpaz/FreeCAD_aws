#!/usr/bin/env python3
# coding: utf-8
# 
# Command template 

from PySide import QtGui, QtCore
import FreeCAD, FreeCADGui, Part, os, math, re

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )


class newBody:
	"My tool object"

	def GetResources(self):
		return {"MenuText": "Create a new Body in the Model",
				"Accel": "Ctrl+B",
				"ToolTip": "Create a new Body in the Model",
				"Pixmap" : os.path.join( iconPath , 'PartDesign_Body.svg')
				}

	def IsActive(self):
		if FreeCAD.ActiveDocument == None:
			return False
		else:
			return True

	def Activated(self):
		# do something here...
		bodyName = 'Body'
		text,ok = QtGui.QInputDialog.getText(None,'Create new Body in Model','Enter new Body name :                                        ', text = bodyName)
		if ok and text:
			FreeCAD.activeDocument().getObject('Model').newObject( 'PartDesign::Body', text )

FreeCADGui.addCommand( 'newBodyCmd', newBody() )
