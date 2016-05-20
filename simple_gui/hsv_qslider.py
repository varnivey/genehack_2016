#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Grigoriy A. Armeev, 2014
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as·
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License v2 for more details.

import sys
from PyQt4 import QtGui, QtCore

class slider(QtGui.QWidget):
    
    def __init__(self):
        super(slider, self).__init__()
            
        style = """QSlider::groove:horizontal {
border: 1px solid #bbb;
background: qlineargradient(x1: 0, x2: 1,
    stop: 0 red, stop: 0.166666667 #ff0, stop: 0.333333333 #0f0, stop: 0.5 #0ff, stop: 0.666666667 #00f, stop: 0.833333333 #f0f, stop: 1.0 #f00);
height: 13px;
margin-left: 5px;
margin-right: 5px;
border-radius: 4px;
}

QSlider::sub-page:horizontal {
border: 1px solid #777;
height: 10px;
border-radius: 4px;
margin-left: 5px;
}

QSlider::add-page:horizontal {
border: 1px solid #777;
height: 10px;
border-radius: 4px;
margin-right: 5px;
}

QSlider::handle:horizontal {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #eee, stop:1 #ccc);
border: 1px solid #777;
width: 10px;
height: 7px;
margin-left: -5px;
margin-right: -5px;
margin-top: 5px;
margin-bottom: -1px;
border-radius: 2px;
}

QSlider::handle:horizontal:hover {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #fff, stop:1 #ddd);
border: 1px solid #444;
border-radius: 2px;
}

QSlider::sub-page:horizontal:disabled {
background: #bbb;
border-color: #999;
}

QSlider::add-page:horizontal:disabled {
background: #eee;
border-color: #999;
}

QSlider::handle:horizontal:disabled {
background: #eee;
border: 1px solid #aaa;
border-radius: 4px;
}

"""
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)

        self.sld.setStyleSheet(style)
        self.sld.setGeometry(0, 0, 190, 20)
        self.sld.setFixedSize(190,16)
        self.sld.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
       
        
        #self.show()

    def setPos(self,pos):    
        self.sld.setValue(pos*99.0)

    def getPos(self):    
        return self.sld.sliderPosition()/99.0
