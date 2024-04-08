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

# 左测回类
class halfRoundObs:
    def __init__(self,index_halfRound = "L",refHt = 0.0, Hz = 0.0, Vz = 0.0, SDist = 0.0) -> None:
        self.index_halfRound = index_halfRound
        self.refHt = refHt 
        self.Hz = Hz
        self.Vz = Vz
        self.SDist = SDist  # 斜距

    def rightFace2LeftFace(self):
        if self.index_halfRound == "R":
            # To add...
            testValue = 0.0
            self.HzR2L = self.Hz + 180
            self.VzR2L = testValue
            pass

# 一个测回类（仅是一个目标点的一个测回观测）
class RoundObs:
    def __init__(self,indexRound = "One",halfRoundObsList = []) -> None:
        self.indexRound = indexRound
        self.halfRoundObsList = halfRoundObsList 

    # 计算左右盘互差，及均值： (盘左 - 盘右)
    def roundCompute(self):
        leftRoundObs = self.halfRoundObsList[0]
        rightRoundObs = self.halfRoundObsList[-1]

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
        self.averageMutiRoundDist = sum(item.averageLRDist for item in self.roundObsList) / len(self.roundObsList)

        for roundObs in self.roundObsList:
            roundObs.difRoundHz = roundObs.Hz - self.averageMutiRoundHz
            roundObs.difRoundVz = roundObs.Vz - self.averageMutiRoundVz
            roundObs.difRoundSDist = roundObs.SDist - self.averageMutiRoundDist        

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

    # 测站点,观测方向,测回数,半测回标志,水平方向,垂直方向,距离,棱镜高,测站高
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

    # 外业质量检查
    def stringFormat_3(self):
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
                        str(halfRoundObs.refHt) + "," + str(self.stationHt) + "," + \
                        str(halfRoundObs.HzR2L) + "," + str(halfRoundObs.VzR2L) + "," + " \n"  
                                      
                    # print(info)
                    allInfoOneStation.append(info)

                    info = "" 
        return allInfoOneStation

    # def stringFormat_1(self):
    #     allInfoOneStation = []

    #     for targetObs in self.targetObsList:
    #         for roundObs in targetObs.roundObsList:
    #             for halfRoundObs in roundObs.halfRoundObsList:
    #                 info = self.indexStation + "," + targetObs.indexTarget  + "," +  \
    #                     roundObs.indexRound + "," + halfRoundObs.index_halfRound + "," +  \
    #                     halfRoundObs.refHt + "," + halfRoundObs.Hz + "\n"                    
    #                 print(info)
    #                 allInfoOneStation.append(info)

    #                 info = "" 

    #     return allInfoOneStation  

# 一个标准的工程记录文件
class RoundMeasureFile:
    def __init__(self) -> None:
        pass
    

    def generateRoundMeasureFile(self,stationObsList,outPutFileDir):
        with open(outPutFileDir, 'w', encoding='utf-8') as file:      
            file.write("测站点,观测方向,测回数,半测回标志,水平方向,垂直方向,距离,棱镜高,测站高" + "\n")

            for stationObs in stationObsList:
                infoList = stationObs.stringFormat_2()
                for info in infoList:
                    file.write(info)