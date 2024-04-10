import math

import util

## 标准的全站仪边角网数据记录格式
#############################################################################
# 测量项目 - 测站1 - 目标点1 - 第1测回 - 盘左 : 棱镜高、水平方向、垂直方向、斜距、 
#                                      盘右
#                             第2测回 - 盘左 
#                                      盘右
#                   目标点2 - 第1测回 - 盘左  
#                                      盘右
#                             第2测回 - 盘左 
#                                      盘右
#            测站1 - 目标点2 - 第1测回 - 盘左 : 棱镜高、水平方向、垂直方向、斜距、 
#                                      盘右
#                             第2测回 - 盘左 
#                                      盘右
#                   目标点2 - 第1测回 - 盘左  
#                                      盘右
#                             第2测回 - 盘左 
#                                      盘右
################################################################################

# 半测回类：一次测量按键
#
# 竖直角范围: -90 ~ 90
class halfRoundObs:
    def __init__(self,index_halfRound = "L",refHt = 0.0, Hz = 0.0, Vz = 0.0, SDist = 0.0) -> None:
        self.index_halfRound = index_halfRound
        self.refHt = refHt 
        self.Hz = Hz
        self.Vz = Vz
        self.SDist = SDist  # 斜距

        self.HzR2L = 0.0

        self.test_factor  = 3600

    def halfRoundCompute(self):
        self.rightFace2LeftFace()
        self.azimuth2Vertical()

    
    # 盘右转为盘左后的值
    def rightFace2LeftFace(self):
        if self.index_halfRound == "R":            
            if self.Hz >=  (180 * self.test_factor):           
                self.HzR2L = self.Hz - (180 * self.test_factor)
            if self.Hz < 180:           
                self.HzR2L = self.Hz + (180 * self.test_factor) 
        
        if self.index_halfRound == "L": 
            self.HzR2L = self.Hz
    
    # 将 天顶距 转化为 竖直角
    #   盘左时： 90 - L (左天顶距：当初准轴水平时为 90度)
#   #   盘左时： R - 270
    def azimuth2Vertical(self):
        if self.index_halfRound == "L":
            self.VzVertical = (90 * self.test_factor) - self.Vz
            print()

        if self.index_halfRound == "R":
            self.VzVertical = self.Vz - (270 * self.test_factor)

# 一个测回类：仅是一个目标点的一个测回观测，但可以包含多次按键测量的数据。
class RoundObs:
    def __init__(self,indexRound = "",halfRoundObsList = []) -> None:
        self.indexRound = indexRound
        self.halfRoundObsList = halfRoundObsList
        
        self.difLRHz = 0.0
        self.difLRVz = 0.0
        self.difLRSDist = 0.0 

        self.averageLRHz = 0.0
        self.averageLRVz = 0.0
        self.averageLRSDist = 0.0

        self.difMutiRoundHz = 0.0
        self.difMutiRoundVz = 0.0
        self.difMutiRoundSDist = 0.0

    # 计算 ：
    #   1）左右盘互差，(盘左 - 盘右)
    #   2）一测回内均值
    #    
    def roundCompute(self):
        leftRoundObs = halfRoundObs()
        rightRoundObs = halfRoundObs()     
        for item in self.halfRoundObsList:
            if item.index_halfRound == "L":
                leftRoundObs = item
                leftRoundObs.halfRoundCompute()               
            if item.index_halfRound == "R":                
                rightRoundObs = item
                leftRoundObs.halfRoundCompute()

        self.difLRHz = leftRoundObs.Hz - rightRoundObs.HzR2L
        self.difLRVz = leftRoundObs.VzVertical - rightRoundObs.VzVertical
        self.difLRSDist = leftRoundObs.SDist - rightRoundObs.SDist

        self.averageLRHz = (leftRoundObs.Hz + rightRoundObs.HzR2L) / 2.0
        self.averageLRVz = (leftRoundObs.VzVertical + rightRoundObs.VzVertical) / 2.0
        self.averageLRSDist = (leftRoundObs.SDist + rightRoundObs.SDist) / 2.0

# 一个观测点类（包括多个测回）
class TargetObs:
    def __init__(self,indexTarget = "", roundObsList = []) -> None:
        self.indexTarget = indexTarget
        self.roundObsList = roundObsList

        self.averageMutiRoundHz = 0.0
        self.averageMutiRoundVz = 0.0
        self.averageMutiRoundSDist = 0.0

    # 计算一个观测点的多个测回的均值，及测回差： （测回 - 平均值）
    def multiRoundCompute(self):
        self.averageMutiRoundHz = sum(item.averageLRHz for item in self.roundObsList) / len(self.roundObsList)
        self.averageMutiRoundVz = sum(item.averageLRVz for item in self.roundObsList) / len(self.roundObsList)
        self.averageMutiRoundSDist = sum(item.averageLRSDist for item in self.roundObsList) / len(self.roundObsList)

        # 测回差
        for roundObs in self.roundObsList:
            roundObs.difMutiRoundHz = roundObs.averageLRHz - self.averageMutiRoundHz
            roundObs.difMutiRoundVz = roundObs.averageLRVz - self.averageMutiRoundVz
            roundObs.difMutiRoundSDist = roundObs.averageLRSDist - self.averageMutiRoundSDist        

# 一个站点的所有目标点
class StationObs:
    def __init__(self,indexStation = "", stationHt = 0.0,targetObsList = []) -> None:
        self.indexStation = indexStation
        self.stationHt = stationHt
        self.targetObsList = targetObsList

        self.deleteTag = "999999"

    def stationCompute(self):
        for targetObs in self.targetObsList:
            for roundObs in targetObs.roundObsList:
                for halfRoundObs in roundObs.halfRoundObsList:
                    halfRoundObs.halfRoundCompute()
                    print()
                roundObs.roundCompute()
            targetObs.multiRoundCompute()    

    # 测站数据质检检查：1）测回内超限检查，2）测回间超限检查
    #                 [seconds,seconds,meter]
    def stationObsCheck(self,toleranceRound = [20,20,0.001],toleranceMutiRound = [0,0,0]):        
        # 测回内检查: station  :  target  :  round
        resultInfoRoundCheck = "" 
        for targetObs in self.targetObsList:
            for roundObs in targetObs.roundObsList:
                if abs(roundObs.difLRHz) > toleranceRound[0] or \
                    abs(roundObs.difLRVz) > toleranceRound[1] or \
                    abs(roundObs.difLRSDist) > toleranceRound[2] or \
                    abs(roundObs.difMutiRoundHz) > toleranceRound[0] or \
                    abs(roundObs.difMutiRoundVz) > toleranceRound[1] or \
                    abs(roundObs.difMutiRoundSDist) > toleranceRound[2] :

                    resultInfoRoundCheck += (self.indexStation + "," + targetObs.indexTarget + "," + 
                                             roundObs.indexRound + ",," + str(roundObs.difLRHz) + "," + 
                                             str(roundObs.difLRVz) + "," + str(roundObs.difLRSDist) + ",," +
                                             str(roundObs.difMutiRoundHz) + "," + str(roundObs.difMutiRoundVz) + "," +
                                             str(roundObs.difMutiRoundSDist) + "\n") 

        # 测回间检查
        for targetObs in self.targetObsList:
            # To add...
            pass

        return  resultInfoRoundCheck         

    # 超限数据剔除
    def dataClear(self,toleranceRound = [20,20,0.001]):
        for targetObs in self.targetObsList:
            for roundObs in targetObs.roundObsList:
                # 剔除超限的水平角
                if abs(roundObs.difLRHz) > toleranceRound[0]:
                    for halfRoundObs in roundObs.halfRoundObsList:
                        # halfRoundObs.Hv = self.deleteTag
                        halfRoundObs.HzR2L = self.deleteTag
                
                # 剔除超限的竖直角
                if abs(roundObs.difLRVz) > toleranceRound[1]:
                    for halfRoundObs in roundObs.halfRoundObsList:
                        halfRoundObs.VzVertical = self.deleteTag
                        # halfRoundObs.HzR2L = self.deleteTag
                
                # 剔除超限的距离
                if abs(roundObs.difLRSDist) > toleranceRound[2]:
                    for halfRoundObs in roundObs.halfRoundObsList:
                        halfRoundObs.SDist = self.deleteTag
                        # halfRoundObs.HzR2L = self.deleteTag
                
                        pass                
       

    # 站点数据格式化输出：测站点,观测方向,测回数,半测回标志,水平方向,垂直方向,距离,棱镜高,测站高
    def stringFormat_2(self):
        allInfoOneStation = []

        for indexTgt,targetObs in enumerate(self.targetObsList):
            # 仅在第一个目标时，输出测站编号
            infoStation = ""
            if indexTgt == 0:
                infoStation = self.indexStation
            else:
                infoStation = ""

            for indexRound,roundObs in enumerate(targetObs.roundObsList):
                # 仅在第一个测量回，输出目标编号
                infoTarget = ""
                if indexRound == 0:
                    infoTarget = targetObs.indexTarget
                else:                    
                    infoTarget = ""

                for indexHalfRound,halfRoundObs in enumerate(roundObs.halfRoundObsList):
                    # 仅在第一个半测量回时，输出测回编号
                    infoRound = ""
                    if indexHalfRound == 0:
                        infoRound = roundObs.indexRound
                    else:                        
                        infoStation = ""
                        infoTarget = ""
                        infoRound = ""

                    info = infoStation + "," + infoTarget  + "," + infoRound + "," + \
                        halfRoundObs.index_halfRound + "," +  \
                        str(halfRoundObs.Hz) + "," + str(halfRoundObs.Vz) + "," + str(halfRoundObs.SDist) + "," +\
                        str(halfRoundObs.refHt) + "," + str(self.stationHt) + " \n"  
                                      
                    # print(info)
                    allInfoOneStation.append(info)

                    info = "" 

        return allInfoOneStation

    # 站点数据格式化输出：带外业限差计算输出
    def stringFormat_3(self):
        allInfoOneStation = []

        for indexTgt,targetObs in enumerate(self.targetObsList):
            # 仅在第一个目标时，输出测站编号            
            if indexTgt == 0:
                infoStation = self.indexStation
            else:
                infoStation = ""

            for indexRound,roundObs in enumerate(targetObs.roundObsList):
                # 仅在第一个测量回，输出目标编号                
                if indexRound == 0:
                    infoTarget = targetObs.indexTarget
                    infoAverageMutiRound = (str(targetObs.averageMutiRoundHz) + ","  + 
                                            str(targetObs.averageMutiRoundVz) + "," + str(targetObs.averageMutiRoundSDist))
                else:                    
                    infoTarget = ""
                    infoAverageMutiRound = ",,"

                for indexHalfRound,halfRoundObs in enumerate(roundObs.halfRoundObsList):
                    # 仅在第一个半测量回时，输出测回编号                   
                    if indexHalfRound == 0:
                        infoRound = roundObs.indexRound

                        infoRoundComputer = (str(roundObs.difLRHz) + "," + str(roundObs.difLRVz) + "," + str(roundObs.difLRSDist) + ",," + 
                                             str(roundObs.averageLRHz) + "," + str(roundObs.averageLRVz) + "," + str(roundObs.averageLRSDist)) 
                        # To add...
                        infoMutiRoundDif = (str(roundObs.averageLRHz - targetObs.averageMutiRoundHz) + "," + 
                                            str(roundObs.averageLRVz -targetObs.averageMutiRoundVz) + "," + 
                                            str(roundObs.averageLRSDist - targetObs.averageMutiRoundSDist))

                    else:                        
                        infoStation = ""
                        infoTarget = "" 
                        infoAverageMutiRound = ",,"                       

                        infoRound = ""   
                        infoRoundComputer = ",,,,,," 
                        infoMutiRoundDif = ",,"
                    
                    info = infoStation + "," + infoTarget  + "," + infoRound + "," + \
                        halfRoundObs.index_halfRound + "," +  \
                        str(halfRoundObs.Hz) + "," + str(halfRoundObs.Vz) + "," + str(halfRoundObs.SDist) + "," + \
                        str(halfRoundObs.refHt) + "," + str(self.stationHt) + ",," + \
                        str(halfRoundObs.HzR2L) + "," + str(halfRoundObs.Vz) + ",," + \
                        infoRoundComputer + ",," + \
                        infoAverageMutiRound + ",," + \
                        infoMutiRoundDif + ",," + "\n"  
                                      
                    # print(info)
                    allInfoOneStation.append(info)

                    info = "" 
        return allInfoOneStation    
   
# 一个标准的工程记录文件
class RoundMeasureFile:
    def __init__(self) -> None:
        pass    

    def generateRoundMeasureFile(self,stationObsList,outPutFileDir):
        with open(outPutFileDir, 'w', encoding='utf-8') as file:      
            # file.write("测站点,观测方向,测回数,半测回标志,水平方向,垂直方向,距离,棱镜高,测站高" + "\n")
            stringCapital = ("测站点,观测方向,测回数,半测回标志,水平方向,垂直方向,距离,棱镜高,测站高,," +
                             "转换到盘左的Hz,转换到盘左的Vz,," + 
                             "水平角2C差,垂直角指标差,距离差（测回内）,," + 
                             "水平方向平均值,垂直方向平均值,距离平均值（一测回）,," + 
                             "水平方向平均值,垂直方向平均值,距离平均值（多测回）,," + 
                             "水平角差,垂直角差,距离差（与多测回平均值的差）" + "\n")
                        
            file.write(stringCapital)

            for stationObs in stationObsList:
                infoList = stationObs.stringFormat_3()
                for info in infoList:
                    file.write(info)

            # 增加超限检查         
            resultInfoRoundCheck = (" \n out of range: " + "\n")
                                
            resultInfoRoundCheck += ("测站, 目标, 测回,," + 
                                     "水平角差, 垂直角差, 距离差（一测回）,," +
                                     "水平角差, 垂直角差, 距离差（与多测回平均值差）\n")
            # 输出表头
            file.write(resultInfoRoundCheck)
            
            # 输出超限项
            for stationObs in stationObsList:
                infoCheck = stationObs.stationObsCheck([0,0,0])
                file.write(infoCheck)
                pass
    
    # 删除了粗差的观测数据
    def generateClearedDataFile(self,stationObsList,clearedFileDir):
        with open(clearedFileDir, 'w', encoding='utf-8') as file:
            stringCapital = ("测站点,观测方向,测回数,半测回标志,方位角,竖直角,距离,测站高,棱镜高,平差站点序号, \n")
            file.write(stringCapital)
            
            for indexStation,stationObs in enumerate(stationObsList):
                codeStationPreAdjumtment = indexStation
                stationObs.dataClear()
                for targetObs in stationObs.targetObsList:
                    for roundObs in targetObs.roundObsList:                
                        for halfRoundObs in roundObs.halfRoundObsList:
                            infoData = (stationObs.indexStation + "," + 
                                targetObs.indexTarget + "," + 
                                roundObs.indexRound + "," + 
                                halfRoundObs.index_halfRound + "," + 
                                str(halfRoundObs.HzR2L) + "," +
                                str(halfRoundObs.VzVertical) + "," + 
                                str(halfRoundObs.SDist) + "," +
                                str(stationObs.stationHt) + "," +
                                str(halfRoundObs.refHt) + "," +
                                str(codeStationPreAdjumtment) + "\n")
                            file.write(infoData)







