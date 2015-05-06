#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

__author__ = 'tomas'

import sys, os, subprocess, traceback
import logging
import ConfigParser
from PyQt4.QtCore import *
from PyQt4 import QtGui
import platform
import ctypes

class Button(QtGui.QPushButton):

    def __init__(self, title, parent):
        super(Button, self).__init__(title, parent)

        #self.setAcceptDrops(True)

    def dragEnterEvent(self, e):

        #e.accept()
        #return
        # mp4 mpg4
        if(e.mimeData().hasFormat("video/mp4")):
            logging.info("video/mp4")
            e.accept()
        # mpeg mpg mpe
        elif(e.mimeData().hasFormat("video/mpeg")):
            logging.info("video/mpeg")
            e.accept()
        # ogv
        elif(e.mimeData().hasFormat("video/ogg")):
            logging.info("video/ogg")
            e.accept()

        # qt, mov
        elif(e.mimeData().hasFormat("video/quicktime")):
            logging.info("video/quicktime")
            e.accept()
        # avi
        elif(e.mimeData().hasFormat("video/x-msvideo")):
            logging.info("video/x-msvideo")
            e.accept()

        # flv
        elif (e.mimeData().hasFormat("video/x-flv")):
            logging.info("video/x-flv")
            e.accept()

        # webm
        elif (e.mimeData().hasFormat("video/webm")):
            logging.info("video/webm")
            e.accept()
        else:
            logging.info(e.mimeData().getFormat())
            e.ignore()

    def dropEvent(self, e):
        self.setText(e.mimeData().urls()[0].toLocalFile())#text())
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                logging.info(path)

class FileArea(QtGui.QLineEdit):

    def __init__(self, title, parent):
        super(FileArea, self).__init__(title, parent)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.accept()
        return

    def dropEvent(self, e):
        self.setText(e.mimeData().urls()[0].toLocalFile())#text())
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                logging.info(path)

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        self.edit = FileArea('', self)
        self.edit.setDragEnabled(True)
        self.edit.move(30, 65)
        self.edit.setReadOnly(True)

        button = Button("Open file", self)
        button.move(190, 65)
        button.clicked.connect(self.showDialog)

        self.setWindowTitle('Post Bellum VideoWall')
        self.setGeometry(300, 300, 300, 150)

        formLayout = QtGui.QFormLayout()

        fileL = QtGui.QHBoxLayout()
        fileL.addWidget(self.edit)
        fileL.addWidget(button)
        formLayout.addRow("soubor",fileL)

        lanOptions = QtGui.QHBoxLayout()
        self.master = QtGui.QCheckBox()
        self.ip = QtGui.QLineEdit()
        self.ip.setDisabled(True)
        self.master.stateChanged.connect(self.set_master)

        lanOptions.addWidget(self.master)
        lanOptions.addWidget(self.ip)
        formLayout.addRow("master, IP addr",lanOptions)

        self.sound = QtGui.QComboBox()
        self.sound.addItem("stereo")
        self.sound.addItem("5.1")
        self.sound.addItem("mute")
        formLayout.addRow("zvuk",self.sound)

        self.osd = QtGui.QComboBox()
        self.osd.addItem("none")
        self.osd.addItem("all")
        formLayout.addRow("osd", self.osd)

        self.dual = QtGui.QCheckBox()
        formLayout.addRow("dual",self.dual)

        okButton = QtGui.QPushButton("OK")
        okButton.clicked.connect(self.runMplayer)
        cancelButton = QtGui.QPushButton("Close")
        cancelButton.clicked.connect(sys.exit)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(formLayout)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()

        self.load_current_state()
        if self.getIpAddr():
            self.ip.setText(self.getIpAddr())

    def showDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                              '/home')
        name = str(fname)
        if os.path.exists(name):
            self.edit.setText(os.path.normpath(name))

    def set_master(self):
        self.ip.setEnabled(not self.ip.isEnabled())

    def getIpAddr(self):
        command = ""
        is_windows = any(platform.win32_ver())
        if is_windows:
            command = "ipconfig /all"
        else:
            command = "ifconfig"
        status = subprocess.check_output(command, shell=True)
        logging.info(status)
        p = re.compile(ur'\s+IPv4 Address.*: ([\d\.]+)', re.MULTILINE)
        return re.findall(p, status)[0] if re.findall(p, status) else []


    def runMplayer(self):
        args = "mplayer -vo gl2 -idle -fixed-vo -noborder"
        if self.osd.currentText() == "none":
            args += " -osdlevel 0"
        if self.sound.currentText() == "5.1":
            args += " -channels 6"
        elif self.sound.currentText() == "mute":
            args += " -nosound"
        if self.master.isChecked():
            args += " -udp-master -udp-ip {}".format(self.get_broadcast_address())
        else:
            args += " -udp-slave"
        if self.dual.isChecked():
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
            args += " -geometry {}x{}+0+0".format(2*w,h)
        args += " " + self.edit.text()
        logging.info(args)
        self.save_current_state()
        status = subprocess.Popen("{}".format(args), shell=True)
        logging.info(status)

    def get_broadcast_address(self):
        ip = str(self.ip.text()).split(".")
        try:
            [int(i) for i in ip]
        except:
            logging.info("Error parsing ip")
        broadcast_ip = ".".join(ip[:3]+["255"])
        return broadcast_ip


    def save_current_state(self):
        config = ConfigParser.RawConfigParser()
        config.add_section('GlobalOptions')
        config.set('GlobalOptions', 'file', self.edit.text())
        config.set('GlobalOptions', 'master', self.master.isChecked())
        config.set('GlobalOptions', 'ip', self.ip.text())
        config.set('GlobalOptions', 'sound', self.sound.currentIndex())
        config.set('GlobalOptions', 'osd', self.osd.currentIndex())

        with open('config.cfg', 'wb') as configfile:
            config.write(configfile)

    def load_current_state(self):
        config = ConfigParser.RawConfigParser()
        try:
            config.read('config.cfg')
            file_name = config.get('GlobalOptions', 'file')
            if os.path.exists(file_name):
                self.edit.setText(file_name)
            master = config.getboolean('GlobalOptions', 'master')
            self.master.setChecked(master)
            ip = config.get('GlobalOptions','ip')
            self.ip.setText(ip)
            sound = config.getint('GlobalOptions', 'sound')
            self.sound.setCurrentIndex(sound)
            osd = config.getint('GlobalOptions', 'osd')
            self.osd.setCurrentIndex(osd)
        except:
            logging.info("Error loading config file")
            traceback.print_exc(file=sys.stdout)


def main():
    """logging into file"""
    logging.basicConfig(filename='pb_video_wall.log',level=logging.INFO)
    """logging to the console"""
    # logging.basicConfig(level=logging.INFO)

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec_()


if __name__ == '__main__':

    main()