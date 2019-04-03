#!/usr/bin/env python3
# coding: utf-8
# 
# Command template 

from PySide import QtGui, QtCore
from libAsm4 import *
import FreeCAD, FreeCADGui, Part, os, math, re


__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )



"""
    ╔═══════════════════════════════════════════════╗
    ║                  main class                   ║
    ╚═══════════════════════════════════════════════╝
"""
class placeLCS( QtGui.QDialog ):
	"My tool object"


	def __init__(self):
		super(placeLCS,self).__init__()
		self.selectedLCS = []


	def GetResources(self):
		return {"MenuText": "Place an LCS in the Assembly",
				"ToolTip": "Attach an LCS to an external Part",
				"Pixmap" : os.path.join( iconPath , 'PlaceLCS.svg')
				}


	def IsActive(self):
		# is there an active document ?
		if FreeCAD.ActiveDocument:
			# is something selected ?
			if FreeCADGui.Selection.getSelection():
				return True
		else:
			return(False)


	"""
    ╔═══════════════════════════════════════════════╗
    ║                 the real stuff                ║
    ╚═══════════════════════════════════════════════╝
	"""
	def Activated(self):
		
		# get the current active document to avoid errors if user changes tab
		self.activeDoc = FreeCAD.activeDocument()

		# check that we have selected a PartDesign::CoordinateSystem
		selection = self.checkSelectionLCS()
		if not selection:
			self.close()
		else:
			self.selectedLCS = selection

		# Now we can draw the UI
		self.drawUI()
		self.show()

		# get and save the current ExpressionEngine:
		old_EE = self.selectedLCS.ExpressionEngine
		if old_EE:
			( pla, EE ) = old_EE[0]
		else:
			EE = 'megszentsegtelenithetetlensegeskedeseitekert'
		# decode the old ExpressionEngine
		# <<LinkName>>.Placement.multiply( <<LinkName>>.<<LCS.>>.Placement )
		# if the decode is unsuccessful, old_Expression is set to False
		# and old_attPart and old_attLCS are set to 'None'
		( self.old_Expression, self.old_attPart, self.old_attLCS ) = splitExpressionDatum( EE )

		# Search for all App::Links in the current document
		allLinkedParts = self.getAllLinkedParts()
		# Now populate the list with the (linked) sister parts
		for part in allLinkedParts:
			itemIcon = part.LinkedObject.ViewObject.Icon
			itemText = part.Name
			itemObj = part
			# fill the parent selection combo-box
			self.parentList.addItem( itemIcon, itemText, itemObj)

		# find the oldPart in the part list...
		oldPart = self.parentList.findText( self.old_attPart )
		if oldPart:
			# ... and select it
			self.parentList.setCurrentIndex( oldPart )
		# this should have triggered to fill the LCS list
		# find the oldLCS in the list of LCS of the linked part...
		oldLCS = self.attLCSlist.findItems( self.old_attLCS, QtCore.Qt.CaseSensitive )
		if oldLCS:
			# ... and select it
			self.attLCSlist.setCurrentItem( oldLCS[0], QtGui.QItemSelectionModel.Select )

		#self.msgBox = QtGui.QMessageBox()
		#self.msgBox.setWindowTitle('Warning')
		#self.msgBox.setIcon(QtGui.QMessageBox.Critical)
		#self.msgBox.setText("Activated placeLCSCmd")
		#self.msgBox.exec_()
		#FreeCAD.activeDocument().Tip = FreeCAD.activeDocument().addObject('App::Part','Model')
		#FreeCAD.activeDocument().getObject('Model').newObject('App::DocumentObjectGroup','Constraints')
		#FreeCAD.activeDocument().getObject('Model').newObject('PartDesign::CoordinateSystem','LCS_0')



	"""
    ╔═══════════════════════════════════════════════╗
    ║ check that all necessary things are selected, ║
    ║   populate the expression with the selected   ║
    ║    elements, put them into the constraint     ║
    ║   and trigger the recomputation of the part   ║
    ╚═══════════════════════════════════════════════╝
	"""
	def onApply(self):
		# get the name of the part to attach to:
		# it's either the top level part name ('Model')
		# or the provided link's name.
		a_Part = self.parentList.currentText()

		# the attachment LCS's name in the parent
		# check that something is selected in the QlistWidget
		if self.attLCSlist.selectedItems():
			a_LCS = self.attLCSlist.selectedItems()[0].text()
		else:
			a_LCS = None

		# check that all of them have something in
		# constrName has been checked at the beginning
		if not a_Part or not a_LCS :
			self.expression.setText( 'Problem in selections' )
		else:
			# don't forget the last '.' !!!
			# <<LinkName>>.Placement.multiply( <<LinkName>>.<<LCS.>>.Placement )
			# expr = '<<'+ a_Part +'>>.Placement.multiply( <<'+ a_Part +'>>.<<'+ a_LCS +'.>>.Placement )'
			expr = makeExpressionDatum( a_Part, a_LCS )
			# this can be skipped when this method becomes stable
			self.expression.setText( expr )
			# load the built expression into the Expression field of the constraint
			self.activeDoc.getObject( self.selectedLCS.Name ).setExpression( 'Placement', expr )
			# recompute the object to apply the placement:
			self.selectedLCS.recompute()
			# highlight the selected LCS in its new position
			FreeCADGui.Selection.clearSelection()
			FreeCADGui.Selection.addSelection( self.activeDoc.Name, 'Model', self.selectedLCS.Name +'.')
		return



	"""
    ╔═══════════════════════════════════════════════╗
    ║   find all the linked parts in the assembly   ║
    ╚═══════════════════════════════════════════════╝
	"""
	def getAllLinkedParts(self):
		allLinkedParts = [ ]
		for obj in self.activeDoc.findObjects("App::Link"):
			# add it to our list if it's a link to an App::Part
			if obj.LinkedObject.isDerivedFrom('App::Part'):
				allLinkedParts.append( obj )
		return allLinkedParts


	"""
    ╔═══════════════════════════════════════════════╗
    ║           get all the LCS in a part           ║
    ╚═══════════════════════════════════════════════╝
	"""
	def getPartLCS( self, part ):
		partLCS = [ ]
		# parse all objects in the part (they return strings)
		for objName in part.getSubObjects():
			# get the proper objects
			# all object names end with a "." , this needs to be removed
			obj = part.getObject( objName[0:-1] )
			if obj.TypeId == 'PartDesign::CoordinateSystem':
				partLCS.append( obj )
		return partLCS


	"""
    ╔═══════════════════════════════════════════════╗
    ║   fill the LCS list when chaining the parent   ║
    ╚═══════════════════════════════════════════════╝
	"""
	def onParentList(self):
		# clear the LCS list
		self.attLCSlist.clear()
		# clear the selection in the GUI window
		FreeCADGui.Selection.clearSelection()
		# the current text in the combo-box is the link's name...
		parentName = self.parentList.currentText()
		# ... or it's 'Parent Assembly' then the parent is the 'Model' root App::Part
		if parentName =='Parent Assembly':
			Parent = self.activeDoc.getObject( 'Model' )
			# we get the LCS directly in the root App::Part 'Model'
			partLCS = self.getPartLCS( Parent )
			self.parentDoc.setText( Parent.Document.Name )
		# a sister object is an App::Link
		# the .LinkedObject is an App::Part
		else:
			Parent = self.activeDoc.getObject( parentName )
			# we get the LCS from the linked part
			partLCS = self.getPartLCS( Parent.LinkedObject )
			self.parentDoc.setText( Parent.LinkedObject.Document.Name )
			# highlight the selected part:
			FreeCADGui.Selection.addSelection( Parent.Document.Name, 'Model', Parent.Name+'.' )
		# build the list
		for lcs in partLCS:
			newItem = QtGui.QListWidgetItem()
			newItem.setText( lcs.Name )
			newItem.setIcon( lcs.ViewObject.Icon )
			self.attLCSlist.addItem( newItem )
		return


	"""
    ╔═══════════════════════════════════════════════╗
    ║  An LCS has been clicked in 1 of the 2 lists  ║
    ║              We highlight both LCS             ║
    ╚═══════════════════════════════════════════════╝
	"""
	def onLCSclicked( self ):
		# clear the selection in the GUI window
		FreeCADGui.Selection.clearSelection()
		# get the part where the selected LCS is
		a_Part = self.parentList.currentText()
		# LCS in the parent
		a_LCS = self.attLCSlist.selectedItems()[0].text()
		# parent assembly and sister part need a different treatment
		if a_Part == 'Parent Assembly':
			linkDot = ''
		else:
			linkDot = a_Part+'.'
		# Gui.Selection.addSelection('asm_Test','Model','Lego_3001.LCS_h2x1.')
		# Gui.Selection.addSelection('asm_Test','Model','LCS_0.')
		FreeCADGui.Selection.addSelection( self.activeDoc.Name, 'Model', linkDot+a_LCS+'.')
		return


	"""
    ╔═══════════════════════════════════════════════╗
    ║                     Cancel                    ║
    ║           restores the previous values        ║
    ╚═══════════════════════════════════════════════╝
	"""
	def onCancel(self):
		# restore previous expression if it existed
		if self.old_Expression:
			self.selectedLCS.setExpression('Placement', self.old_Expression )
		self.selectedLCS.recompute()
		# highlight the selected LCS in its new position
		FreeCADGui.Selection.clearSelection()
		FreeCADGui.Selection.addSelection( self.activeDoc.Name, 'Model', self.selectedLCS.Name +'.')
		self.close()


	"""
    ╔═══════════════════════════════════════════════╗
    ║                      OK                       ║
    ║               accept and close                ║
    ╚═══════════════════════════════════════════════╝
	"""
	def onOK(self):
		self.onApply()
		self.close()


	"""
    ╔═══════════════════════════════════════════════╗
    ║     defines the UI, only static elements      ║
    ╚═══════════════════════════════════════════════╝
	"""
	def drawUI(self):
		# Our main window will be a QDialog
		self.setWindowTitle('Place Coordinate System')
		self.setMinimumSize(370, 570)
		self.resize(370,570)
		self.setModal(False)
		# make this dialog stay above the others, always visible
		self.setWindowFlags( QtCore.Qt.WindowStaysOnTopHint )
		
		# Part, Left side
		#
		# Selected Link label
		self.lcsLabel = QtGui.QLabel(self)
		self.lcsLabel.setText("Selected LCS :")
		self.lcsLabel.move(10,20)
		# the name as seen in the tree of the selected link
		self.lscName = QtGui.QLineEdit(self)
		self.lscName.setReadOnly(True)
		self.lscName.setText( self.selectedLCS.Name )
		self.lscName.setMinimumSize(150, 1)
		self.lscName.move(150,18)

		# combobox showing all available App::Link 
		self.parentList = QtGui.QComboBox(self)
		self.parentList.move(10,80)
		self.parentList.setMinimumSize(350, 1)
		# initialize with an explanation
		self.parentList.addItem('Select attachment Parent')

		# label
		self.parentLabel = QtGui.QLabel(self)
		self.parentLabel.setText("Parent Document :")
		self.parentLabel.move(10,120)
		# the document containing the linked object
		self.parentDoc = QtGui.QLineEdit(self)
		self.parentDoc.setReadOnly(True)
		self.parentDoc.setMinimumSize(300, 1)
		self.parentDoc.move(30,150)
		# label
		self.labelRight = QtGui.QLabel(self)
		self.labelRight.setText("Select LCS in Parent :")
		self.labelRight.move(10,200)
		# The list of all attachment LCS in the assembly is a QListWidget
		# it is populated only when the parent combo-box is activated
		self.attLCSlist = QtGui.QListWidget(self)
		self.attLCSlist.move(10,240)
		self.attLCSlist.setMinimumSize(350, 200)

		# Expression
		#
		# expression label
		self.labelExpression = QtGui.QLabel(self)
		self.labelExpression.setText("Expression Engine :")
		self.labelExpression.move(10,450)
		# Create a line that will contain full expression for the expression engine
		self.expression = QtGui.QLineEdit(self)
		self.expression.setMinimumSize(350, 0)
		self.expression.move(10, 480)

		# Buttons
		#
		# Cancel button
		self.CancelButton = QtGui.QPushButton('Cancel', self)
		self.CancelButton.setAutoDefault(False)
		self.CancelButton.move(10, 530)

		# Apply button
		self.ApplyButton = QtGui.QPushButton('Apply', self)
		self.ApplyButton.setAutoDefault(False)
		self.ApplyButton.move(150, 530)
		self.ApplyButton.setDefault(True)

		# OK button
		self.OKButton = QtGui.QPushButton('OK', self)
		self.OKButton.setAutoDefault(False)
		self.OKButton.move(280, 530)
		self.OKButton.setDefault(True)

		# Actions
		self.CancelButton.clicked.connect(self.onCancel)
		self.ApplyButton.clicked.connect(self.onApply)
		self.OKButton.clicked.connect(self.onOK)
		self.parentList.currentIndexChanged.connect( self.onParentList )
		self.attLCSlist.itemClicked.connect( self.onLCSclicked )


	"""
    ╔═══════════════════════════════════════════════╗
    ║                 initial check                 ║
    ╚═══════════════════════════════════════════════╝
	"""
	def checkSelectionLCS(self):
		# check that there is an App::Part called 'Model'
		# a standard App::Part would also do, but then more error checks are necessary
		if not self.activeDoc.getObject('Model') or not self.activeDoc.getObject('Model').TypeId=='App::Part' :
			msgBox = QtGui.QMessageBox()
			msgBox.setWindowTitle('Warning')
			msgBox.setIcon(QtGui.QMessageBox.Critical)
			msgBox.setText("This placement is not compatible with this assembly.")
			msgBox.exec_()
			return(False)
		# check that something is selected
		if not FreeCADGui.Selection.getSelection():
			msgBox = QtGui.QMessageBox()
			msgBox.setWindowTitle('Warning')
			msgBox.setIcon(QtGui.QMessageBox.Critical)
			msgBox.setText("Please select a linked part.")
			msgBox.exec_()
			return(False)
		# set the (first) selected object as global variable
		selectedObj = FreeCADGui.Selection.getSelection()[0]
		# check that the selected object is of App::Link type
		if not selectedObj.isDerivedFrom('PartDesign::CoordinateSystem'):
			msgBox = QtGui.QMessageBox()
			msgBox.setWindowTitle('Warning')
			msgBox.setIcon(QtGui.QMessageBox.Critical)
			msgBox.setText("Please select a coordinate system.")
			msgBox.exec_()
			return(False)
		# now we should be safe
		return( selectedObj )



FreeCADGui.addCommand( 'placeLCSCmd', placeLCS() )
