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
#   盘左时： 90 - L (左天顶距：当初准轴水平时为 90度)
#   盘左时： R - 270
#
class halfRoundObs:
    def __init__(self,index_halfRound = "L",refHt = 0.0, Hz = 0.0, Vz = 0.0, SDist = 0.0) -> None:
        self.index_halfRound = index_halfRound
        self.refHt = refHt 
        self.Hz = Hz
        self.Vz = Vz
        self.SDist = SDist  # 斜距

        # 盘右转为盘左后的值
        self.HzR2L = ""
        self.VzR2L = ""

    def rightFace2LeftFace(self):
        if self.index_halfRound == "R":
            if self.Hz >= 180:           
                self.HzR2L = self.Hz - 180
            if self.Hz < 180:           
                self.HzR2L = self.Hz + 180               
  
            self.VzR2L = 90 - self.Hz
            self.VzR2L = self.Hz -270

            pass

# 一个测回类：仅是一个目标点的一个测回观测，但可以包含多次按键测量的数据。
class RoundObs:
    def __init__(self,indexRound = "",halfRoundObsList = []) -> None:
        self.indexRound = indexRound
        self.halfRoundObsList = halfRoundObsList 

    # 计算左右盘互差，及均值： (盘左 - 盘右)
    def roundCompute(self):
        leftRoundObs = halfRoundObs()
        rightRoundObs = halfRoundObs()     
        for item in self.halfRoundObsList:
            if item.index_halfRound == "L":
                leftRoundObs = item
            if item.index_halfRound == "R":                
                rightRoundObs = item

        self.difLRHz = leftRoundObs.Hz - rightRoundObs.HzR2L
        self.difLRVz = leftRoundObs.Vz - rightRoundObs.VzR2L
        self.difLRSDist = leftRoundObs.SDist - rightRoundObs.SDist

        self.averageLRHz = (leftRoundObs.Hz + rightRoundObs.HzR2L) / 2.0
        self.averageLRVz = (leftRoundObs.Vz + rightRoundObs.VzR2L) / 2.0
        self.averageLRSDist = (leftRoundObs.SDist + rightRoundObs.SDist) / 2.0    

# 一个观测点类（包括多个测回）
class TargetObs:
    def __init__(self,indexTarget = "", roundObsList = []) -> None:
        self.indexTarget = indexTarget
        self.roundObsList = roundObsList

    # 计算一个观测点的多个测回的均值，及测回差： （测回 - 平均值）
    def multiRoundCompute(self):
        self.averageMutiRoundHz = sum(item.averageLRHz for item in self.roundObsList) / len(self.roundObsList)
        self.averageMutiRoundVz = sum(item.averageLRVz for item in self.roundObsList) / len(self.roundObsList)
        self.averageMutiRoundSDist = sum(item.averageLRSDist for item in self.roundObsList) / len(self.roundObsList)

        # 测回差
        for roundObs in self.roundObsList:
            roundObs.difRoundHz = roundObs.averageLRHz - self.averageMutiRoundHz
            roundObs.difRoundVz = roundObs.averageLRVz - self.averageMutiRoundVz
            roundObs.difRoundSDist = roundObs.averageLRSDist - self.averageMutiRoundSDist        

# 一个站点的所有目标点
class StationObs:
    def __init__(self,indexStation = "", stationHt = 0.0,targetObsList = []) -> None:
        self.indexStation = indexStation
        self.stationHt = stationHt
        self.targetObsList = targetObsList

    def stationCompute(self):
        for targetObs in self.targetObsList:
            for roundObs in targetObs.roundObsList:
                for halfRoundObs in roundObs.halfRoundObsList:
                    halfRoundObs.rightFace2LeftFace()
                    print()
                roundObs.roundCompute()
            targetObs.multiRoundCompute()    

    # 测站数据质检检查：1）测回内超限检查，2）测回间超限检查
    def stationObsCheck(self,toleranceRound = [0,0,0],toleranceMutiRound = [0,0,0]):
        # 测回间检查
        for targetObs in self.targetObsList:
            # To add...
            pass
        
        
        # 测回内检查: station  :  target  :  round
        resultInfoRoundCheck = "" 
        for targetObs in self.targetObsList:
            for roundObs in targetObs.roundObsList:
                if abs(roundObs.difLRHz) > toleranceRound[0] or \
                    abs(roundObs.difLRVz) > toleranceRound[1] or \
                    abs(roundObs.difLRSDist) > toleranceRound[2] :

                    resultInfoRoundCheck += (self.indexStation + "," + targetObs.indexTarget + "," + 
                                             roundObs.indexRound + "," + str(roundObs.difLRHz) + "," + 
                                             str(roundObs.difLRVz) + "," + str(roundObs.difLRSDist) + "\n") 

        return  resultInfoRoundCheck         

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
                        # infoMutiRoundDif
                    else:                        
                        infoStation = ""
                        infoTarget = "" 
                        infoAverageMutiRound = ",,"                       

                        infoRound = ""   
                        infoRoundComputer = ",,,,,," 

                    info = infoStation + "," + infoTarget  + "," + infoRound + "," + \
                        halfRoundObs.index_halfRound + "," +  \
                        str(halfRoundObs.Hz) + "," + str(halfRoundObs.Vz) + "," + str(halfRoundObs.SDist) + "," + \
                        str(halfRoundObs.refHt) + "," + str(self.stationHt) + ",," + \
                        str(halfRoundObs.HzR2L) + "," + str(halfRoundObs.VzR2L) + ",," + \
                        infoRoundComputer + ",," + \
                        infoAverageMutiRound + ",," + "\n"  
                                      
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
                             "水平方向平均值,垂直方向平均值,距离平均值（测回内）,," + "\n")
                        
            file.write(stringCapital)

            for stationObs in stationObsList:
                infoList = stationObs.stringFormat_3()
                for info in infoList:
                    file.write(info)

            # 增加超限检查         
            resultInfoRoundCheck = (" \n out of range: " + "\n")
                                # (str(data) + " : " for data in toleranceRound) + "\n")
            resultInfoRoundCheck += ("station, target, round,diffHz, diffVz, diffSDist  \n")
            # 输出表头
            file.write(resultInfoRoundCheck)
            
            # 输出超限项
            for stationObs in stationObsList:
                infoCheck = stationObs.stationObsCheck([0,0,0])
                file.write(infoCheck)
                pass