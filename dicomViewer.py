# -*- coding: utf-8 -*-

import sys
import cv2
import numpy as np
import imutils
import os
import pydicom
import json
import matplotlib.pyplot as plt

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QTimer

from datetime import date
from cuScript import createupdateUser


dicomRoiCollection = {}
ROICollection = {}

roiIndex = -1
datasetUser = ''

tempFFC = {}

class dicomeViewer(QDialog):
    def __init__(self):
        super(dicomeViewer,self).__init__()
        loadUi('dicomViewer.ui',self)

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create ('Fusion'))
        

        self.cuBtn.clicked.connect(self.cu_User)
        self.refreshBtn.clicked.connect(self.refresh)

        self.uName.clear()
        self.uStudy.clear()
        self.uName.currentTextChanged.connect(self.onUnameChanged)
        self.uStudy.currentTextChanged.connect(self.onStudyChanged)
        
        self.laodBtn.clicked.connect(self.loadImage)
        self.prevBtn.clicked.connect(self.PrevImage)
        self.nextBtn.clicked.connect(self.NextImage)
        self.roiBtn.clicked.connect(self.roi_selection)
        self.zmIPBtn.clicked.connect(self.zoomIP)
        self.zmOPBtn.clicked.connect(self.zoomOP)

        self.cBtn.clicked.connect(self.clockwise)
        self.ccBtn.clicked.connect(self.counterclockwise)
        self.vfBtn.clicked.connect(self.verticalflip)
        self.hfBtn.clicked.connect(self.horizontalflip)

        self.brightSlid.valueChanged['int'].connect (self.brightness_value)
        self.contrastSlid.valueChanged['int'].connect (self.blur_value)

        self.saveStdyBtn.clicked.connect (self.saveStudy)
        self.slideShwBtn.clicked.connect (self.slideshow)

        cwdlst = []
        self.currentUser = ""
        self.currentUserPath = ""

        self.userCaseStudyLst = []
        self.currentUserCasestudy = ""
        self.currentCasestudyPath = ""

        self.userDataSetLst = []
        self.currentUserDataSetPath = ""
        
        self.userCaseStudyLst = []
        self.currentUserCasestudy = ""
        self.currentCasestudyPath = ""

        self.currentUserIPPath = ""
        self.currentUserOPPath = ""
        self.currentUserIPFileLst = []
        self.currentUserOPFileLst = []

        self.flippedIPDCM = np.empty((0))
        self.flippedOPDCM = np.empty((0))
        
        cwdlst = os.getcwd().split ('\\')

        self.cwd = '/'.join(cwdlst)
        print (self.cwd)
        self.userSetPath = self.cwd + "/userSet/"
        self.usersetLst = os.listdir (self.userSetPath)
        print (len (self.usersetLst))

        if len (self.usersetLst) > 0:
            self.uName.clear()            
            for name in self.usersetLst:
                self.uName.addItem (name)

            self.currentUser = self.uName.currentText()
            self.currentUserPath = self.userSetPath + self.currentUser + "/"
            print (self.currentUser)

            self.userDataSetLst = []
            for studyFolder in os.listdir(self.currentUserPath):
                if os.path.isdir(os.path.join(self.currentUserPath, studyFolder)):
                    self.userDataSetLst.append (studyFolder)

            self.currentUserDataSetPath = self.currentUserPath + self.userDataSetLst[0] + "/"
            self.userCaseStudyLst = os.listdir(self.currentUserDataSetPath)
            
            self.uStudy.clear()
            if len (self.userCaseStudyLst) > 0:
                for name in self.userCaseStudyLst:
                    self.uStudy.addItem (name)
            
            self.uName.setEnabled (True)
            self.uStudy.setEnabled (True)
            print ("Ok")
        else:
            self.uName.setEnabled(False)
            self.uStudy.setEnabled(False)

        self.userFldrLst = []
        self.dcmFileLoc = None
        self.dcmIPFileName = None
        self.dcmOPFileName = None

        self.roiJsonLoc = None
        self.currentUserroiJsonFile = None

        self.loadedImgID = 0
        self.loadedImgID_temp = 1
        self.imageCount = 0

        self.scale = 1
        self.dcmFilesize = 0

        self.brightness_value_now = 256
        self.blur_value_now = 128

    def cu_User (self):
        self.cuUserWindow = createupdateUser ()
        self.cuUserWindow.show()

    def refresh (self):
        self.ipView.setText ("Inphase View")
        self.opView.setText ("Outphase View")
        self.ffcView.setText ("FFC")
        self.mffcTbl.clear ()

        self.sosClassDat.setText ("Nil")
        self.pNameDat.setText ("Nil")
        self.pIDDat.setText ("Nil")
        self.modalityDat.setText ("Nil")
        self.stdyDateDat.setText ("Nil")
        self.imgSizDat.setText ("Nil")
        self.pxlSpaceDat.setText ("Nil")
        self.slicingLocDat.setText ("Nil")
        self.stnNameDat.setText ("Nil")
        self.stdyDiscDat.setText ("Nil")
        self.mnfDat.setText ("Nil")
        self.instNameDat.setText ("Nil")

        self.prevBtn.setEnabled (False)
        self.nextBtn.setEnabled (False)
        self.roiBtn.setEnabled (False)
        self.zmIPBtn.setEnabled (False)
        self.zmOPBtn.setEnabled (False)
        self.cBtn.setEnabled (False)
        self.ccBtn.setEnabled (False)
        self.vfBtn.setEnabled (False)
        self.hfBtn.setEnabled (False)
        self.brightSlid.setEnabled (False)
        self.contrastSlid.setEnabled (False)
        self.saveStdyBtn.setEnabled (False)
        self.slideShwBtn.setEnabled (False) 
        self.hotkeyLbl.setEnabled (False)
            
        self.usersetLst = os.listdir (self.userSetPath)
        if len (self.usersetLst) > 0:
            self.uName.clear()
            
            for name in self.usersetLst:
                self.uName.addItem (name)

            self.currentUser = self.uName.currentText()
            self.currentUserPath = self.userSetPath + self.currentUser + "/"

            self.userDataSetLst = []
            for studyFolder in os.listdir(self.currentUserPath):
                if os.path.isdir(os.path.join(self.currentUserPath, studyFolder)):
                    self.userDataSetLst.append (studyFolder)

            self.currentUserDataSetPath = self.currentUserPath + self.userDataSetLst[0] + "/"

            self.userCaseStudyLst = os.listdir(self.currentUserDataSetPath)
##            print (self.userCaseStudyLst)
            self.uStudy.clear()
            if len (self.userCaseStudyLst) > 0:
                for name in self.userCaseStudyLst:
                    self.uStudy.addItem (name)
            
            self.uName.setEnabled (True)
            self.uStudy.setEnabled (True)
        else:
            self.uName.setEnabled(False)
            self.uStudy.setEnabled(False)

    def onUnameChanged (self, value):
        self.ipView.setText ("Inphase View")
        self.opView.setText ("Outphase View")
        self.ffcView.setText ("FFC")
        self.mffcTbl.clear ()

        self.sosClassDat.setText ("Nil")
        self.pNameDat.setText ("Nil")
        self.pIDDat.setText ("Nil")
        self.modalityDat.setText ("Nil")
        self.stdyDateDat.setText ("Nil")
        self.imgSizDat.setText ("Nil")
        self.pxlSpaceDat.setText ("Nil")
        self.slicingLocDat.setText ("Nil")
        self.stnNameDat.setText ("Nil")
        self.stdyDiscDat.setText ("Nil")
        self.mnfDat.setText ("Nil")
        self.instNameDat.setText ("Nil")

        self.prevBtn.setEnabled (False)
        self.nextBtn.setEnabled (False)
        self.roiBtn.setEnabled (False)
        self.zmIPBtn.setEnabled (False)
        self.zmOPBtn.setEnabled (False)
        self.cBtn.setEnabled (False)
        self.ccBtn.setEnabled (False)
        self.vfBtn.setEnabled (False)
        self.hfBtn.setEnabled (False)
        self.brightSlid.setEnabled (False)
        self.contrastSlid.setEnabled (False)
        self.saveStdyBtn.setEnabled (False)
        self.slideShwBtn.setEnabled (False) 
        self.hotkeyLbl.setEnabled (False)
        
        self.uStudy.clear()
        self.currentUser = self.uName.currentText()
        self.currentUserPath = self.userSetPath + self.currentUser + "/"

        self.userDataSetLst = []
        for studyFolder in os.listdir(self.currentUserPath):
            if os.path.isdir(os.path.join(self.currentUserPath, studyFolder)):
                self.userDataSetLst.append (studyFolder)

        self.currentUserDataSetPath = self.currentUserPath + self.userDataSetLst[0] + "/"

        self.userCaseStudyLst = os.listdir(self.currentUserDataSetPath)
        if len (self.userCaseStudyLst) > 0:
            for name in self.userCaseStudyLst:
                self.uStudy.addItem (name)
                    
        self.currentUser = self.uName.currentText()
        self.currentUserPath = self.userSetPath + self.currentUser + "/"
        self.currentUserDataSetPath = self.currentUserPath + value + "/dataset/"

    def onStudyChanged (self, value):
        self.ipView.setText ("Inphase View")
        self.opView.setText ("Outphase View")
        self.ffcView.setText ("FFC")
        self.mffcTbl.clear ()

        self.sosClassDat.setText ("Nil")
        self.pNameDat.setText ("Nil")
        self.pIDDat.setText ("Nil")
        self.modalityDat.setText ("Nil")
        self.stdyDateDat.setText ("Nil")
        self.imgSizDat.setText ("Nil")
        self.pxlSpaceDat.setText ("Nil")
        self.slicingLocDat.setText ("Nil")
        self.stnNameDat.setText ("Nil")
        self.stdyDiscDat.setText ("Nil")
        self.mnfDat.setText ("Nil")
        self.instNameDat.setText ("Nil")

        self.prevBtn.setEnabled (False)
        self.nextBtn.setEnabled (False)
        self.roiBtn.setEnabled (False)
        self.zmIPBtn.setEnabled (False)
        self.zmOPBtn.setEnabled (False)
        self.cBtn.setEnabled (False)
        self.ccBtn.setEnabled (False)
        self.vfBtn.setEnabled (False)
        self.hfBtn.setEnabled (False)
        self.brightSlid.setEnabled (False)
        self.contrastSlid.setEnabled (False)
        self.saveStdyBtn.setEnabled (False)
        self.slideShwBtn.setEnabled (False) 
        self.hotkeyLbl.setEnabled (False)
        
        self.currentUser = self.uName.currentText()
        self.currentUserPath = self.userSetPath + self.currentUser + "/"

        self.userDataSetLst = []
        for studyFolder in os.listdir(self.currentUserPath):
            if os.path.isdir(os.path.join(self.currentUserPath, studyFolder)):
                self.userDataSetLst.append (studyFolder)

        self.currentUserDataSetPath = self.currentUserPath + self.userDataSetLst[0] + "/"                    
        self.currentUserCasestudy = self.uStudy.currentText()
        self.currentCasestudyPath = self.currentUserDataSetPath + self.currentUser + "/"        

    def loadImage(self):
        if len (self.usersetLst) > 0:
            self.currentUser = self.uName.currentText()
            self.currentUserCasestudy = self.uStudy.currentText()

            self.currentUserPath = self.userSetPath + self.currentUser + "/"
            self.userDataSetLst = []
            for FileorDir in os.listdir(self.currentUserPath):
                if os.path.isdir(os.path.join(self.currentUserPath, FileorDir)):
                    self.currentUserDataSetPath = self.currentUserPath + FileorDir + "/"
                if not os.path.isdir(os.path.join(self.currentUserPath, FileorDir)):
                    self.currentUserroiJsonFile = self.currentUserPath + FileorDir

            self.currentCasestudyPath = self.currentUserDataSetPath + self.currentUserCasestudy + "/"
            print (self.currentUserroiJsonFile)
            print (self.currentUserDataSetPath)
            print (self.currentCasestudyPath)

            self.currentUserIPPath = self.currentCasestudyPath + "inphase/"
            self.currentUserOPPath = self.currentCasestudyPath + "outphase/"
            self.currentUserIPFileLst = os.listdir(self.currentUserIPPath)
            self.currentUserOPFileLst = os.listdir(self.currentUserOPPath)
            self.imageCount = len (self.currentUserIPFileLst)

            self.dcmIPFileName = self.currentUserIPPath + str (self.currentUserIPFileLst [self.loadedImgID])
            self.dcmOPFileName = self.currentUserOPPath + str (self.currentUserOPFileLst [self.loadedImgID])
            print (self.dcmIPFileName)
            print (self.dcmOPFileName)
            print ("")

            self.displayOnTable ()

            ds = pydicom.dcmread (self.dcmIPFileName)
            sos = str (ds.SOPClassUID) + "\n" + str (ds.SOPClassUID.name)

            pat_name = ds.PatientName
            pNamedat = pat_name.family_name + ", " + pat_name.given_name

            pIDdat = str (ds.PatientID)
            modality = str (ds.Modality)
            studyDate = str (ds.StudyDate)
            imgSize = str (ds.Rows) + " x " + str (ds.Columns)
            pxlSpacing = str (ds.PixelSpacing)
            sliceLoc = str (ds.get('SliceLocation', '(missing)'))
            stationNm = str (ds.get('StationName', '(missing)'))
            studyDis = str (ds.get('StudyDescription', '(missing)'))
            manufacturer = str (ds.Manufacturer)
            inistituteNam = str (ds.get('InstitutionName', '(missing)'))

            self.ffcView.setText ("FFC")

            self.sosClassDat.setText(sos)
            self.pNameDat.setText(pNamedat)
            self.pIDDat.setText(pIDdat)
            self.modalityDat.setText(modality)
            self.stdyDateDat.setText(studyDate)
            self.imgSizDat.setText(imgSize)
            self.pxlSpaceDat.setText(pxlSpacing)
            self.slicingLocDat.setText(sliceLoc)
            self.stnNameDat.setText(stationNm)
            self.stdyDiscDat.setText(studyDis)
            self.mnfDat.setText(manufacturer)
            self.instNameDat.setText(inistituteNam)

            self.prevBtn.setEnabled (True)
            self.nextBtn.setEnabled (True)
            self.roiBtn.setEnabled (True)
            self.zmIPBtn.setEnabled (True)
            self.zmOPBtn.setEnabled (True)
            self.cBtn.setEnabled (True)
            self.ccBtn.setEnabled (True)
            self.vfBtn.setEnabled (True)
            self.hfBtn.setEnabled (True)
            self.brightSlid.setEnabled (True)
            self.contrastSlid.setEnabled (True)
            self.saveStdyBtn.setEnabled (False)
            self.slideShwBtn.setEnabled (True)
            self.hotkeyLbl.setEnabled (True)
            
            self.setPhoto(self.dcmIPFileName, self.dcmOPFileName)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Message")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("No User Set Created. Firstly create a User with its Dicome Images")
            x = msg.exec_()

    def PrevImage(self):
        self.saveStdyBtn.setEnabled (False)
        self.ffcView.setText ("FFC")
        
        self.loadedImgID_temp = self.loadedImgID - 1
        
        if self.loadedImgID_temp < 0:
            self.loadedImgID_temp = self.imageCount - 1

        self.loadedImgID = self.loadedImgID_temp
        print (self.loadedImgID)

        self.dcmIPFileName = self.currentUserIPPath + str (self.currentUserIPFileLst [self.loadedImgID])
        self.dcmOPFileName = self.currentUserOPPath + str (self.currentUserOPFileLst [self.loadedImgID])

        self.setPhoto(self.dcmIPFileName, self.dcmOPFileName)

    def NextImage(self):
        self.saveStdyBtn.setEnabled (False)
        self.ffcView.setText ("FFC")
        
        self.loadedImgID_temp = self.loadedImgID + 1

        if self.loadedImgID_temp > (self.imageCount - 1):
            self.loadedImgID_temp = 0

        self.loadedImgID = self.loadedImgID_temp
        print (self.loadedImgID)

        self.dcmIPFileName = self.currentUserIPPath + str (self.currentUserIPFileLst [self.loadedImgID])
        self.dcmOPFileName = self.currentUserOPPath + str (self.currentUserOPFileLst [self.loadedImgID])

        self.setPhoto(self.dcmIPFileName, self.dcmOPFileName)

    def meanFFCGenerator(self, tempRoi, index):
        today = date.today ()
        today = today.strftime ("%d/%m/%Y")

        url = self.currentUserroiJsonFile
        jsonFile = open(url, "r")

        global ROICollection
        try:    
            ROICollection = json.load(jsonFile)
        except:
            ROICollection = {}

        tempRoiMean = 0 
        index += 1
        print ("FFC Funtion index: ", index)

        for i in range (index):
            try:
                tempRoiMean += tempRoi [i]["roiMean"] 
            except KeyError:
                print ("error")
                
        if(index != 0):
            tempRoiMean = tempRoiMean / index
            tempRoiMean = np.round(tempRoiMean,2)

        ROICollection[today] = {
            "ffcMean": tempRoiMean
        }

        print(ROICollection,"Line 198")
        self.FFCMnVal.setText (str (tempRoiMean))
        
    def saveStudy (self):
        self.saveStdyBtn.setEnabled (False)
        self.ffcView.setText ("FFC")

        url = self.currentUserroiJsonFile
        print (url, ROICollection)
        with open (url, 'w') as jsonFile:
            json.dump (ROICollection, jsonFile)

        self.mffcTbl.clear ()
        self.displayOnTable ()

    def roi_selection(self):
        global roiIndex 
        
        roiIndex += 1
        print ("Index: ", roiIndex)

        roiIPdcmFile = self.dcmIPFileName
        roiOPdcmFile = self.dcmOPFileName

        iproiDCM = pydicom.dcmread (roiIPdcmFile)
        oproiDCM = pydicom.dcmread (roiOPdcmFile)

        ipAryroi = iproiDCM.pixel_array
        print(ipAryroi.shape)
        scalipAry = cv2.convertScaleAbs(ipAryroi)

        opAryroi = oproiDCM.pixel_array
        scalopAry = cv2.convertScaleAbs(opAryroi)
        
        r = cv2.selectROI (scalipAry)
        self.ROIposVal.setText (str (r))

        dcmCropIP = ipAryroi [int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        dcmCropOP = opAryroi [int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

        print (len (dcmCropIP), len (dcmCropOP))
        self.saveStdyBtn.setEnabled (True)
        diff = dcmCropIP - dcmCropOP
        diff = np.array(diff, dtype=np.int16)
        dcmCropIP = np.array(dcmCropIP, dtype=np.int16)
        diff = np.absolute(np.array(diff))
        dcmCropIP = np.absolute(np.array(dcmCropIP))
        diff=np.round(diff,2)
        
        
        print (len (diff))
        strROI = ""
        tempROI = ""
        for x in dcmCropIP:
            strROI = strROI + str (x) + "\n"
        tempROI = strROI
        print ("IN roi ok")
        f = open("roiIN.txt", "w")
        f.write(tempROI)
        f.close()

        strROI = ""
        tempROI = ""
        for x in dcmCropOP:
            strROI = strROI + str (x) + "\n"
        tempROI = strROI
        print ("OUT roi ok")
        f = open("roiOUT.txt", "w")
        f.write(tempROI)
        f.close()

        strROI = ""
        tempROI = ""
        for x in diff:
            strROI = strROI + str (x) + "\n"
        tempROI = strROI
        print ("dif roi ok")
        f = open("roiDIF.txt", "w")
        f.write(tempROI)
        f.close()

        try:
            ffc = ((diff) / (2 * dcmCropIP))*100
            ffc = np.round(ffc,2)
            ffcMean = np.mean(ffc)
            ffcMean = np.round(ffcMean,2)
        except KeyError:
            print ("error in computation")

        dicomRoiCollection[roiIndex] = {
            "roiMatrix": ffc,
            "roiMean":ffcMean 
        }

        #cv2.imshow ("FF", ffc)

        ffcArray = cv2.convertScaleAbs(ffc)
        ffcIMG = QImage(ffcArray, ffcArray.shape[1], ffcArray.shape[0], ffcArray.strides[0], QImage.Format_Indexed8).rgbSwapped()

        self.ffcView.setPixmap (QtGui.QPixmap.fromImage (ffcIMG))
        self.ffcView.setScaledContents (True)
        
        print ("")
        
        if(roiIndex >= 2 ):
            self.meanFFCGenerator(dicomRoiCollection, roiIndex)
        print("Current ROI fatfraction Mean: ", ffcMean)
        self.CrntFFCVal.setText (str (ffcMean))

    def zoomIP(self):
        self.dcmIPFileName = self.currentUserIPPath + str (self.currentUserIPFileLst [self.loadedImgID])
        
        ip = pydicom.dcmread (self.dcmIPFileName).pixel_array
        plt.imshow(ip, cmap=plt.cm.bone)
        plt.show()

    def zoomOP(self):
        self.dcmOPFileName = self.currentUserOPPath + str (self.currentUserOPFileLst [self.loadedImgID])

        op = pydicom.dcmread (self.dcmOPFileName).pixel_array
        plt.imshow(op, cmap=plt.cm.bone)
        plt.show()

    def clockwise (self):
        print ("c Rotate Image Button Clicked")
        self.flippedIPDCM = cv2.rotate (self.flippedIPDCM, cv2.ROTATE_90_CLOCKWISE)
        RotatescalipAry = cv2.convertScaleAbs(self.flippedIPDCM)

        self.flippedOPDCM = cv2.rotate (self.flippedOPDCM, cv2.ROTATE_90_CLOCKWISE)
        RotatescalopAry = cv2.convertScaleAbs(self.flippedOPDCM)

        Rotate_ip_Image = QImage(RotatescalipAry, RotatescalipAry.shape[1], RotatescalipAry.shape[0], RotatescalipAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        Rotate_op_Image = QImage(RotatescalopAry, RotatescalopAry.shape[1], RotatescalopAry.shape[0], RotatescalopAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (Rotate_ip_Image))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (Rotate_op_Image))
        self.opView.setScaledContents (True)

    def counterclockwise (self):
        print ("cc Rotate Image Button Clicked")
        self.flippedIPDCM = cv2.rotate (self.flippedIPDCM, cv2.ROTATE_90_COUNTERCLOCKWISE)
        RotatescalipAry = cv2.convertScaleAbs(self.flippedIPDCM)

        self.flippedOPDCM = cv2.rotate (self.flippedOPDCM, cv2.ROTATE_90_COUNTERCLOCKWISE)
        RotatescalopAry = cv2.convertScaleAbs(self.flippedOPDCM)

        Rotate_ip_Image = QImage(RotatescalipAry, RotatescalipAry.shape[1], RotatescalipAry.shape[0], RotatescalipAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        Rotate_op_Image = QImage(RotatescalopAry, RotatescalopAry.shape[1], RotatescalopAry.shape[0], RotatescalopAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (Rotate_ip_Image))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (Rotate_op_Image))
        self.opView.setScaledContents (True)

    def verticalflip (self):
        print ("V.Flip Image Button Clicked")
        self.flippedIPDCM = cv2.flip (self.flippedIPDCM, 0)
        FlipscalipAry = cv2.convertScaleAbs(self.flippedIPDCM)

        self.flippedOPDCM = cv2.flip (self.flippedOPDCM, 0)
        FlipscalopAry = cv2.convertScaleAbs(self.flippedOPDCM)

        Flip_ip_Image = QImage(FlipscalipAry, FlipscalipAry.shape[1], FlipscalipAry.shape[0], FlipscalipAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        Flip_op_Image = QImage(FlipscalopAry, FlipscalopAry.shape[1], FlipscalopAry.shape[0], FlipscalopAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (Flip_ip_Image))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (Flip_op_Image))
        self.opView.setScaledContents (True)

    def horizontalflip (self):
        print ("H.Flip Image Button Clicked")
        self.flippedIPDCM = cv2.flip (self.flippedIPDCM, 1)
        FlipscalipAry = cv2.convertScaleAbs(self.flippedIPDCM)

        self.flippedOPDCM = cv2.flip (self.flippedOPDCM, 1)
        FlipscalopAry = cv2.convertScaleAbs(self.flippedOPDCM)

        Flip_ip_Image = QImage(FlipscalipAry, FlipscalipAry.shape[1], FlipscalipAry.shape[0], FlipscalipAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        Flip_op_Image = QImage(FlipscalopAry, FlipscalopAry.shape[1], FlipscalopAry.shape[0], FlipscalopAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (Flip_ip_Image))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (Flip_op_Image))
        self.opView.setScaledContents (True)

    def brightness_value (self,value):
        self.brightness_value_now = value * 2
        self.update ()
		
    def blur_value (self, value):
        self.blur_value_now = value * 2
        self.update ()
		
    def update (self):
        brightness = int((self.brightness_value_now - 0) * (255 - (-255)) / (510 - 0) + (-255))
        contrast = int((self.blur_value_now - 0) * (127 - (-127)) / (254 - 0) + (-127))

        pydicom.dcmread (self.dcmIPFileName).pixel_array
        pydicom.dcmread (self.dcmOPFileName).pixel_array

        ip_ = cv2.convertScaleAbs(pydicom.dcmread (self.dcmIPFileName).pixel_array)
        op_ = cv2.convertScaleAbs(pydicom.dcmread (self.dcmOPFileName).pixel_array)

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max = 255
            else:
                shadow = 0
                max = 255 + brightness
            al_pha = (max - shadow) / 255
            ga_mma = shadow

            cal_ip = cv2.addWeighted(ip_, al_pha, ip_, 0, ga_mma)
            cal_op = cv2.addWeighted(op_, al_pha, op_, 0, ga_mma)
        else:
            cal_ip = ip_
            cal_op = op_

        if contrast != 0:
            Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            Gamma = 127 * (1 - Alpha)

            cal_ip = cv2.addWeighted(cal_ip, Alpha, cal_ip, 0, Gamma)
            cal_op = cv2.addWeighted(cal_op, Alpha, cal_op, 0, Gamma)

        ip_Image = QImage(cal_ip, cal_ip.shape[1], cal_ip.shape[0], cal_ip.strides[0], QImage.Format_Indexed8).rgbSwapped()
        op_Image = QImage(cal_op, cal_op.shape[1], cal_op.shape[0], cal_op.strides[0], QImage.Format_Indexed8).rgbSwapped()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (ip_Image))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (op_Image))
        self.opView.setScaledContents (True)
        
    def setPhoto (self, dcmIPF, dcmOPF):
        ipDCM = pydicom.dcmread (dcmIPF)
        opDCM = pydicom.dcmread (dcmOPF)

        ipAry = ipDCM.pixel_array
        scalipAry = cv2.convertScaleAbs(ipAry)
        self.flippedIPDCM = scalipAry

        opAry = opDCM.pixel_array
        scalopAry = cv2.convertScaleAbs(opAry)
        self.flippedOPDCM = scalipAry

        ipoutImage = QImage(scalipAry, scalipAry.shape[1], scalipAry.shape[0], scalipAry.strides[0], QImage.Format_Indexed8).rgbSwapped()
        opoutImage = QImage(scalopAry, scalopAry.shape[1], scalopAry.shape[0], scalopAry.strides[0], QImage.Format_Indexed8).rgbSwapped()

        self.dcmFilesize = QtGui.QPixmap.fromImage (ipoutImage).size()
        
        self.ipView.setPixmap (QtGui.QPixmap.fromImage (ipoutImage))
        self.ipView.setScaledContents (True)
        self.opView.setPixmap (QtGui.QPixmap.fromImage (opoutImage))
        self.opView.setScaledContents (True)

    def displayDate (self, displayVal): 
        horHeaders = []
##        print (displayVal)
        for n, key in enumerate (sorted (displayVal.keys ())):
            horHeaders.append (key)
            for m, item in enumerate (displayVal [key]):
                self.mffcTbl.setItem (m, n, QTableWidgetItem (item))
##                print (item)
        self.mffcTbl.setHorizontalHeaderLabels (horHeaders)

    def displayOnTable (self):
        stylesheet = "color:rgb(0,0,0);}"
        QTableWidget.setStyleSheet(self.mffcTbl,stylesheet)
        jsonPath = self.currentUserroiJsonFile
        jsonFile = open(jsonPath, "r")
        jsonData = json.load(jsonFile)
        print (type (jsonData), len (jsonData), jsonData)

        if len (jsonData) > 0:
            self.headderNames = ["Date", "FFC Mean"]
            cCount = len (self.headderNames)

            self.dateDisplayLst = list (jsonData.keys())
            rCount = len (self.dateDisplayLst)
            jsonValuesLst = list (jsonData.values())

            self.mffcTbl.setRowCount (rCount)
            self.mffcTbl.setColumnCount (cCount)
            
            for r, dateVal in enumerate(self.dateDisplayLst):
                if r == 0:
                    self.mffcTbl.setItem (r, r, QTableWidgetItem (dateVal))
                    self.mffcTbl.setItem (r, r + 1, QTableWidgetItem (str (jsonData [self.dateDisplayLst [r]]['ffcMean'])))
                elif r == 1:
                    self.mffcTbl.setItem (r, r - 1, QTableWidgetItem (dateVal))
                    self.mffcTbl.setItem (r, r, QTableWidgetItem (str (jsonData [self.dateDisplayLst [r]]['ffcMean'])))
            print ("")
            self.mffcTbl.setHorizontalHeaderLabels (self.headderNames)

    def slideshow (self):
        print ("|| Hot Keys ||")
        print ("1.  's' to pause the slideshow")
        print ("2.  'q' to exit the slideshow")
        
        image_id = 0        
        while image_id < self.imageCount:
            self.dcmIPFileName = self.currentUserIPPath + str (self.currentUserIPFileLst [image_id])
            self.dcmOPFileName = self.currentUserOPPath + str (self.currentUserOPFileLst [image_id])
            dsi = cv2.convertScaleAbs (pydicom.dcmread (self.dcmIPFileName).pixel_array)
            dso = cv2.convertScaleAbs (pydicom.dcmread (self.dcmOPFileName).pixel_array)

            im_h = cv2.hconcat([dsi, dso])

            key, pause_key = None, None
            cv2.imshow('Slideshow', im_h)
            key = cv2.waitKey(1000)
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                pause_key = cv2.waitKey()
                if pause_key == ord('q'):
                    break

            image_id += 1
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    window = dicomeViewer()
    window.setWindowTitle('Dicom Viewer')
    window.show()
    sys.exit(app.exec_())
