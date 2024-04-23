## Leica IDX 文件
#########################################
## 测量文件 --测站 1 -- SETUP
## --------------------SLOPE -- ITEM 1
## ---------------------------- ITEM 2
##           测站 2 -- SETUP
## --------------------SLOPE -- ITEM 1
## ---------------------------- ITEM 2
#########################################
import os
import sys
import copy

import round_measure as rm
import util

class Setup:
    def __init__(self,stnId = "",instHt = 0) -> None:
        self.stnId = stnId
        self.instHt = instHt

    def parserSetupBlock(self,rawSetupBlock):
        # setup = Setup()
        for info in rawSetupBlock:        
            if info.find("STN_ID") != -1:
                #print(info)
                self.stnId = info.split()[1].strip().replace('"',"")

            if info.find("INST_HT") != -1:
                self.instHt = info.split()[1].strip().replace(";","")
                # print(stn_id)
        # return setup   

class SlopeItem:
    def __init__(self,rawTgtId = "", Hz = 0.0, Vz = 0.0, SDist = 0.0, RefHt = 0.0, flags = "",date = "",appType = "") -> None:
        self.rawTgtId = rawTgtId
        self.Hz = Hz # 默认单位为弧度
        self.Vz = Vz # 默认单位为弧度
        self.SDist = SDist
        self.RefHt = RefHt
        self.flags = flags
        self.date = date
        self.appType = appType

        self.tgtId = ""
        self.round = ""
    
    #  Leica IDX 中现有的字段
    def parseSlopeItem(self,slopeLine):
        infoList = slopeLine.split(",")
        appType = infoList[9].strip()
        # 仅解析测量数据，不对设站数据处理
        if appType == "107" :            
            self.rawTgtId = infoList[1].strip().replace('"',"")  

            Hz = util.Angle()
            Hz.ddmmssString2radians(infoList[3].strip())
            self.Hz = Hz

            Vz = util.Angle()
            Vz.ddmmssString2radians(infoList[4].strip())
            self.Vz = Vz

            self.SDist = infoList[5].strip()
            self.RefHt = infoList[6].strip()
            self.date = infoList[7].strip()
            self.appType = infoList[9].strip()
            # 半测回标记：0：左半测回；1：右半测回
            self.flags = infoList[10].strip().replace(';',"")

            # 获取真实的tgtId,round
            self.parseTgtId() 
            self.parseRLFace()

            # 将角度转化为： 秒
            # self.angle2ss()
            print()

    # 从Leica IDX文件中的 TgtID中，判断目标、测回信息
    def parseTgtId(self):
        self.tgtId = self.rawTgtId[-1]
        self.round = self.rawTgtId[0]   

    def parseRLFace(self):
        if self.flags == "00000000":
            self.indexHalfRound = "L"
        if self.flags == "00000001":
            self.indexHalfRound = "R"

    # def angle2radians(self):
    #     self.Hz = util.ddmmssString2radians(self.Hz)
    #     self.Vz = util.ddmmssString2radians(self.Vz)

    # def angle2ss(self):
    #     self.Hz = util.ddmmssString2ss(self.Hz)
    #     self.Vz = util.ddmmssString2ss(self.Vz)        

class Slope:
    def __init__(self) -> None:
        self.slopeItemList = list()

    def parserSlopeBlock(self,rawSlopeBlock): 
        for splopeLine in rawSlopeBlock:
            slopeItem = SlopeItem()
            slopeItem.parseSlopeItem(splopeLine)
            if slopeItem.appType == "107":                
                self.slopeItemList.append(slopeItem)           
            print()    

class StationBlock:
    def __init__(self,setUp = None, slope = None) -> None:        
        self.setUp = setUp
        self.slope = slope

    def parserStationBlock(self,rawStationBlock):
        setUp = Setup()
        setUp.parserSetupBlock(rawStationBlock["setUp"])
        self.setUp = setUp

        slope = Slope()
        slope.parserSlopeBlock(rawStationBlock["slope"])
        self.slope = slope
        print()
    
    # 将Leica IDX 的 StationBlock 类，转换到以 目标点为组织的结构：
    # 
    # 测站 - 目标点（多个） - 测回（多个） - 半测回（盘左，盘右）
    #
    def stationBlock2stationObsByTarget(self):
        stationObs = rm.StationObs()

        stationObs.indexStation = self.setUp.stnId
        stationObs.stationHt = float(self.setUp.instHt)  
        
        # 提取所有的 targetId
        duplicatesTargetIndexList = []
        for splotItem in self.slope.slopeItemList:
            duplicatesTargetIndexList.append(splotItem.tgtId)        
        targetIndexList = util.removeDuplicatesList(duplicatesTargetIndexList) 

        for targetIndex in targetIndexList:
            targetObs = rm.TargetObs() 
            targetObs.indexTarget = targetIndex
            stationObs.targetObsList = [copy.deepcopy(element) for element in stationObs.targetObsList]
            stationObs.targetObsList.append(targetObs)                
        
        # 提取所有的 roundIndex
        for tgtObs in stationObs.targetObsList:
            duplicatesRoundIndexList = []
            for sloptItem in self.slope.slopeItemList:
                if tgtObs.indexTarget.find(sloptItem.tgtId) != -1:
                    duplicatesRoundIndexList.append(sloptItem.round)
            roundIndexList =util.removeDuplicatesList(duplicatesRoundIndexList)

            for roundIndex in roundIndexList:
                roundObs = rm.RoundObs()
                roundObs.indexRound = roundIndex
                tgtObs.roundObsList = [copy.deepcopy(element) for element in tgtObs.roundObsList]
                tgtObs.roundObsList.append(roundObs)
                # print()

        # 提取半测回数据
        for slopeItem in self.slope.slopeItemList:
            halfRoundObs = rm.halfRoundObs()
            halfRoundObs.index_halfRound = slopeItem.indexHalfRound
            halfRoundObs.Hz = slopeItem.Hz
            halfRoundObs.Vz = slopeItem.Vz 
            halfRoundObs.SDist = float(slopeItem.SDist)
            halfRoundObs.refHt = float(slopeItem.RefHt)

            halfRoundObs.rightFace2LeftFace()
            halfRoundObs.azimuth2Vertical()

            # test = float(slopeItem.Vz)
            # t2 = halfRoundObs.azimuth2Vertical(test)

            for tgtObs in stationObs.targetObsList:
                if tgtObs.indexTarget.find(slopeItem.tgtId) != -1:
                    for roundObs in tgtObs.roundObsList:
                        # roundObs.indexRound = slopeItem.round
                        if roundObs.indexRound.find(slopeItem.round) != -1:
                            roundObs.halfRoundObsList = [copy.deepcopy(element) for element in roundObs.halfRoundObsList]
                            roundObs.halfRoundObsList.append(halfRoundObs)
        
        stationObs.stationCompute()
        stationObs.stringFormat_2()
        stationObs.stringFormat_3()
        
        return stationObs 
        # print("test................") 

class LeicaIDX:
    def __init__(self,fileDir) -> None:
        # 原始的数据
        self.allRawStationBlock = []

        # 结构化后的原始数据
        self.allStationBlock = []

        # 标准化后的测量数据：测站 - 目标点（多个）- 测  回（多个) - 半测回（盘左，盘右）
        self.allStationObsByTarget = []

        # 标准化后的测量数据：测站 - 测  回（多个) - 目标点（多个) - 半测回（盘左，盘右）
        # 后续增加
        self.allStationObsByRound = []
    
    #  仅提取所有的测站数据到数组中，不做解析。
    def extractAllRawStationBlock(self,fileDir):        
        with open(fileDir, 'r', encoding='utf-8') as fo:
            line = fo.readline()
            while line:
                
                # extract context from "SETUP - ENDSETUP"
                if line.find("SETUP") != -1:
                    stationBlock = {}

                    setUpBlock = []
                    while line:
                        line = fo.readline()  
                        setUpBlock.append(line)                  
                        if line.find("END SETUP") != -1:
                            setUpBlock.pop()                      
                            break
                    stationBlock["setUp"] = setUpBlock
                
                if line.find("SLOPE") != -1:
                    slopeBlock = []
                    while line:
                        line = fo.readline() 
                        slopeBlock.append(line)                   
                        if line.find("END SLOPE") != -1:
                            slopeBlock.pop()                      
                            break
                    stationBlock["slope"] = slopeBlock

                    self.allRawStationBlock.append(stationBlock)

                line = fo.readline()  

    # 起始处
    def parserAllStatioBlock(self):
        for rawStationBlock in self.allRawStationBlock:
            stationBlock = StationBlock()
            stationBlock.parserStationBlock(rawStationBlock)

            self.allStationBlock.append(stationBlock)
            print()  
   
    def getAllstationObsByTarget(self):        
        for stationBlock in self.allStationBlock:            
            stationObsByTarget = stationBlock.stationBlock2stationObsByTarget()
            self.allStationObsByTarget.append(stationObsByTarget)

###  test......    ..................
fileDir = "data\\20240407_edit_0408.IDX"

# fileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\20240407_edit_0408.IDX"
# fileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\240403.1.IDX"

# allStationBlcokList = extractAllStationBlock(fileDir)
# setUpBlock = allStationBlcokList[0]["setUp"]
# slopBlock = allStationBlcokList[0]["slop"]
# parserSetupBlock(setUpBlock)
# parserSlopeBlock(slopBlock)
# parserStationBlock(allStationBlcokList[0])

leicaIDX = LeicaIDX(fileDir)
leicaIDX.extractAllRawStationBlock(fileDir)
allStationBlock = leicaIDX.parserAllStatioBlock()
leicaIDX.getAllstationObsByTarget()

roundMeasureFile = rm.RoundMeasureFile()
roundMeasureFile.generateRawMeasureFile(leicaIDX.allStationObsByTarget,"data\\00_rawData.txt")
roundMeasureFile.generateRawCheckFile(leicaIDX.allStationObsByTarget,"data\\01_rawCheckData.txt")
roundMeasureFile.generateRawCheckFileByRound(leicaIDX.allStationObsByTarget,"data\\01_rawCheckDataByRound.txt")
roundMeasureFile.generateClearedDataFile(leicaIDX.allStationObsByTarget,"data\\02_clearedData.txt")
roundMeasureFile.generateClearedAverageFile(leicaIDX.allStationObsByTarget,"data\\03_clearedAverageData.txt")