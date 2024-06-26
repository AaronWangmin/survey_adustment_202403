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
    def __init__(self,index_halfRound = "L",refHt = 0.0, 
                 Hz = util.Angle(), Vz = util.Angle(), SDist = 0.0,) -> None:                
        self.index_halfRound = index_halfRound
        self.refHt = refHt 
        self.Hz = Hz
        self.Vz = Vz
        self.SDist = SDist  # 斜距

        self.HzR2L = util.Angle()        
    
    def halfRoundCompute(self):
        self.rightFace2LeftFace()
        self.azimuth2Vertical()
    
    # 盘右转为盘左后的值
    def rightFace2LeftFace(self):
        degrees_180 = util.Angle(180, util.AngleType.degrees)
        degrees_180.degrees2radians()

        if self.index_halfRound == "R":            
            if self.Hz.value >=  degrees_180.value: 
                HzR2L = util.Angle(self.Hz.value - degrees_180.value)         
                self.HzR2L = HzR2L
            if self.Hz.value < degrees_180.value: 
                HzR2L = util.Angle(self.Hz.value + degrees_180.value)                
                self.HzR2L = HzR2L 
        
        if self.index_halfRound == "L": 
            self.HzR2L = self.Hz
    
    # 将 天顶距 转化为 竖直角
    #   盘左时： 90 - L (左天顶距：当初准轴水平时为 90度)
#   #   盘右时： R - 270
    def azimuth2Vertical(self):
        vertical = util.Angle()

        if self.index_halfRound == "L":
            degrees_90 = util.Angle(90,util.AngleType.degrees)
            degrees_90.degrees2radians()
            
            # 转换为竖直角
            # vertical.value = degrees_90.value - self.Vz.value           
            # self.vertical = vertical   
            
            # 天顶距
            vertical.value = self.Vz.value  
            self.vertical = vertical   
            print()

        if self.index_halfRound == "R":
            degrees_270 = util.Angle(270,util.AngleType.degrees)
            degrees_270.degrees2radians()
            
            # 转换为竖直角
            # vertical.value = self.Vz.value - degrees_270.value
            # self.vertical = vertical
            
            # 转换为盘左天顶距
            degrees_360 = util.Angle(360,util.AngleType.degrees)
            degrees_360.degrees2radians()
            vertical.value = degrees_360.value - self.Vz.value  
            self.vertical = vertical              
       
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
        
        # 测回内2C差
        difLRHz = util.Angle(leftRoundObs.Hz.value - rightRoundObs.HzR2L.value)
        self.difLRHz = difLRHz

        difLRVz = util.Angle(leftRoundObs.vertical.value - rightRoundObs.vertical.value)
        self.difLRVz = difLRVz

        self.difLRSDist = leftRoundObs.SDist - rightRoundObs.SDist
        
        # 测回内均值
        averageLRHz = util.Angle((leftRoundObs.Hz.value + rightRoundObs.HzR2L.value) / 2.0)
        self.averageLRHz = averageLRHz

        averageLRVz = util.Angle((leftRoundObs.vertical.value + rightRoundObs.vertical.value) / 2.0)
        self.averageLRVz = averageLRVz

        self.averageLRSDist = (leftRoundObs.SDist + rightRoundObs.SDist) / 2.0

        # 本测回与多测回均值的差
        self.difMutiRoundHz = util.Angle()
        self.difMutiRoundVz = util.Angle()
        self.difMutiRoundSDist = 0.0

# 一个观测点类（包括多个测回）
class TargetObs:
    def __init__(self,indexTarget = "", roundObsList = []) -> None:
        self.indexTarget = indexTarget
        self.roundObsList = roundObsList
        
        # TODO...
        # 目标点的高度应该从halfRound类中移到这里

        self.averageMutiRoundHz = util.Angle()
        self.averageMutiRoundVz = util.Angle()
        self.averageMutiRoundSDist = 0.0

    # 计算一个观测点的多个测回的均值，及测回差： （测回 - 平均值）
    def multiRoundCompute(self):
        self.averageMutiRoundHz.value = sum(item.averageLRHz.value for item in self.roundObsList) / len(self.roundObsList)
        self.averageMutiRoundVz.value = sum(item.averageLRVz.value for item in self.roundObsList) / len(self.roundObsList)
        
        self.averageMutiRoundSDist = sum(item.averageLRSDist for item in self.roundObsList) / len(self.roundObsList)

        # 测回差
        for roundObs in self.roundObsList:
            roundObs.difMutiRoundHz.value = roundObs.averageLRHz.value - self.averageMutiRoundHz.value
            roundObs.difMutiRoundVz.value = roundObs.averageLRVz.value - self.averageMutiRoundVz.value

            roundObs.difMutiRoundSDist = roundObs.averageLRSDist - self.averageMutiRoundSDist        

# 一个站点的所有目标点
class StationObs:
    def __init__(self,indexStation = "", stationHt = 0.0,targetObsList = []) -> None:
        self.indexStation = indexStation
        self.stationHt = stationHt
        self.targetObsList = targetObsList

        self.deleteTag = 999999        

        self.averageObsList = list()
        
        #  超限检查：角度单位 秒 ： 20
        self.toleranceRound = [util.Angle(2,util.AngleType.seconds).seconds2radians().value,
                               util.Angle(5,util.AngleType.seconds).seconds2radians().value,
                               0.0007]
        self.toleranceMutiRound = [util.Angle(20,util.AngleType.seconds).seconds2radians().value,
                                   util.Angle(20,util.AngleType.seconds).seconds2radians().value,
                                   0.00015]

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
    def stationObsCheck(self,):        
        # 测回内检查: station  :  target  :  round
        resultInfoRoundCheck = "" 
        for targetObs in self.targetObsList:
            for roundObs in targetObs.roundObsList:
                if abs(roundObs.difLRHz.value) > self.toleranceRound[0] or \
                    abs(roundObs.difLRVz.value) > self.toleranceRound[1] or \
                    abs(roundObs.difLRSDist) > self.toleranceRound[2] or \
                    abs(roundObs.difMutiRoundHz.value) > self.toleranceRound[0] or \
                    abs(roundObs.difMutiRoundVz.value) > self.toleranceRound[1] or \
                    abs(roundObs.difMutiRoundSDist) > self.toleranceRound[2] :

                    resultInfoRoundCheck += (self.indexStation + "," + targetObs.indexTarget + "," + 
                                             roundObs.indexRound + ",," + 
                                             roundObs.difLRHz.radians2dmsString() + "," + 
                                             roundObs.difLRVz.radians2dmsString() + "," + str(roundObs.difLRSDist) + ",," +
                                             roundObs.difMutiRoundHz.radians2dmsString() + "," + 
                                             roundObs.difMutiRoundVz.radians2dmsString() + "," + str(roundObs.difMutiRoundSDist) + "\n") 

        # 测回间检查
        for targetObs in self.targetObsList:
            # To add...
            pass

        return  resultInfoRoundCheck         

    # 超限数据剔除
    def dataClear(self):
        for targetObs in self.targetObsList:
            for roundObs in targetObs.roundObsList:
                # 剔除超限的水平角
                if abs(roundObs.difLRHz.value) > self.toleranceRound[0]:
                    for halfRoundObs in roundObs.halfRoundObsList:
                        # halfRoundObs.Hv = self.deleteTag
                        halfRoundObs.HzR2L = util.Angle(self.deleteTag) 
                        print()
                
                # 剔除超限的竖直角
                if abs(roundObs.difLRVz.value) > self.toleranceRound[1]:
                    for halfRoundObs in roundObs.halfRoundObsList:
                        halfRoundObs.vertical = util.Angle(self.deleteTag) 
                        # halfRoundObs.HzR2L = self.deleteTag
                
                # 剔除超限的距离
                if abs(roundObs.difLRSDist) > self.toleranceRound[2]:
                    for halfRoundObs in roundObs.halfRoundObsList:
                        halfRoundObs.SDist = self.deleteTag
                        # halfRoundObs.HzR2L = self.deleteTag
                
                        pass                

    # 测站点观测数据平均值计算
    def averageObsComputer(self):                       
        self.dataClear()
        for targetObs in self.targetObsList:
            hzList = list()
            verticalList = list()
            sDistList = list()

            for roundObs in targetObs.roundObsList:                
                for halfRoundObs in roundObs.halfRoundObsList:
                    if halfRoundObs.HzR2L.value != self.deleteTag:
                        hzList.append(halfRoundObs.HzR2L)

                    if halfRoundObs.vertical.value != self.deleteTag:
                        verticalList.append(halfRoundObs.vertical)

                    if halfRoundObs.SDist != self.deleteTag:
                        sDistList.append(halfRoundObs.SDist)

            if len(hzList) != 0:                
                averageHz = sum([x.value for x in hzList]) / len(hzList)
            else:
                averageHz = self.deleteTag
                print("ERROR: len(hzList) = 0")
                
            if len(verticalList) != 0:
                averageVertical = sum([x.value for x in verticalList]) / len(verticalList)
            else:
                averageVertical = self.deleteTag
                print("ERROR: len(verticalList) = 0")
               
            averageSdist = sum(sDistList) / len(sDistList)

            averageObs = (util.Angle(averageHz),
                          util.Angle(averageVertical),
                          averageSdist,
                          targetObs.indexTarget)
            self.averageObsList.append(averageObs)

    # 原始站点数据格式输出：测站点,观测方向,测回数,半测回标志,水平方向,垂直方向,距离,棱镜高,测站高
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
              
                    info = (infoStation + "," + infoTarget  + "," + infoRound + "," +
                            halfRoundObs.index_halfRound + "," + 
                            halfRoundObs.Hz.radians2dmsString() + "," + 
                            halfRoundObs.Vz.radians2dmsString() + "," + 
                            str(halfRoundObs.SDist) + "," + 
                            str(halfRoundObs.refHt) + "," + str(self.stationHt) + " \n")  
                                      
                    # print(info)
                    allInfoOneStation.append(info)

                    info = "" 

        return allInfoOneStation

    # 原始站点数据检查格式化输出：
    #   1）以目标点组织数据输出
    #   2）带外业限差计算输出
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
                    infoAverageMutiRound = (str(targetObs.averageMutiRoundHz.radians2dmsString()) + ","  + 
                                            str(targetObs.averageMutiRoundVz.radians2dmsString()) + "," + str(targetObs.averageMutiRoundSDist))
                else:                    
                    infoTarget = ""
                    infoAverageMutiRound = ",,,,,,"

                for indexHalfRound,halfRoundObs in enumerate(roundObs.halfRoundObsList):
                    # 仅在第一个半测量回时，输出测回编号                   
                    if indexHalfRound == 0:
                        infoRound = roundObs.indexRound

                        infoRoundComputer = (str(roundObs.difLRHz.radians2dmsString()) + "," + str(roundObs.difLRVz.radians2dmsString()) + "," + str(roundObs.difLRSDist) + ",," + 
                                             str(roundObs.averageLRHz.radians2dmsString()) + "," + str(roundObs.averageLRVz.radians2dmsString()) + "," + str(roundObs.averageLRSDist)) 
                        # To add...
                        infoMutiRoundDif = (util.Angle(roundObs.averageLRHz.value - targetObs.averageMutiRoundHz.value).radians2dmsString() + "," + 
                                            util.Angle(roundObs.averageLRVz.value - targetObs.averageMutiRoundVz.value).radians2dmsString() + "," + 
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
                        halfRoundObs.Hz.radians2dmsString() + "," + halfRoundObs.Vz.radians2dmsString() + "," + str(halfRoundObs.SDist) + "," + \
                        str(halfRoundObs.refHt) + "," + str(self.stationHt) + ",," + \
                        halfRoundObs.HzR2L.radians2dmsString() + "," + halfRoundObs.vertical.radians2dmsString() + ",," + \
                        infoRoundComputer + ",," + \
                        infoAverageMutiRound + ",," + \
                        infoMutiRoundDif + ",," + "\n"  
                                      
                    # print(info)
                    allInfoOneStation.append(info)

                    info = "" 
        return allInfoOneStation    
    
    # 原始站点数据检查格式化输出：
    #   1）以测回组织数据输出
    #   2）带外业限差计算输出
    def stringFormat_4(self):
        allInfoOneStation = [] 

        # 获取所有盘左的数据信息
        round_count = len(self.targetObsList[0].roundObsList)
        infoHalfRoundOnOff = "ON"                       
        for round_id in range(round_count):
            infoRoundOnOff = "ON"            
            for indexTag ,targetObs in enumerate(self.targetObsList):                
                for indexRound,roundObs in enumerate(targetObs.roundObsList): 
                    if indexRound == round_id: 
                        for indexHalfRound,halfRoundObs in enumerate(roundObs.halfRoundObsList):
                            if halfRoundObs.index_halfRound == "L":
                                infoHalfRound = halfRoundObs.index_halfRound
                                infoRound = roundObs.indexRound                                
                                infoStation = self.indexStation
                                
                                infoRoundComputer = (str(roundObs.difLRHz.radians2dmsString()) + "," + str(roundObs.difLRVz.radians2dmsString()) + "," + str(roundObs.difLRSDist) + ",," + 
                                             str(roundObs.averageLRHz.radians2dmsString()) + "," + str(roundObs.averageLRVz.radians2dmsString()) + "," + str(roundObs.averageLRSDist))                           
                                                                
                                if indexRound == 0:
                                    infoAverageMutiRound = (str(targetObs.averageMutiRoundHz.radians2dmsString()) + ","  + 
                                            str(targetObs.averageMutiRoundVz.radians2dmsString()) + "," + str(targetObs.averageMutiRoundSDist))
                                else:
                                    infoAverageMutiRound = ",,,,,,"
                                
                                infoMutiRoundDif = (util.Angle(roundObs.averageLRHz.value - targetObs.averageMutiRoundHz.value).radians2dmsString() + "," + 
                                        util.Angle(roundObs.averageLRVz.value - targetObs.averageMutiRoundVz.value).radians2dmsString() + "," + 
                                        str(roundObs.averageLRSDist - targetObs.averageMutiRoundSDist))                                    
                                
                                if infoHalfRoundOnOff == "OFF":
                                    infoHalfRound =""
                                    infoStation = "" 
                                
                                if infoRoundOnOff == "OFF": 
                                    infoRound = ""                                    

                                # if infoAverageMutiRoundOnOff == "OFF":
                                #     infoAverageMutiRound = ""

                                info = (infoStation + "," + infoRound + "," + infoHalfRound + "," + targetObs.indexTarget  + ",")

                                infoHalfRoundOnOff = "OFF"
                                infoRoundOnOff = "OFF"
                                infoAverageMutiRoundOnOff = "OFF"  
                                
                                infofixed = (halfRoundObs.Hz.radians2dmsString() + "," + halfRoundObs.Vz.radians2dmsString() + "," + str(halfRoundObs.SDist) + "," + 
                                            str(halfRoundObs.refHt) + "," + str(self.stationHt) + ",," + 
                                            "," + "," + halfRoundObs.vertical.radians2dmsString() + ",," + infoRoundComputer + ",," +
                                            infoAverageMutiRound + ",," +
                                            infoMutiRoundDif + "\n" ) 
                                
                                
                                info += infofixed

                                allInfoOneStation.append(info) 
        info = ""    

        # 获取所有盘右的数据信息                 
        infoHalfRoundOnOff = "ON"                       
        for round_id in range(round_count):
            infoRoundOnOff = "ON"            
            for indexTag ,targetObs in enumerate(self.targetObsList):                
                for indexRound,roundObs in enumerate(targetObs.roundObsList): 
                    if indexRound == round_id: 
                        for indexHalfRound,halfRoundObs in enumerate(roundObs.halfRoundObsList):
                            if halfRoundObs.index_halfRound == "R":
                                infoHalfRound = halfRoundObs.index_halfRound
                                infoRound = roundObs.indexRound                                
                                infoStation = self.indexStation
                                
                                if infoHalfRoundOnOff == "OFF":
                                    infoHalfRound =""
                                    infoStation = "" 
                                
                                if infoRoundOnOff == "OFF": 
                                    infoRound = ""


                                info = (infoStation + "," + infoRound + "," + infoHalfRound + "," + targetObs.indexTarget  + ",")
                                infoHalfRoundOnOff = "OFF"
                                infoRoundOnOff = "OFF"

                                infofixed = (halfRoundObs.Hz.radians2dmsString() + "," + halfRoundObs.Vz.radians2dmsString() + "," + str(halfRoundObs.SDist) + "," + 
                                            str(halfRoundObs.refHt) + "," + str(self.stationHt) + ",," + 
                                            halfRoundObs.HzR2L.radians2dmsString() + "," + halfRoundObs.vertical.radians2dmsString() + ",," + "\n" ) 
                                
                                info += infofixed

                                allInfoOneStation.append(info) 
        info = ""               
            
        return allInfoOneStation
   
# 一个标准的工程记录文件
class RoundMeasureFile:
    def __init__(self) -> None:
        pass    

    def generateRawMeasureFile(self,stationObsList,outPutFileDir):
         with open(outPutFileDir, 'w', encoding='utf-8') as file:      
            # file.write("测站点,观测方向,测回数,半测回标志,水平方向,垂直方向,距离,棱镜高,测站高" + "\n")
            stringCapital = ("测站点,观测方向,测回数,半测回标志,水平方向,,,垂直方向,,,距离,棱镜高,测站高,," + "\n")                        
            file.write(stringCapital)

            for stationObs in stationObsList:
                infoList = stationObs.stringFormat_2()
                for info in infoList:
                    file.write(info)
    
    # 以目标点组织数据输出
    def generateRawCheckFile(self,stationObsList,outPutFileDir):
        with open(outPutFileDir, 'w', encoding='utf-8') as file:            
            stringCapital = ("测站点,观测点,测回数,半测回标志,水平方向,,,垂直方向,,,距离,棱镜高,测站高,," +
                             "转换到盘左的Hz,,,转换到竖直角VzVz,,,," + 
                             "水平角2C差,,,垂直角指标差,,,距离差（测回内）,," + 
                             "（一测回）水平方向平均值,,,垂直方向平均值,,,距离平均值,," + 
                             "（多测回）水平方向平均值,,,垂直方向平均值,,,距离平均值,," + 
                             "（与多测回平均值的差）水平角差,,,垂直角差,,,距离差" + "\n")
                        
            file.write(stringCapital)

            for stationObs in stationObsList:
                infoList = stationObs.stringFormat_3()
                for info in infoList:
                    file.write(info)

            # 增加超限检查         
            resultInfoRoundCheck = (" \n out of range: " + "\n")
                                
            resultInfoRoundCheck += ("测站, 目标, 测回,," + 
                                     "（一测回）水平角差,,, 垂直角差,,, 距离差,," +
                                     "（与多测回平均值差）水平角差,,, 垂直角差,,, 距离差\n")
            # 输出表头
            file.write(resultInfoRoundCheck)
            
            # 输出超限项
            for stationObs in stationObsList:
                infoCheck = stationObs.stationObsCheck()
                file.write(infoCheck)
                pass
    
    # 以测回组织数据输出
    def generateRawCheckFileByRound(self,stationObsList,outPutFileDir):
         with open(outPutFileDir, 'w', encoding='utf-8') as file:            
            stringCapital = ("测站点,测回数,半测回标志,观测点,水平方向,,,垂直方向,,,距离,棱镜高,测站高,," +
                             "转换到盘左的Hz,,,转换到竖直角Vz,,,," + 
                             "水平角2C差,,,垂直角指标差,,距离差（测回内）,," + 
                             "（一测回）水平方向平均值,,,垂直方向平均值,,,距离平均值,," + 
                             "（多测回）水平方向平均值,,,垂直方向平均值,,,距离平均值,," + 
                             "（与多测回平均值的差）水平角差,,,垂直角差,,,距离差" + "\n")
                        
            file.write(stringCapital)

            for stationObs in stationObsList:
                infoList = stationObs.stringFormat_4()
                for info in infoList:
                    file.write(info)

    # 生成删除了粗差的观测数据,用于平差处理的输入
    def generateClearedDataFile(self,stationObsList,clearedFileDir):
        with open(clearedFileDir, 'w', encoding='utf-8') as file:
            stringCapital = ("测站点,观测方向,测回数,半测回标志,左盘方位角,竖直角,距离,测站高,棱镜高, \n")
            file.write(stringCapital)
            
            for indexStation,stationObs in enumerate(stationObsList):               
                
                stationObs.dataClear()

                stationObs.averageObsComputer()

                for targetObs, average in zip(stationObs.targetObsList, stationObs.averageObsList):
                    averageONOff = "ON"
                    
                    for roundObs in targetObs.roundObsList:
                        for halfRoundObs in roundObs.halfRoundObsList:
                            averageInfo = (str(average[0].value) + "," + str(average[1].value) + "," +
                                           str(average[2]) + ",")
                            if (averageONOff == "OFF"):
                                averageInfo = ""
                                
                            infoData = (stationObs.indexStation + "," + 
                                targetObs.indexTarget + "," + 
                                roundObs.indexRound + "," + 
                                halfRoundObs.index_halfRound + "," + 
                                str(halfRoundObs.HzR2L.value) + "," +
                                str(halfRoundObs.vertical.value) + "," + 
                                str(halfRoundObs.SDist) + "," +
                                str(stationObs.stationHt) + "," +
                                str(halfRoundObs.refHt) + ",," + 
                                averageInfo + "\n")
                            file.write(infoData)

                            averageONOff = "OFF"
    
    # 生成删除了粗差的观测数据的平均值,用于计算概略坐标的计算   
    def generateClearedAverageFile(self,stationObsList,clearedFileDir):
        with open(clearedFileDir, 'w', encoding='utf-8') as file:
            stringCapital = ("测站点,观测方向,左盘方位角,竖直角,距离,测站高,棱镜高, \n")
            file.write(stringCapital)
            
            for indexStation,stationObs in enumerate(stationObsList):               
                
                stationObs.dataClear()

                stationObs.averageObsComputer()

                for targetObs, average in zip(stationObs.targetObsList, stationObs.averageObsList):
                                        
                    averageInfo = (str(average[0].value) + "," + str(average[1].value) + "," +
                                    str(average[2]))
                    
                    infoData = (stationObs.indexStation + "," + 
                        targetObs.indexTarget + "," +                        
                        averageInfo + "," + 
                        str(stationObs.stationHt) + "," +
                        str(targetObs.roundObsList[0].halfRoundObsList[0].refHt) + ",," +
                        average[0].radians2dmsString() + "\n")
                    
                    file.write(infoData)




              
  










