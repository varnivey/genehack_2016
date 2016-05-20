#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is a part of DARFI project (dna Damage And Repair Foci Imager)
#    Copyright (C) 2014  Ivan V. Ozerov, Grigoriy A. Armeev
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as·
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License v2 for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys,os, pickle
sys.path.append(os.path.join('..','engine'))
import folder_widget
import settings_window
from settings import Settings
from tablewidget import TableWidget
from PyQt4 import QtGui, QtCore


#### Uncomment these lines if building py2exe binary with window output only
## import warnings
## warnings.simplefilter('ignore')

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class CusLabel(QtGui.QLabel):
    def __init__(self, parent, key=None):
        super(CusLabel, self).__init__(parent)
        self.parent=parent
        self.key=key
        self.setMouseTracking(True)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.hoverMouse)


    def mousePressEvent(self, e):

        super(CusLabel, self).mousePressEvent(e)
        self.parent.labelClicked(e,self.key)

    def mouseMoveEvent(self, e):
        super(CusLabel, self).mouseMoveEvent(e)
        self.coord= [e.x(),e.y()]
        self.timer.stop()
        self.timer.start(600)

    def hoverMouse(self):
        #print self.coord
        self.timer.stop()





class DarfiUI(QtGui.QMainWindow):

    def __init__(self):
        super(DarfiUI, self).__init__()
        self.settings=Settings()
        self.workDir=unicode(QtCore.QDir.currentPath())
        self.showMiniatures=True
        self.oldDirsWithImages=[]
        self.oldFoci_rescale_min = None
        self.oldFoci_rescale_max = None
        self.lastCalc=False
        self.settingsChanged=True
        self.initUI()
        if os.path.isfile(os.path.join(unicode(QtCore.QDir.currentPath()),"Darfi_session.dcf")):
            self.readSettings(os.path.join(unicode(QtCore.QDir.currentPath()),"Darfi_session.dcf"))


    def loadDefaultSettings(self):
        self.settings=Settings()
        self.settings.foci_name=self.fociNameComboBox.currentText()
        self.settings.nuclei_name=self.nuclNameComboBox.currentText()
        self.fileMenuArea.setWorkDir(self.workDir)
        print "Default settings loaded"



    def dumpSettings(self,filename=None):
        if not(filename):
            filename=unicode(QtGui.QFileDialog.getSaveFileName(self,'Write DARFI config file', '','DARFI Config File, *.dcf;;All Files (*)'))
        if ((filename != "") & (self.settings.nuclei_name!='')):

            #that is rude but it works (
            if filename[-4:] != '.dcf':
                filename+=unicode('.dcf')
            with open(filename, 'w+') as f:
                #self.tableWidget.getOrders()
                print self.settings.rowOrder
                print self.settings.columnOrder
                pickle.dump([self.fileMenuArea.workDir,self.settings,self.fileMenuArea.getCheckedPaths()], f)

    def readSettings(self,filename=None):
        if not(filename):
            filename=unicode(QtGui.QFileDialog.getOpenFileName(self,'Open DARFI config file', '','DARFI Config File, *.dcf;;All Files (*)'))
        if filename != "":
            with open(filename) as f:
                print "Loading previous config"
                try:
                    self.workDir,self.settings, paths = pickle.load(f)
                    self.fileMenuArea.openWorkDir(self.workDir)
                    self.fileMenuArea.setCheckedFromPaths(paths)
                    if self.settings.foci_name=='--None--':
                        self.rescaleButton.setEnabled(False)
                    else:
                        self.rescaleButton.setEnabled(True)
                except ValueError:
                    print "Save file is corrupted or incompatible \n Loading default"


    def openSettings(self):
        self.settingsWindow = settings_window.SettingsWindow(self.settings)
        self.settingsWindow.exec_()
        self.settings,self.settingsChanged = self.settingsWindow.getSettings()

    def closeEvent(self, event):
        print "Closing DARFI, goodbye"
        filename=os.path.join(unicode(QtCore.QDir.currentPath()),"Darfi_session.dcf")
        self.dumpSettings(filename)


    def resizeEvent( self, oldsize):
        ''' override resize event to redraw pictures'''
        self.updateImages()


    def setNuclei_name(self,text):
        self.settings.nuclei_name = unicode(text)
        self.fileMenuArea.openWorkDir(self.workDir)

    def setFoci_name(self,text=None):
        self.settings.foci_name = unicode(text)
        self.fileMenuArea.changeFociImages()
        if self.settings.foci_name=='--None--':
            self.rescaleButton.setEnabled(False)
        else:
            self.rescaleButton.setEnabled(True)



    def refreshImages(self):
        self.showMiniatures=True
        self.updateImages()

    def refreshImage(self):
        self.showMiniatures=False
        self.updateImages()

    def labelClicked(self,event,key):
        if not(self.showMiniatures):
            imageName = self.fileMenuArea.selectedImage
            if not((os.path.basename(imageName) == self.settings.nuclei_name) |
                (os.path.basename(imageName) == self.settings.foci_name)):
                originalSize = QtGui.QPixmap(imageName).size()
                coordx =(event.x()/float(self.lbl1.width()))*originalSize.width()
                coordy=(event.y()/float(self.lbl1.height()))*originalSize.height()
                coord = [round(coordx),round(coordy)]
                if not(self.fileMenuArea.touchCellAndRedraw(coord)):
                    self.showMiniatures = True
                    self.fileMenuArea.selectedImage = ''
                    self.updateImages()
            else:
                self.showMiniatures = True
                self.fileMenuArea.selectedImage = ''
                self.updateImages()

        else:
            self.showMiniatures = False
            self.fileMenuArea.selectedImage = unicode(self.fileMenuArea.selectedImageDir.absolutePath() + QtCore.QDir.separator() + self.imageNameList[key])
            self.updateImages()

    def saveParams(self):

        filename=QtGui.QFileDialog.getSaveFileName(self,'Save results of latest calculation'
            , self.workDir + str(os.sep) + \
            'result.xlsx','Microsoft Excel file, *.xlsx;;CSV File, *.csv;;All Files (*)')
        if not filename.isEmpty():

            try:
                if filename[-4:] == 'xlsx':
                    self.tableWidget.handleSaveXLSX(filename)
                else:
                    self.tableWidget.handleSaveCSV (filename)
                print "File saved!"
            except:
                print "Error file saving!"

    def updateImages(self):
        if self.showMiniatures:
            try:
                self.lbl1.clear()

                imageDir = self.fileMenuArea.selectedImageDir
                if imageDir=="":
                    self.lbl1.clear()
                    self.lbl2.clear()
                    self.lbl3.clear()
                    self.lbl4.clear()
                    self.lbl5.clear()
                    self.lbl6.clear()
                else:
                    path = imageDir.absolutePath()
                    #FIXME use margins e.t.c
                    sizex=self.imagePreviewArea.width()/2-10
                    sizey=self.imagePreviewArea.height()/3-10
                    filters = ["*.jpg", "*.JPG"]
                    imageDir.setNameFilters(filters)
                    self.imageNameList = [self.settings.nuclei_name, self.settings.foci_name]
                    [self.imageNameList.append(i) for i in imageDir.entryList(filters,sort= QtCore.QDir.Name|QtCore.QDir.Type)]
                    try:

                        pix1 = QtGui.QPixmap(path + QtCore.QDir.separator() + self.imageNameList[0])
                        self.lbl1.resize(sizex,sizey)
                        self.lbl1.setPixmap(pix1.scaled(self.lbl1.size(), QtCore.Qt.KeepAspectRatio))
                        self.lbl1.update()

                    except IndexError:
                        self.lbl1.clear()

                    try:
                        pix2 = QtGui.QPixmap(path + QtCore.QDir.separator() + self.imageNameList[1])
                        self.lbl2.resize(sizex,sizey)

                        self.lbl2.setPixmap(pix2.scaled(self.lbl2.size(), QtCore.Qt.KeepAspectRatio))
                        self.lbl2.update()
                    except IndexError:
                        self.lbl2.clear()


                    try:
                        pix = QtGui.QPixmap(path + QtCore.QDir.separator() + self.imageNameList[2])
                        self.lbl3.resize(sizex,sizey)
                        self.lbl3.update()
                        self.lbl3.setPixmap(pix.scaled(self.lbl3.size(), QtCore.Qt.KeepAspectRatio))
                        self.lbl3.update()
                    except IndexError:
                        self.lbl3.clear()

                    try:
                        pix = QtGui.QPixmap(path + QtCore.QDir.separator() + self.imageNameList[3])
                        self.lbl4.resize(sizex,sizey)
                        self.lbl4.setPixmap(pix.scaled(self.lbl4.size(), QtCore.Qt.KeepAspectRatio))
                        self.lbl4.update()
                    except IndexError:
                        self.lbl4.clear()

                    try:
                        pix = QtGui.QPixmap(path + QtCore.QDir.separator() + self.imageNameList[4])
                        self.lbl5.resize(sizex,sizey)
                        self.lbl5.setPixmap(pix.scaled(self.lbl5.size(), QtCore.Qt.KeepAspectRatio))
                        self.lbl5.update()
                    except IndexError:
                        self.lbl5.clear()

                    try:
                        pix = QtGui.QPixmap(path + QtCore.QDir.separator() + self.imageNameList[5])
                        self.lbl6.resize(sizex,sizey)
                        self.lbl6.setPixmap(pix.scaled(self.lbl6.size(), QtCore.Qt.KeepAspectRatio))
                        self.lbl6.update()
                    except IndexError:
                        self.lbl6.clear()
            except AttributeError:
                ()
        else:
            imageName = self.fileMenuArea.selectedImage
            pix1 = QtGui.QPixmap(imageName)
            self.lbl2.clear()
            self.lbl2.resize(0,0)
            self.lbl3.clear()
            self.lbl3.resize(0,0)
            self.lbl4.clear()
            self.lbl4.resize(0,0)
            self.lbl5.clear()
            self.lbl5.resize(0,0)
            self.lbl6.clear()
            self.lbl6.resize(0,0)
            sizex=self.imagePreviewArea.width()-30
            sizey=self.imagePreviewArea.height()-60
            self.lbl1.resize(sizex,sizey)
            self.lbl1.setPixmap(pix1.scaled(self.lbl1.size(), QtCore.Qt.KeepAspectRatio))
            self.lbl1.update()


    def initUI(self):


################## FILEMENU AREA  ########################################

        self.fileMenuArea = folder_widget.FolderWidget(self)
        self.fileMenuArea.signal_update_images.connect(self.refreshImages)
        self.fileMenuArea.signal_update_image.connect(self.refreshImage)

################## IMAGE AREA  ########################################

        self.imagePreviewArea = QtGui.QScrollArea(self)

        self.imagePreviewLayout = QtGui.QGridLayout(self.imagePreviewArea)
        self.connect(self.imagePreviewArea, QtCore.SIGNAL("resizeEvent()"), self.updateImages)
        self.lbl1 = CusLabel(self,0)
        self.imagePreviewLayout.addWidget(self.lbl1, 0,0)
        self.lbl2 = CusLabel(self,1)
        self.imagePreviewLayout.addWidget(self.lbl2, 0,1)
        self.lbl3 = CusLabel(self,2)
        self.imagePreviewLayout.addWidget(self.lbl3, 1,0)
        self.lbl4 = CusLabel(self,3)
        self.imagePreviewLayout.addWidget(self.lbl4, 1,1)
        self.lbl5 = CusLabel(self,4)
        self.imagePreviewLayout.addWidget(self.lbl5, 2,0)
        self.lbl6 = CusLabel(self,5)
        self.imagePreviewLayout.addWidget(self.lbl6, 2,1)

################## SETTINGS AREA  ########################################

        buttonArea = QtGui.QWidget(self)
        buttonLayout = QtGui.QVBoxLayout(buttonArea)

        self.openSettingsButton = QtGui.QPushButton("Settings")
        self.openSettingsButton.clicked.connect(self.openSettings)
        buttonLayout.addWidget(self.openSettingsButton)
        self.pbar = QtGui.QProgressBar(self)





        nuclNameFieldLabel = QtGui.QLabel(self)
        nuclNameFieldLabel.setText("Files with nuclei:")
        self.nuclNameComboBox = QtGui.QComboBox(self)
        self.nuclNameComboBox.activated[str].connect(self.setNuclei_name)
        buttonLayout.addWidget(nuclNameFieldLabel)
        buttonLayout.addWidget(self.nuclNameComboBox)

        fociNameFieldLabel = QtGui.QLabel(self)
        fociNameFieldLabel.setText("Files with foci:")
        self.fociNameComboBox = QtGui.QComboBox(self)
        self.fociNameComboBox.addItem('--None--')
        self.fociNameComboBox.activated[str].connect(self.setFoci_name)

        buttonLayout.addWidget(fociNameFieldLabel)
        buttonLayout.addWidget(self.fociNameComboBox)




        self.rescaleButton = QtGui.QPushButton("Get scale from selection")
        self.rescaleButton.clicked.connect(self.fileMenuArea.getScaleFromSelected)
        buttonLayout.addWidget(self.rescaleButton)

        runCalcButton = QtGui.QPushButton("Calculate")
        runCalcButton.clicked.connect(self.fileMenuArea.calculateSelected)
        runCalcButton.setMinimumHeight(40)
        buttonLayout.addWidget(runCalcButton)



        self.pbar.hide()
        buttonLayout.addWidget(self.pbar)

        #spacer=QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        #buttonLayout.addSpacerItem(spacer)

        self.tableWidget=TableWidget(self)

        tabs = QtGui.QTabWidget(self)
        #_______________________________________
        #buttonLayout.addWidget(self.tableWidget)

        tab1=QtGui.QWidget()
        tab1Layout=QtGui.QVBoxLayout(tab1)
        tabs.addTab(tab1,"Results")
        tab1Layout.addWidget(self.tableWidget)



        self.outfileButton = QtGui.QPushButton("Save results")
        self.outfileButton.clicked.connect(self.saveParams)
        self.outfileButton.setEnabled(False)
        tab1Layout.addWidget(self.outfileButton)

        self.singleCellOutputBox = QtGui.QCheckBox('Single cell output', self)
        self.singleCellOutputBox.setEnabled(False)
        self.singleCellOutputBox.stateChanged.connect(self.fileMenuArea.updateParamsTable)
        tab1Layout.addWidget(self.singleCellOutputBox)



        nuclLogLabel = QtGui.QLabel(self)


        self.logText = QtGui.QTextEdit()
        #self.logText.setMaximumHeight(130)
        self.logText.setReadOnly(True)
        self.logText.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.logText.append("Welcome to DARFI! ")
        self.logger = Logger(self.logText)
        #self.errors = Logger(self.logText)
        sys.stdout = self.logger
        #sys.stderr = self.errors
        #________________________________
        #buttonLayout.addWidget(self.logText)
        tabs.addTab(self.logText,"Log")
        buttonLayout.addWidget(tabs)


        buttonLayout.setAlignment(QtCore.Qt.AlignTop)






################## COMPOSITING  ########################################



        windowInitWidth = 1300
        windowInitHeight = 768


        icon = QtGui.QIcon()

        homepath = os.path.abspath(os.path.dirname(os.getcwd()))
        iconpath = os.path.join(homepath, 'misc', 'darfi.ico')

        if os.path.isfile(iconpath):
            icon.addPixmap(QtGui.QPixmap(_fromUtf8(iconpath)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon.addPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(os.getcwd(), 'misc', 'darfi.ico'))), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        hbox = QtGui.QHBoxLayout()

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.imagePreviewArea)
        splitter1.addWidget(buttonArea)
        splitter1.setSizes([windowInitWidth-480,240])
        splitter1.splitterMoved.connect(self.updateImages)

        '''
        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.statusArea)
        splitter2.setSizes([windowInitHeight-200,windowInitHeight/200])
        splitter2.splitterMoved.connect(self.updateImages)
        '''

        splitter3 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter3.addWidget(self.fileMenuArea)
        splitter3.addWidget(splitter1)
        splitter3.setSizes([240,windowInitWidth-240])
        splitter3.splitterMoved.connect(self.updateImages)

        hbox.addWidget(splitter3)

        hboxWidget=QtGui.QWidget(self)
        hboxWidget.setLayout(hbox)
        self.setCentralWidget(hboxWidget)

        self.setGeometry(0, 0,windowInitWidth, windowInitHeight)
        self.setWindowTitle('DARFI')
        self.setWindowIcon(icon)
        self.createActions()
        self.createMenus()
        self.show()

    ################## MAIN MENU AREA  ########################################

    def createActions(self):
        self.settingsAct = QtGui.QAction("&Settings...", self, shortcut="Ctrl+S",triggered=self.openSettings)

        self.settingsDefAct = QtGui.QAction("&Load Defaults...", self, shortcut="Ctrl+D",triggered=self.loadDefaultSettings)

        self.openSettingsAct = QtGui.QAction("&Load settings...", self, shortcut="Ctrl+R",triggered=self.readSettings)

        self.saveSettingsAct = QtGui.QAction("&Write settings...", self, shortcut="Ctrl+W",triggered=self.dumpSettings)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",triggered=self.close)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.settingsAct)
        self.fileMenu.addAction(self.settingsDefAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openSettingsAct)
        self.fileMenu.addAction(self.saveSettingsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = QtGui.QMenu("&About", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.helpMenu)

    def about(self):
        QtGui.QMessageBox.about(self, "About DARFI",
                "<p><b>DARFI</b> is short of dna Damage And Repair Foci Imager <br>"
                "Copyright (C) 2014  Ivan V. Ozerov<br>"
                "This program is free software; you can redistribute it and/or modify "
                "it under the terms of the GNU General Public License version 2 as "
                "published by the Free Software Foundation.</p>")




class Logger(object):
    def __init__(self, output):
        self.output = output

    def write(self, string):
        if not (string == "\n" ):
            trstring = QtGui.QApplication.translate("MainWindow", string.rstrip(), None, QtGui.QApplication.UnicodeUTF8)
            self.output.append(trstring)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = DarfiUI()
    ex.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
