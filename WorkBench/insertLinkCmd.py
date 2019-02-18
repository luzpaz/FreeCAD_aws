#!/usr/bin/env python3
# coding: utf-8
# 
# Command template 

from PySide import QtGui, QtCore
import FreeCAD, FreeCADGui, Part, os, math, re

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )

#activeDoc = FreeCAD.activeDocument()


"""
    ╔═══════════════════════════════════════════════╗
    ║                  main class                   ║
    ╚═══════════════════════════════════════════════╝
"""
class insertLink( QtGui.QDialog ):
	"My tool object"


	def GetResources(self):
		return {"MenuText": "Insert a Link to an external Part",
				"Accel": "Ctrl+L",
				"ToolTip": "Insert a Link to an external Part",
				"Pixmap" : os.path.join( iconPath , 'LinkModel.svg')
				}


	def IsActive(self):
		if FreeCAD.ActiveDocument == None:
			return False
		else:
			return True


	def Activated(self):
		# This function is executed when the command is activated

		activeDoc = FreeCAD.ActiveDocument

		# the GUI objects are defined later down
		self.drawGUI()

		# Search for all App::Parts in all open documents
		self.getAllParts()

		# build the list
		for part in self.allParts:
			newItem = QtGui.QListWidgetItem()
			newItem.setText( part.Document.Name +" -> "+ part.Name )
			newItem.setIcon(part.ViewObject.Icon)
			self.partList.addItem(newItem)


	"""
    ╔═══════════════════════════════════════════════╗
    ║     defines the UI, only static elements      ║
    ╚═══════════════════════════════════════════════╝
	"""
	def drawGUI(self):
		print('drawing UI')
		# Our main window will be a QDialog
		self.GUIwidget = QtGui.QDialog(self)
		self.GUIwidget.setWindowTitle('Create link 2 a Model')
		self.GUIwidget.setMinimumSize(400, 500)
		self.GUIwidget.resize(400,500)

		# label
		self.labelMain = QtGui.QLabel(self)
		self.labelMain.setText("Select the part to be inserted :")
		self.labelMain.move(10,20)

		# label
		self.labelLink = QtGui.QLabel(self)
		self.labelLink.setText("Enter a Name for the link :\n(Must be unique in the Model tree)")
		self.labelLink.move(10,350)

		# Create a line that will contain the name of the link (in the tree)
		self.linkNameInput = QtGui.QLineEdit(self)
		self.linkNameInput.setMinimumSize(380, 0)
		self.linkNameInput.move(10, 400)
	
		# The part list is a QListWidget
		self.partList = QtGui.QListWidget(self)
		self.partList.move(10,50)
		self.partList.setMinimumSize(380, 280)

		# Cancel button
		self.CancelButton = QtGui.QPushButton('Cancel', self)
		self.CancelButton.setAutoDefault(False)
		self.CancelButton.move(10, 460)

		# create Link button
		self.createLinkButton = QtGui.QPushButton('Insert part', self)
		self.createLinkButton.move(285, 460)
		self.createLinkButton.setDefault(True)

		# Actions
		self.CancelButton.clicked.connect(self.onCancel)
		self.createLinkButton.clicked.connect(self.onCreateLink)
		self.partList.itemClicked.connect( self.onItemClicked)

		self.GUIwidget.show()


	def getAllParts(self):
		# get all App::Part from all open documents
		self.allParts = []
		for doc in FreeCAD.listDocuments().values():
			if doc != activeDoc:
				parts = doc.findObjects("App::Part")
				# there might be more than 1 App::Part per document
				for obj in parts:
					self.allParts.append( obj )


	def onItemClicked( self, item ):
		for selected in self.partList.selectedIndexes():
			# get the selected part
			model = self.allParts[ selected.row() ]
            # set the text of the link to be made to the document where the part is in
			self.linkNameInput.setText(model.Document.Name)


	def onCancel(self):
		print ("Cancelled")
		self.close()


	def onCreateLink(self):
		# parse the selected items 
		# TODO : there should only be 1
		for selected in self.partList.selectedIndexes():
			# get the selected part
			model = self.allParts[ selected.row() ]
		# get the name of the link (as it should appear in the tree)
		linkName = self.linkNameInput.text()
		# create the App::Link to the previously selected model
		createdLink = activeDoc.getObject('Model').newObject( 'App::Link', linkName )
		createdLink.LinkedObject = model
		# because of the unique naming principle of FreeCAD, 
		# the created object might been assigned a different name
		linkName = createdLink.Name
		
		# create an App::FeaturePython for that object in the Constraints group
		constrName = PyFeaturePrefix + linkName
		# if it exists, delete it
		# TODO : a bit aggressive, no ?
		if activeDoc.getObject('Constraints').getObject( constrName ):
			activeDoc.removeObject( constrName )
		# create the constraints feature
		activeDoc.getObject('Constraints').newObject( 'App::FeaturePython', constrName )
		# get the App::FeaturePython itself
		constrFeature = activeDoc.getObject( constrName )
		# store the name of the linked document (only for information)
		constrFeature.addProperty( 'App::PropertyString', 'Linked_File' )
		constrFeature.Linked_File = model.Document.Name
		# store the name of the App::Link this cosntraint refers-to
		constrFeature.addProperty( 'App::PropertyString', 'Link_Name' )
		constrFeature.Link_Name = linkName

		# the constraint and how the part is attached with it 
		# TODO : hard-coded, should do proper error checking
		attPart = 'Parent Assembly'
		attLCS  = 'LCS_0'
		linkLCS = 'LCS_0'

		# populate the App::Link's Expression Engine with this info
		expr = makeExpressionPart( attPart, attLCS, constrName, linkLCS )
		# put this expression into the Expression Engine of the link:
		createdLink.setExpression( 'Placement', expr )

		# add an App::Placement that will be the osffset between attachment and link LCS
		# the last 'Placement' means that the property will be placed in that group
		constrFeature.addProperty( 'App::PropertyPlacement', 'Offset', 'Placement' )
		# store the name of the part where the link is attached to
		constrFeature.addProperty( 'App::PropertyString', 'is_attached_to', 'Placement' )
		constrFeature.is_attached_to = attPart
		# store the name of the LCS in the assembly where the link is attached to
		constrFeature.addProperty( 'App::PropertyString', 'LCS_in_parent', 'Placement' )
		constrFeature.LCS_in_parent = attLCS
		# store the name of the LCS in the assembly where the link is attached to
		constrFeature.addProperty( 'App::PropertyString', 'LCS_in_linkedPart', 'Placement' )
		constrFeature.LCS_in_linkedPart = linkLCS
		# store the expression used in the App::Link's ExpressionEngine
		constrFeature.addProperty( 'App::PropertyString', 'Expression', 'Placement' )
		constrFeature.Expression = expr

		# update the link
		createdLink.recompute()

		# finished
		self.close()


FreeCADGui.addCommand( 'insertLinkCmd', insertLink() )
