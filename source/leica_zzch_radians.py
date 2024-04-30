import copy

import util
import round_measure as rm

class ZzchRadinas:
    def __init__(self) -> None:
        self.allStationInfoList = []
        self.allStationObsList = []       
     
    def extractAllRawStationBlock(self,fileDir):       
        with open(fileDir, 'r', encoding='utf-8') as fo:
            line = fo.readline()
            while line:
                stationInfoList = []
                stationInfoList.append(line)
                
                line = fo.readline()
                stationInfoList.append(line)              
                
                infoList = line.split(",")
                roundCount = int(infoList[0].strip())
                targetCount = int(infoList[1].strip())
                
                for lineInfo in range(roundCount * targetCount * 2):
                    line = fo.readline().strip()
                    stationInfoList.append(line)  
                
                self.allStationInfoList.append(stationInfoList)
                
                line = fo.readline() 
  
    def parseStationObs(self,stationInfoList): 
        # 提取一个测站信息
        stationObs = rm.StationObs()
        
        infoList = stationInfoList[0].split(",")        
        stationObs.indexStation = infoList[0].strip()
        stationObs.stationHt = float(infoList[1].strip())
        
        infoList = stationInfoList[1].split(",")     
        roundCount = int(infoList[0].strip())
        targetCount = int(infoList[1].strip())
                
        # 提取所有的 targetId
        duplicatesTargetIndexList = []      
        for line in stationInfoList[2:]:
            infoList = line.split(",")                        
            duplicatesTargetIndexList.append(infoList[1].strip()) 
        targetIndexList = util.removeDuplicatesList(duplicatesTargetIndexList)
            
        for targetIndex in targetIndexList:
            targetObs = rm.TargetObs() 
            targetObs.indexTarget = targetIndex
            stationObs.targetObsList = [copy.deepcopy(element) for element in stationObs.targetObsList]
            stationObs.targetObsList.append(targetObs) 
        
        # 提取所有的 roundIndex
        for targetObs in stationObs.targetObsList:
            for roundIndex in range(roundCount):
                roundObs = rm.RoundObs()
                roundObs.indexRound = str(roundIndex)
                targetObs.roundObsList = [copy.deepcopy(element) for element in targetObs.roundObsList]
                targetObs.roundObsList.append(roundObs)                          
        
        # 为每一行增加测回信息
        stationInfoListWithRoundInfo = []
        indexRound = 0
        for indexLine,line in enumerate(stationInfoList[2:]):             
            if  (targetCount * 2 * indexRound <= indexLine)  and \
                (indexLine < targetCount * 2 * indexRound + targetCount * 2):
                
                lineWithRoundInfo = (line + "," + str(indexRound)) 
                stationInfoListWithRoundInfo.append(lineWithRoundInfo)
                pass
            else:
                indexRound += 1 
                lineWithRoundInfo = (line + "," + str(indexRound)) 
                stationInfoListWithRoundInfo.append(lineWithRoundInfo) 
        
        # 提取半测回数据
        for line in stationInfoListWithRoundInfo:                            
            infoList = line.split(",")            
            targetIndex = infoList[1].strip()
            indexRound = infoList[-1].strip()
            
            halfRoundObs = rm.halfRoundObs()
            halfRoundObs.index_halfRound = self.parseRLFace(infoList[10].strip())
            halfRoundObs.Hz = util.Angle(float(infoList[3].strip()))
            halfRoundObs.Vz = util.Angle(float(infoList[4].strip()))
            halfRoundObs.SDist = float(infoList[5].strip())
            halfRoundObs.refHt = float(infoList[6].strip()) 
            
            halfRoundObs.rightFace2LeftFace()
            halfRoundObs.azimuth2Vertical()    
            
            for tgtObs in stationObs.targetObsList:
                if tgtObs.indexTarget == targetIndex:                                                            
                    for roundObs in tgtObs.roundObsList: 
                        if roundObs.indexRound == indexRound:
                            roundObs.halfRoundObsList = [copy.deepcopy(element) for element in roundObs.halfRoundObsList]
                            roundObs.halfRoundObsList.append(halfRoundObs) 
    
        stationObs.stationCompute()
        stationObs.stringFormat_2()
        stationObs.stringFormat_3()
        
        return stationObs                 
                   
    def getAllStationObsList(self) :
        for stationInfo in self.allStationInfoList:
            stationObs = self.parseStationObs(stationInfo)
            self.allStationObsList.append(stationObs)        
    
    def parseRLFace(self,tagString):
        if tagString == "1":
            return "L"
        if tagString == "2":
            return "R"                
                   
# test........
#
zzcch_radians_dir = "data\\sh20240429_01.txt" 
# zzcch_radians_dir = "data\\sh20240429_02.txt"

zzchRadinas = ZzchRadinas()
zzchRadinas.extractAllRawStationBlock(zzcch_radians_dir)
zzchRadinas.getAllStationObsList()

outPutPrefix = zzcch_radians_dir.split(".")[0]
roundMeasureFile = rm.RoundMeasureFile()
roundMeasureFile.generateRawMeasureFile(zzchRadinas.allStationObsList,str(outPutPrefix + "_00_rawData.txt"))
roundMeasureFile.generateRawCheckFile(zzchRadinas.allStationObsList,str(outPutPrefix + "_01_rawCheckData.txt"))
roundMeasureFile.generateRawCheckFileByRound(zzchRadinas.allStationObsList,str(outPutPrefix + "_01_rawCheckDataByRound.txt"))
roundMeasureFile.generateClearedDataFile(zzchRadinas.allStationObsList,str(outPutPrefix + "_02_clearedData.txt"))
roundMeasureFile.generateClearedAverageFile(zzchRadinas.allStationObsList,str(outPutPrefix + "_03_clearedAverageData.txt"))
print("test....")


                    
                