# -*- coding: utf-8 -*-

import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QRadioButton
from PyQt5.uic import loadUi

import json
from datetime import date
import shutil

class createupdateUser (QDialog):
    def __init__(self):
        super(createupdateUser,self).__init__()
        loadUi('cuWindow.ui',self)

        self.doneBtn.clicked.connect(self.doneInfo)
        self.ipBrowse.clicked.connect(self.browseIP)
        self.opBrowse.clicked.connect(self.browseOP)

        self.createRdBtn.toggled.connect(self.createSelected)
        self.updtRdBtn.toggled.connect(self.updateSelected)

        self.ipLoc = ""
        self.opLoc = ""
        self.userStatus = "Create"

        cwdlst = []
        cwdlst = os.getcwd().split ('\\')
        self.cwd = '/'.join(cwdlst)
        print (self.cwd)
        self.dbFile = os.listdir(self.cwd + "/userSet/")

    def createSelected(self, selected):
        if selected:
            self.userStatus = "Create"
            self.uNameCmb.clear()

            self.uNameDat.clear()
            self.stdyNameDat.clear()
            
            self.uNameCmb.setEnabled(False)
            self.uNameDat.setEnabled(True)
            self.ipFolderLbl.setText("Select In phase folder")
            self.opFolderLbl.setText("Select Out phase folder")
            print ("Create Enabled")
              
    def updateSelected(self, selected):
        if selected:
            self.userStatus = "Update"

            self.uNameDat.clear()
            self.stdyNameDat.clear()
            
            self.uNameCmb.setEnabled(True)
            self.uNameDat.setEnabled(False)
            self.ipFolderLbl.setText("Select In phase folder")
            self.opFolderLbl.setText("Select Out phase folder")
            
            userList = os.listdir(self.cwd + "/userSet/")
            print (self.dbFile)
            for name in userList:
                self.uNameCmb.addItem (name)
                print (name)
            
            print ("Update Enabled")

    def doneInfo (self):
        if self.userStatus == "Create":
            uname = self.uNameDat.text()
        elif self.userStatus == "Update":
            uname = str (self.uNameCmb.currentText())
        ustdyName = self.stdyNameDat.text()

        if len (uname) > 0 and len (ustdyName) > 0:
            userFolderLoc = self.cwd + "/userSet/" + uname + "/"
            parentLoc = userFolderLoc + "dataset/" + ustdyName + "/"

            userIPLoc = parentLoc + "inphase/"
            userOPLoc = parentLoc + "outphase/"

            if self.userStatus == "Create":
                if not os.path.exists(userFolderLoc):
                    if os.path.exists(self.ipLoc) and os.path.exists(self.opLoc):
                        ipFileList = os.listdir(self.ipLoc)
                        opFileList = os.listdir(self.opLoc)

                        if (len (ipFileList) == len (opFileList)) and (len (ipFileList) > 0) and (len (opFileList) > 0):
##                            os.makedirs(userIPLoc)
##                            os.makedirs(userOPLoc)
                            print ("File transfer in progress")
                            shutil.copytree(self.ipLoc, userIPLoc)
                            shutil.copytree(self.opLoc, userOPLoc)

                            print (self.ipLoc, userIPLoc)
                            print (self.opLoc, userOPLoc)

                            try:
                                url = userFolderLoc + uname + "_ffc.json"
                                ROICollection = {}
                                with open (url, 'w') as jsonFile:
                                    json.dump (ROICollection, jsonFile)
                                jsonFile.close()
                            except OSError:
                                msg = QMessageBox()
                                msg.setWindowTitle("Message")
                                msg.setIcon(QMessageBox.Critical)
                                msg.setText("Failed creating the file")
                                x = msg.exec_()
                            else:
                                msg = QMessageBox()
                                msg.setWindowTitle("Message")
                                msg.setText("All Folders Sucessfully Created")
                                x = msg.exec_()
                        else:
                            msg = QMessageBox()
                            msg.setWindowTitle("Message")
                            msg.setIcon(QMessageBox.Critical)
                            msg.setText("Uneven Inphase/Outphase files")
                            x = msg.exec_()
                    else:
                        msg = QMessageBox()
                        msg.setWindowTitle("Message")
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("No such Inphase/Outphase Folder")
                        x = msg.exec_()
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("Message")
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("User Exists, please rename the user")
                    x = msg.exec_()
            if self.userStatus == "Update":
                if not os.path.exists(parentLoc):
                    if os.path.exists(self.ipLoc) and os.path.exists(self.opLoc):
                        ipFileList = os.listdir(self.ipLoc)
                        opFileList = os.listdir(self.opLoc)

                        if (len (ipFileList) == len (opFileList)) and (len (ipFileList) > 0) and (len (opFileList) > 0):
##                            os.makedirs(userIPLoc)
##                            os.makedirs(userOPLoc)

                            print (self.ipLoc, userIPLoc)
                            print (self.opLoc, userOPLoc)
                            
                            print ("File transfer in progress")
                            shutil.copytree(self.ipLoc, userIPLoc)
                            shutil.copytree(self.opLoc, userOPLoc)
                                    
                            msg = QMessageBox()
                            msg.setWindowTitle("Message")
                            msg.setText("All Folders Sucessfully Created")
                            x = msg.exec_()
                        else:
                            msg = QMessageBox()
                            msg.setWindowTitle("Message")
                            msg.setIcon(QMessageBox.Critical)
                            msg.setText("Uneven Inphase/Outphase files")
                            x = msg.exec_()
                    else:
                        msg = QMessageBox()
                        msg.setWindowTitle("Message")
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("No such Inphase/Outphase Folder")
                        x = msg.exec_()
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("Message")
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("User Study Exists, please rename the user study folder")
                    x = msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Message")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Unfilled fields, Please check")
            x = msg.exec_()

    def browseIP (self):
        print ("IP Browse Button Clicked")
        
        self.ipLoc = QFileDialog().getExistingDirectory(self, 'Select InPhase Dicome Folder')
        self.ipFolderLbl.setText(self.ipLoc)

    def browseOP (self):
        print ("OP Browse Button Clicked")
        
        self.opLoc = QFileDialog().getExistingDirectory(self, 'Select OutPhase Dicome Folder')
        self.opFolderLbl.setText(self.opLoc)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = createupdateUser ()
    window.show()
    sys.exit(app.exec_())
