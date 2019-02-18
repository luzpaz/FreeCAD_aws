#!/usr/bin/env python3
# coding: utf-8
# 
# Command template 

from PySide import QtGui, QtCore
import FreeCAD, FreeCADGui, Part, os, math, re

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )


class placeLink:
	"My tool object"

	def GetResources(self):
		return {"MenuText": "Place a linked Part in the Assembly",
				"Accel": "Ctrl+P",
				"ToolTip": "Move an instance of an external Part",
				"Pixmap" : os.path.join( iconPath , 'PlaceLink.svg')
				}

	def IsActive(self):
		if FreeCAD.ActiveDocument == None:
			return False
		else:
			return True

	def Activated(self):
		# do something here...
		self.msgBox = QtGui.QMessageBox()
		self.msgBox.setWindowTitle('Warning')
		self.msgBox.setIcon(QtGui.QMessageBox.Critical)
		self.msgBox.setText("Activated placeLinkCmd")
		self.msgBox.exec_()
		#FreeCAD.activeDocument().Tip = FreeCAD.activeDocument().addObject('App::Part','Model')
		#FreeCAD.activeDocument().getObject('Model').newObject('App::DocumentObjectGroup','Constraints')
		#FreeCAD.activeDocument().getObject('Model').newObject('PartDesign::CoordinateSystem','LCS_0')



FreeCADGui.addCommand( 'placeLinkCmd', placeLink() )
