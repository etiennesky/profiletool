# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tools/ui_profiletool.ui'
#
# Created: Sat Mar 17 14:33:36 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ui_profiletool(object):
    def setupUi(self, ui_profiletool):
        ui_profiletool.setObjectName(_fromUtf8("ui_profiletool"))
        ui_profiletool.resize(501, 342)
        ui_profiletool.setWindowTitle(QtGui.QApplication.translate("ui_profiletool", "Profile Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.formLayout = QtGui.QFormLayout(self.dockWidgetContents)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setMargin(2)
        self.formLayout.setSpacing(2)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.tabWidget = QtGui.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_1 = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_1.sizePolicy().hasHeightForWidth())
        self.tab_1.setSizePolicy(sizePolicy)
        self.tab_1.setObjectName(_fromUtf8("tab_1"))
        self.gridlayout = QtGui.QGridLayout(self.tab_1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self._2 = QtGui.QHBoxLayout()
        self._2.setObjectName(_fromUtf8("_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.qwtPlot = QwtPlot(self.tab_1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qwtPlot.sizePolicy().hasHeightForWidth())
        self.qwtPlot.setSizePolicy(sizePolicy)
        self.qwtPlot.setMinimumSize(QtCore.QSize(0, 0))
        self.qwtPlot.setAutoFillBackground(False)
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.gridLayout.addWidget(self.qwtPlot, 0, 1, 1, 1)
        self.scaleSlider = QtGui.QSlider(self.tab_1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scaleSlider.sizePolicy().hasHeightForWidth())
        self.scaleSlider.setSizePolicy(sizePolicy)
        self.scaleSlider.setOrientation(QtCore.Qt.Vertical)
        self.scaleSlider.setObjectName(_fromUtf8("scaleSlider"))
        self.gridLayout.addWidget(self.scaleSlider, 0, 0, 1, 1)
        self._26 = QtGui.QHBoxLayout()
        self._26.setObjectName(_fromUtf8("_26"))
        self.butPrint = QtGui.QPushButton(self.tab_1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.butPrint.sizePolicy().hasHeightForWidth())
        self.butPrint.setSizePolicy(sizePolicy)
        self.butPrint.setMinimumSize(QtCore.QSize(10, 20))
        self.butPrint.setText(QtGui.QApplication.translate("ui_profiletool", "Print", None, QtGui.QApplication.UnicodeUTF8))
        self.butPrint.setObjectName(_fromUtf8("butPrint"))
        self._26.addWidget(self.butPrint)
        self.butPDF = QtGui.QPushButton(self.tab_1)
        self.butPDF.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.butPDF.sizePolicy().hasHeightForWidth())
        self.butPDF.setSizePolicy(sizePolicy)
        self.butPDF.setMinimumSize(QtCore.QSize(10, 20))
        self.butPDF.setText(QtGui.QApplication.translate("ui_profiletool", "Save as PDF", None, QtGui.QApplication.UnicodeUTF8))
        self.butPDF.setObjectName(_fromUtf8("butPDF"))
        self._26.addWidget(self.butPDF)
        self.butSVG = QtGui.QPushButton(self.tab_1)
        self.butSVG.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.butSVG.sizePolicy().hasHeightForWidth())
        self.butSVG.setSizePolicy(sizePolicy)
        self.butSVG.setMinimumSize(QtCore.QSize(10, 20))
        self.butSVG.setText(QtGui.QApplication.translate("ui_profiletool", "Save as SVG", None, QtGui.QApplication.UnicodeUTF8))
        self.butSVG.setObjectName(_fromUtf8("butSVG"))
        self._26.addWidget(self.butSVG)
        self.gridLayout.addLayout(self._26, 1, 1, 1, 1)
        self._2.addLayout(self.gridLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableView = QtGui.QTableView(self.tab_1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setMinimumSize(QtCore.QSize(10, 10))
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout.addWidget(self.tableView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_2 = QtGui.QPushButton(self.tab_1)
        self.pushButton_2.setMinimumSize(QtCore.QSize(10, 20))
        self.pushButton_2.setText(QtGui.QApplication.translate("ui_profiletool", "Add Raster", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setAutoRepeat(False)
        self.pushButton_2.setAutoDefault(False)
        self.pushButton_2.setDefault(False)
        self.pushButton_2.setFlat(False)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton = QtGui.QPushButton(self.tab_1)
        self.pushButton.setMinimumSize(QtCore.QSize(10, 20))
        self.pushButton.setText(QtGui.QApplication.translate("ui_profiletool", "Remove raster", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self._2.addLayout(self.verticalLayout)
        self.gridlayout.addLayout(self._2, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_1, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self._25 = QtGui.QGridLayout(self.tab_4)
        self._25.setObjectName(_fromUtf8("_25"))
        self.label_3 = QtGui.QLabel(self.tab_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(10, 10))
        self.label_3.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.label_3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_3.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_3.setText(QtGui.QApplication.translate("ui_profiletool", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Profile Tool Plugin</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Profile Plugin plots terrain profiles along interactive pointed polylines. It handles  any format supported by QGis. You can compare up to three layers together, control height scale and line colors. Unfortunately it has huge requirements: development version of QGIS and Qwt5.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Please send me your reflections, opinions, suggestions and wishes (especially related to this plugin;) on <a href=\"http://hub.qgis.org/projects/profiletool/issues\"><span style=\" text-decoration: underline; color:#0000ff;\">http://hub.qgis.org/projects/profiletool/issues</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If you find this plugin useful please don\'t hesitate to let me know desired improvements!</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Profile Tool Plugin - License GNU GPL 2</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Written in 2008 by Borys Jurgiel (borys@wolf.most.org.pl)</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Written in 2012 by Borys Jurgiel, Patrice Verchere</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">REQUIREMENTS:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- Qwt5 (python-qwt5-qt4)</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- QT ver 4.1 for saving to PDF and 4.3 for saving to SVG</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setScaledContents(False)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self._25.addWidget(self.label_3, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_4, _fromUtf8(""))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.tabWidget)
        ui_profiletool.setWidget(self.dockWidgetContents)

        self.retranslateUi(ui_profiletool)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ui_profiletool)

    def retranslateUi(self, ui_profiletool):
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QtGui.QApplication.translate("ui_profiletool", "&Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("ui_profiletool", "Table", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("ui_profiletool", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("ui_profiletool", "&About", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.Qwt5 import QwtPlot
