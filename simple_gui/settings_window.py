from PyQt4 import QtGui, QtCore
import hsv_qslider, copy
from tablewidget import TableWidget


class SettingsWindow(QtGui.QDialog):
      
    def __init__(self,settings):
        super(SettingsWindow, self).__init__()
        
        tabs	= QtGui.QTabWidget(self)    
        tab1	= QtGui.QWidget()	
        tab2	= QtGui.QWidget()
        tab3	= QtGui.QWidget()
        tab4	= QtGui.QWidget()
        
        self.settings = settings        

        tab1layout = QtGui.QGridLayout()
        
        sensitivityLabel = QtGui.QLabel(self)
        sensitivityLabel.setText("Sensitivity:")
        self.sensitivityField = QtGui.QDoubleSpinBox()
        self.sensitivityField.setRange(0,10)
        self.sensitivityField.setDecimals(0)
        self.sensitivityField.setValue(self.settings.sensitivity)
        sensitivityLabel.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        self.sensitivityField.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        tab1layout.addWidget(sensitivityLabel,0,0)
        tab1layout.addWidget(self.sensitivityField,0,1)
        

        min_cell_sizeLabel = QtGui.QLabel(self)
        min_cell_sizeLabel.setText("Minimal cell size:")
        self.min_cell_sizeField = QtGui.QDoubleSpinBox()
        self.min_cell_sizeField.setRange(0,4294967296)
        self.min_cell_sizeField.setDecimals(0)
        self.min_cell_sizeField.setValue(self.settings.min_cell_size)
        min_cell_sizeLabel.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        self.min_cell_sizeField.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        tab1layout.addWidget(min_cell_sizeLabel,1,0)
        tab1layout.addWidget(self.min_cell_sizeField,1,1)
        
        spacer1=QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding) 
        tab1layout.addItem(spacer1,2,0)

        

        tab2layout = QtGui.QGridLayout()

        foci_lookup_sensivityLabel = QtGui.QLabel(self)
        foci_lookup_sensivityLabel.setText("Foci lookup sensitivity")
        self.foci_lookup_sensivityField = QtGui.QDoubleSpinBox()
        self.foci_lookup_sensivityField.setRange(0,100)
        self.foci_lookup_sensivityField.setDecimals(0)
        self.foci_lookup_sensivityField.setValue(self.settings.foci_lookup_sensivity)
        tab2layout.addWidget(foci_lookup_sensivityLabel,0,0)
        tab2layout.addWidget(self.foci_lookup_sensivityField,0,1)
        

        foci_min_val_percLabel = QtGui.QLabel(self)
        foci_min_val_percLabel.setText("Foci area fill percent")
        self.foci_area_fill_percentField = QtGui.QDoubleSpinBox()
        self.foci_area_fill_percentField.setRange(0,100)
        self.foci_area_fill_percentField.setDecimals(0)
        self.foci_area_fill_percentField.setValue(self.settings.foci_area_fill_percent)
        tab2layout.addWidget(foci_min_val_percLabel,1,0)
        tab2layout.addWidget(self.foci_area_fill_percentField,1,1)
        

        min_foci_radiusLabel = QtGui.QLabel(self)
        min_foci_radiusLabel.setText("Min foci radius")
        self.min_foci_radiusField = QtGui.QDoubleSpinBox()
        self.min_foci_radiusField.setRange(0,4294967296)
        self.min_foci_radiusField.setDecimals(0)
        self.min_foci_radiusField.setValue(self.settings.min_foci_radius)
        tab2layout.addWidget(min_foci_radiusLabel,2,0)
        tab2layout.addWidget(self.min_foci_radiusField,2,1)

        max_foci_radiusLabel = QtGui.QLabel(self)
        max_foci_radiusLabel.setText("Max foci radius")
        self.max_foci_radiusField = QtGui.QDoubleSpinBox()
        self.max_foci_radiusField.setRange(0,4294967296)
        self.max_foci_radiusField.setDecimals(0)
        self.max_foci_radiusField.setValue(self.settings.max_foci_radius)
        tab2layout.addWidget(max_foci_radiusLabel,3,0)
        tab2layout.addWidget(self.max_foci_radiusField,3,1)
        
        
        
        
        allowed_foci_overlapLabel = QtGui.QLabel(self)
        allowed_foci_overlapLabel.setText("Allowed foci overlap")
        self.allowed_foci_overlapField = QtGui.QDoubleSpinBox()
        self.allowed_foci_overlapField.setRange(0,100)
        self.allowed_foci_overlapField.setDecimals(0)
        self.allowed_foci_overlapField.setValue(self.settings.allowed_foci_overlap)
        tab2layout.addWidget(allowed_foci_overlapLabel,4,0)
        tab2layout.addWidget(self.allowed_foci_overlapField,4,1)
        

        self.set_auto_rescale_box = QtGui.QCheckBox('Auto rescale Foci', self)
        self.set_auto_rescale_box.setChecked(self.settings.normalize_intensity)
        tab2layout.addWidget(self.set_auto_rescale_box,5,1)
        if (self.settings.foci_rescale_min==None) & (self.settings.foci_rescale_max==None):
            self.set_auto_rescale_box.setChecked(True)
        else:
            self.set_auto_rescale_box.setChecked(False)
        self.set_auto_rescale_box.clicked.connect(self.checkEvent)

        foci_rescale_minLabel = QtGui.QLabel(self)
        foci_rescale_minLabel.setText("Foci rescale min:")
        self.foci_rescale_minField = QtGui.QDoubleSpinBox()
        self.foci_rescale_minField.setRange(0,255)
        self.foci_rescale_minField.setSingleStep(0.1)
        try:
            self.foci_rescale_minField.setValue(self.settings.foci_rescale_min)
        except TypeError:
            self.foci_rescale_minField.setValue(0)
        tab2layout.addWidget(foci_rescale_minLabel,6,0)
        tab2layout.addWidget(self.foci_rescale_minField,6,1)
        

        foci_rescale_maxLabel = QtGui.QLabel(self)
        foci_rescale_maxLabel.setText("Foci rescale max:")
        self.foci_rescale_maxField = QtGui.QDoubleSpinBox()
        self.foci_rescale_maxField.setRange(0,255)
        self.foci_rescale_maxField.setSingleStep(0.1)
        try:
            self.foci_rescale_maxField.setValue(self.settings.foci_rescale_max)
        except TypeError:
            self.foci_rescale_maxField.setValue(0)
        tab2layout.addWidget(foci_rescale_maxLabel,7,0)
        tab2layout.addWidget(self.foci_rescale_maxField,7,1)
        
        self.checkEvent()
        
        self.normalize_intensity_box = QtGui.QCheckBox('Normalize intensity', self)
        self.normalize_intensity_box.setChecked(self.settings.normalize_intensity)
        tab2layout.addWidget(self.normalize_intensity_box,8,0)
        
        spacer2=QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding) 
        tab2layout.addItem(spacer2,9,0)
        

        tab3layout = QtGui.QGridLayout()

        self.nucleiColorSlider = hsv_qslider.slider()
        self.nucleiColorSlider.setPos(self.settings.nuclei_color)
        nuclei_colorLabel = QtGui.QLabel(self)
        nuclei_colorLabel.setText("Nuclei color:")
        nuclei_colorLabel.setFixedHeight(20)
        tab3layout.addWidget(nuclei_colorLabel,0,0)
        tab3layout.addWidget(self.nucleiColorSlider,0,1)
        

        self.fociColorSlider = hsv_qslider.slider()
        self.fociColorSlider.setPos(self.settings.foci_color)
        self.fociColorSlider.setFixedHeight(20)
        foci_colorLabel = QtGui.QLabel(self)
        foci_colorLabel.setText("Foci color:")
        foci_colorLabel.setFixedHeight(20)
        tab3layout.addWidget(foci_colorLabel,1,0)
        tab3layout.addWidget(self.fociColorSlider,1,1)
        
        
        self.return_circles_box = QtGui.QCheckBox('Draw foci with circles', self)
        self.return_circles_box.setChecked(self.settings.return_circles)

        tab3layout.addWidget(self.return_circles_box,2,0)

        spacer3=QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)         
        tab3layout.addItem(spacer3,3,0)
        
        tab4layout = QtGui.QVBoxLayout()
        self.tableWidget=TableWidget(self)
        tab4layout.addWidget(self.tableWidget)
        
        
        spacer4=QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding) 
        tab4layout.addSpacerItem(spacer4)
        
        self.setFixedSize(400, 400)
        tabs.resize(400, 400)
        
        tabs.addTab(tab1,"Cell detection")
        tabs.addTab(tab2,"Foci detection")
        tabs.addTab(tab3,"Images")
        tabs.addTab(tab4,"Table")

        tab1.setLayout(tab1layout)
        tab2.setLayout(tab2layout)
        tab3.setLayout(tab3layout)
        tab4.setLayout(tab4layout)
        
    def checkEvent(self):
        if self.set_auto_rescale_box.checkState():
            self.foci_rescale_minField.setEnabled(False)
            self.foci_rescale_maxField.setEnabled(False)
        else:
            self.foci_rescale_minField.setEnabled(True)
            self.foci_rescale_maxField.setEnabled(True)


    def getSettings(self):
        settings=copy.deepcopy(self.settings)
        settings.sensitivity = self.sensitivityField.value()
        settings.min_cell_size = self.min_cell_sizeField.value()
        settings.foci_lookup_sensivity = self.foci_lookup_sensivityField.value()
        settings.foci_area_fill_percent = self.foci_area_fill_percentField.value()
        settings.min_foci_radius = self.min_foci_radiusField.value()
        settings.max_foci_radius = self.max_foci_radiusField.value()
        settings.allowed_foci_overlap = self.allowed_foci_overlapField.value()
        settings.foci_rescale_min = self.foci_rescale_minField.value()
        settings.foci_rescale_min = None if self.set_auto_rescale_box.checkState() else settings.foci_rescale_min
        settings.foci_rescale_max = self.foci_rescale_maxField.value()
        settings.foci_rescale_max = None if self.set_auto_rescale_box.checkState() else settings.foci_rescale_max
        settings.nuclei_color = self.nucleiColorSlider.getPos()
        settings.foci_color = self.fociColorSlider.getPos()
        settings.normalize_intensity = self.normalize_intensity_box.checkState() == QtCore.Qt.Checked
        settings.return_circles = self.return_circles_box.checkState() == QtCore.Qt.Checked
        
        if settings.__dict__ == self.settings.__dict__:
            print "Settings had not changed"
            return settings,False
            
        else:
            print "Settings changed"
            return settings,True
