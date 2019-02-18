#!/usr/bin/env python3
# coding: utf-8
# 
# Command template 

from PySide import QtGui, QtCore
import FreeCAD, FreeCADGui, Part, os, math, re

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )

 
class placeLCS:
	"My tool object"

	def GetResources(self):
		return {"MenuText": "Place an LCS in the Assembly",
				"ToolTip": "Attach an LCS to an external Part",
				"Pixmap" : os.path.join( iconPath , 'PlaceLCS.svg')
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
		self.msgBox.setText("Activated placeLCSCmd")
		self.msgBox.exec_()
		#FreeCAD.activeDocument().Tip = FreeCAD.activeDocument().addObject('App::Part','Model')
		#FreeCAD.activeDocument().getObject('Model').newObject('App::DocumentObjectGroup','Constraints')
		#FreeCAD.activeDocument().getObject('Model').newObject('PartDesign::CoordinateSystem','LCS_0')



FreeCADGui.addCommand( 'placeLCSCmd', placeLCS() )
