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
        self.Hz = Hz
        self.Vz = Vz
        self.SDist = SDist
        self.RefHt = RefHt
        self.flags = flags
        self.date = date
        self.appType = appType

        self.tgtId = ""
        self.round = ""
    
    # 从Leica IDX文件中的 TgtID中，判断目标、测回信息
    def parseTgtId(self):
        self.tgtId = self.rawTgtId[-1]
        self.round = self.rawTgtId[0]   

    def parseRLFace(self):
        if self.flags == "00000000":
            self.indexHalfRound = "L"
        if self.flags == "00000001":
            self.indexHalfRound = "R"

        # print()

class Slope:
    def __init__(self,slopeItemList = None) -> None:
        self.slopeItemList = slopeItemList

    def parserSlopeBlock(self,rawSlopeBlock):
        self.slopeItemList = []
        for info in rawSlopeBlock:        
            infoList = info.split(",")

            appType = infoList[9].strip()
            # 仅解析测量数据，不对设站数据处理
            if appType == "107" :
                slopeItem = SlopeItem()

                #  Leica IDX 中现有的字段
                slopeItem.rawTgtId = infoList[1].strip().replace('"',"")        
                slopeItem.Hz = infoList[3].strip()
                slopeItem.Vz = infoList[4].strip()
                slopeItem.SDist = infoList[5].strip()
                slopeItem.RefHt = infoList[6].strip()
                slopeItem.date = infoList[7].strip()
                slopeItem.appType = infoList[9].strip()
                # 半测回标记：0：左半测回；1：右半测回
                slopeItem.flags = infoList[10].strip().replace(';',"")

                # 获取真实的tgtId,round
                slopeItem.parseTgtId() 
                slopeItem.parseRLFace()
                
                self.slopeItemList.append(slopeItem)

        # return slopeItemList

class StationBlock:
    def __init__(self,setUp = None, slope = None) -> None:
        self.setUp = setUp
        self.slope = slope

    # def parserStationBlock(self,rawSetupBlock):
    #     # setUpBlock = stationBlock["setUp"]
    #     # slopBlock = stationBlock["slop"]

    #     setUp = Setup()
    #     setUp.parserSetupBlock(rawSetupBlock)

    #     slop = Slope()
    #     slop.parserSlopeBlock(rawSetupBlock)

    #     stationBlock = StationBlock(setUp,slop)

    #     return stationBlock

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
        # allRawStationBlock = [] 
        
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
                    slopBlock = []
                    while line:
                        line = fo.readline() 
                        slopBlock.append(line)                   
                        if line.find("END SLOPE") != -1:
                            slopBlock.pop()                      
                            break
                    stationBlock["slop"] = slopBlock

                    self.allRawStationBlock.append(stationBlock)

                line = fo.readline()

        # return allRawStationBlock

    # 起始处
    def parserAllStatioBlock(self):
        self.extractAllRawStationBlock(fileDir)

        for rawStationBlock in self.allRawStationBlock:
            stationBlock = self.parserStationBlock(rawStationBlock)

            self.allStationBlock.append(stationBlock)
            print()
 
    # def parserSetupBlock(self,rawSetupBlock):
    #     setup = Setup()
    #     for info in rawSetupBlock:        
    #         if info.find("STN_ID") != -1:
    #             #print(info)
    #             setup.stnId = info.split()[1].strip().replace('"',"")

    #         if info.find("INST_HT") != -1:
    #             setup.instHt = info.split()[1].strip().replace(";","")
    #             # print(stn_id)
    #     return setup   

    # def parserSlopeBlock(self,rawSlopeBlock):
    #     slopeItemList = []
    #     for info in rawSlopeBlock:        
    #         infoList = info.split(",")

    #         appType = infoList[9].strip()
    #         # 仅解析测量数据，不对设站数据处理
    #         if appType == "107" :
    #             slopeItem = SlopeItem()

    #             #  Leica IDX 中现有的字段
    #             slopeItem.rawTgtId = infoList[1].strip().replace('"',"")        
    #             slopeItem.Hz = infoList[3].strip()
    #             slopeItem.Vz = infoList[4].strip()
    #             slopeItem.SDist = infoList[5].strip()
    #             slopeItem.RefHt = infoList[6].strip()
    #             slopeItem.date = infoList[7].strip()
    #             slopeItem.appType = infoList[9].strip()
    #             # 半测回标记：0：左半测回；1：右半测回
    #             slopeItem.flags = infoList[10].strip().replace(';',"")

    #             # 获取真实的tgtId,round
    #             slopeItem.parseTgtId() 
    #             slopeItem.parseRLFace()
                
    #             slopeItemList.append(slopeItem)

    #     return slopeItemList

    def parserStationBlock(self,stationBlock):
        setUpBlock = stationBlock["setUp"]
        slopBlock = stationBlock["slop"]

        setUp = Setup()
        setUp.parserSetupBlock(setUpBlock)

        slop = Slope()
        slop.parserSlopeBlock(slopBlock)

        stationBlock = StationBlock(setUp,slop)

        return stationBlock

    # 将Leica IDX 的 StationBlock 类，转换到以 目标点为组织的结构：
    # 
    # 测站 - 目标点（多个） - 测回（多个） - 半测回（盘左，盘右）
    #
    def stationBlock2stationObsByTarget(self,stationBlock):
        stationObs = rm.StationObs()

        stationObs.indexStation = stationBlock.setUp.stnId
        stationObs.stationHt = float(stationBlock.setUp.instHt)  
        
        # 提取所有的 targetId
        duplicatesTargetIndexList = []
        for splotItem in stationBlock.slope.slopeItemList:
            duplicatesTargetIndexList.append(splotItem.tgtId)        
        targetIndexList = self.removeDuplicatesList(duplicatesTargetIndexList) 

        for targetIndex in targetIndexList:
            targetObs = rm.TargetObs() 
            targetObs.indexTarget = targetIndex
            stationObs.targetObsList = [copy.deepcopy(element) for element in stationObs.targetObsList]
            stationObs.targetObsList.append(targetObs)                
        
        # 提取所有的 roundIndex
        for tgtObs in stationObs.targetObsList:
            duplicatesRoundIndexList = []
            for sloptItem in stationBlock.slope.slopeItemList:
                if tgtObs.indexTarget.find(sloptItem.tgtId) != -1:
                    duplicatesRoundIndexList.append(sloptItem.round)
            roundIndexList =self.removeDuplicatesList(duplicatesRoundIndexList)

            for roundIndex in roundIndexList:
                roundObs = rm.RoundObs()
                roundObs.indexRound = roundIndex
                tgtObs.roundObsList = [copy.deepcopy(element) for element in tgtObs.roundObsList]
                tgtObs.roundObsList.append(roundObs)
                # print()

        # 提取半测回数据
        for slopeItem in stationBlock.slope.slopeItemList:
            halfRoundObs = rm.halfRoundObs()
            halfRoundObs.index_halfRound = slopeItem.indexHalfRound
            halfRoundObs.Hz = float(slopeItem.Hz)    
            halfRoundObs.SDist = float(slopeItem.SDist)
            halfRoundObs.refHt = float(slopeItem.RefHt)

            test = float(slopeItem.Vz)
            t2 = halfRoundObs.azimuth2Vertical(test)
            # halfRoundObs.Vz = halfRoundObs.azimuth2Vertical(float(slopeItem.Vz))


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
   
    def getAllstationObsByTarget(self):        
        for stationBlock in self.allStationBlock:            
            stationObsByTarget = self.stationBlock2stationObsByTarget(stationBlock)
            self.allStationObsByTarget.append(stationObsByTarget)
    
    # 不包含重复元素的新列表，同时保持原始列表的顺序
    def removeDuplicatesList(self,lst):
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]

###  test......    ..................
fileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\20240407_edit_0408.IDX"
# fileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\20240407_edit.IDX"
# fileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\240403.1.IDX"
# fileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\20240407.IDX"



# allStationBlcokList = extractAllStationBlock(fileDir)
# setUpBlock = allStationBlcokList[0]["setUp"]
# slopBlock = allStationBlcokList[0]["slop"]
# parserSetupBlock(setUpBlock)
# parserSlopeBlock(slopBlock)
# parserStationBlock(allStationBlcokList[0])

leicaIDX = LeicaIDX(fileDir)
allStationBlock = leicaIDX.parserAllStatioBlock()
leicaIDX.getAllstationObsByTarget()

roundMeasureFile = rm.RoundMeasureFile()
roundMeasureFile.generateRoundMeasureFile(leicaIDX.allStationObsByTarget,"roundMeasureData.txt")