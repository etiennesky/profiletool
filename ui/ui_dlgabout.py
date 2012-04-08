# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dlgabout import Ui_DlgAbout
import platform
import os


class DlgAbout(QDialog, Ui_DlgAbout):

	def __init__(self, parent=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)

		fp = os.path.join( os.path.abspath(os.path.join(os.path.dirname(__file__),"..")) , "metadata.txt")

		iniText = QSettings(fp, QSettings.IniFormat)
		verno = iniText.value("version").toString()
		name = iniText.value("name").toString()
		description = iniText.value("description").toString()

		self.title.setText( name )
		self.description.setText( description  + " - " + verno)




