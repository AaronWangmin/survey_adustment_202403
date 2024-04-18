import numpy as np
import math

import util

## 参数平差

### 平差前各向量符号
#  观测向量: L
#  观测向量权阵：P

#  参数向量估计值：X_0

### 平差后各向量符号
#  观测向量: L_computed
#  观测向量残差(待求量)：V

#  参数向量：X
#  参数向量改正数(待求量)：dX

# 观测方程：
# L_computed = B * X + d

# L_computed = L + V
# X = X_0 + dX

# 误差方程：
# V = B * dX - conL
# conL = L - (B *  X_0 + d)

class Adj_ts_3d():
    def __init__(self,countObs,countPara) -> None: 
        self.countObs = countObs
        self.countPara = countPara

        # 观测信息
        self.L = np.zeros(countObs)
        self.V = np.zeros(countObs)
        self.L_computed = np.zeros(countObs)
        self.P_obs = np.eye(countObs)

        # 参数信息
        self.X_0 = np.zeros(countPara)
        self.dX = np.zeros(countPara)
        self.X = np.zeros(countPara)
        self.Q_para = np.eye(countPara)

        # 系数矩阵 B,及 常数项向量
        self.B = np.zeros((countObs,countPara))
        self.consL = np.zeros(countObs)

    def getX_0(self,X_0):
        index = 0
        for coord in X_0:
            for value in coord:
                self.X_0[index] = value
                index += 1
    
    def generateB(self,clearedDataItemList):
        for index_obs,obs in enumerate(clearedDataItemList):
            stationCoord_0 = self.X_0[obs.stationOrderForAdj * 4 : obs.stationOrderForAdj * 4 + 4]
            targetCoord_0 = self.X_0[obs.targetOrderForAdj * 4 : obs.targetOrderForAdj * 4 + 4]

            b,constantItem = self.b_computer(obs,
                                obs.stationOrderForAdj,stationCoord_0,
                                obs.targetOrderForAdj,targetCoord_0)
            self.B[index_obs] = b
            self.consL[index_obs] = constantItem 
            pass
    
    # 计算三个观测值的系数,测站定向角系数 theta，以及常数项：bHz, bVz, bSdist，constant
    #   待求解参数（测站点，目标点）在列向量中的的序列号，从 0 开始：index_station, index_target
    # 
    def b_computer(self,observation,
                   index_station,stationCoord_0, 
                   index_target,targetCoord_0):
        
        deltaXYZ, distance,distance_2D = self.diffTwoPoints(stationCoord_0[0:3],targetCoord_0[0:3])

        deltaX = deltaXYZ[0]
        deltaY = deltaXYZ[1]
        deltaZ = deltaXYZ[2] 
        
        rho =  180 * 3600.0 / math.pi

        b = np.zeros(self.countPara)
        constantItem = 0.0         

        #  方向观测值系数
        if observation.obsTag == "Hz":
            # 测站点dx,dy的系数
            b[index_station * 4]     =   rho * deltaY / (distance * distance)
            b[index_station * 4 + 1] = - rho * deltaX / (distance * distance)            

            # 目标点dx,dy,dz的系数
            b[index_target * 4]     = - rho * deltaY / (distance * distance)
            b[index_target * 4 + 1] =   rho * deltaX / (distance * distance)
            
            # 测站定向角 dTheta的 系数
            b[index_target * 4 + 3] = -1

            # arrtan 可能有问题。。。。。。。。。
            # 常数项
            theta_0 = stationCoord_0[3]
            constantItem = observation.obsValue + theta_0 - np.arctan2(deltaY, deltaX)

        # To add light correct...........
        # 距离观测值系数
        if observation.obsTag == "Sdist":
            b = np.zeros(self.countPara)
            # 测站点dx,dy,dh的系数
            b[index_station * 4]     = - deltaX / distance
            b[index_station * 4 + 1] = - deltaY / distance   
            b[index_station * 4 + 2] = - deltaZ / distance         

            # 目标点dx,dy,dz的系数
            b[index_target * 4]     =   deltaX / distance
            b[index_target * 4 + 1] =   deltaY / distance   
            b[index_target * 4 + 2] =   deltaZ / distance
            
            # 常数项
            constantItem = observation.obsValue - \
                math.pow(deltaX * deltaX + deltaY * deltaY + 
                         (deltaZ + observation.refHt - observation.stationHt) * (deltaZ + observation.refHt - observation.stationHt) 
                         ,0.5)

        # To add light correct..........
        # 竖直角观测值系数
        if observation.obsTag == "Vertical":
            b = np.zeros(self.countPara)
            # 测站点dx,dy,dz的系数
            b[index_station * 4]     = - rho * deltaZ * deltaX / (distance * distance * distance_2D)
            b[index_station * 4 + 1] = - rho * deltaZ * deltaY / (distance * distance * distance_2D) 
            b[index_station * 4 + 2] =   rho * distance_2D * deltaX / (distance * distance)            

            # 目标点dx,dy,dz的系数
            b[index_target * 4]     =   rho * deltaZ * deltaX / (distance * distance * distance_2D * distance_2D)
            b[index_target * 4 + 1] =   rho * deltaZ * deltaY / (distance * distance * distance_2D * distance_2D) 
            b[index_target * 4 + 2] = - rho * distance_2D / (distance * distance)

            # 常数项
            constantItem = observation.obsValue - \
                math.cos((deltaZ + observation.refHt - observation.stationHt) / distance)
            
        return b,constantItem
      
    # 计算测站点到目标点的坐标差,以及距离：deltaX, deltaY, deltaZ
    def diffTwoPoints(self,stationCoord,targetCoord):
        deltaXYZ = targetCoord - stationCoord
        
        # 3D空间距离
        distance = np.linalg.norm(targetCoord - stationCoord)

        # 2D平面距离
        stationCoord_2d = stationCoord[0:2]
        targetCoord_2d = targetCoord[0:2]
        distance_2D = np.linalg.norm(targetCoord_2d - stationCoord_2d)
        
        # assert distance_2D != 0

        return deltaXYZ,distance,distance_2D

    # 计算验前中误差，以仪器的角度观测精度为单位权中误差，单位为： 秒
    #                            距离的中误差: a + b * sdist
    #                                 固定误差 a, 单位为： mm
    #                                 比例误差 b, 单位为： ppm (10 -6)
    #                                 距离sdist,  单位为： km
    def generatePreObsP(self,clearedDataItemList,sigama_angle,sigma_dist_a,sigma_dist_b):
         for index_obs,obs in enumerate(clearedDataItemList):
            if obs.obsTag == "Hz" or obs.obsTag == "Vertical":
                self.P_obs[index_obs,index_obs] = 1
                 
            if obs.obsTag == "Sdist":
                sigma_dist = sigma_dist_a + sigma_dist_b * obs.obsValue / 1000.0
                
                # sigma_angle_radian = util.Angle(sigama_angle,util.AngleType.seconds)
                # sigma_angle_radian.seconds2radians()
                
                p_dist = sigama_angle * sigama_angle / (sigma_dist * sigma_dist)
                self.P_obs[index_obs,index_obs] = p_dist 
 
    # 秩亏自由网平差计算，及精度评定
    def adjCompute(self,t = 7):
        N = np.transpose(self.B) @ self.P_obs @ self.B
        W = np.transpose(self.B) @ self.P_obs @ self.consL
        
        Nm_inverse = np.transpose(N) @ np.linalg.inv(N @ np.transpose(N))
        
        self.dX = Nm_inverse @ W
        
        self.V = self.B @ self.dX - self.consL
        
        self.L_computed = self.L + self.V
        
        self.X = self.X_0 + self.dX        
        
        self.Q_para = Nm_inverse @ Nm_inverse @ N
        
        sigama_2 = np.transpose(self.V) @ self.P_obs @ self.V / (self.countObs - t)
        
        self.sigama_0 = np.sqrt(sigama_2)
        
        self.sigama_para = np.sqrt(sigama_2 * np.diag(self.Q_para))
        
        print("test: adj compute...")
       
class ClearedData():
    def __init__(self) -> None:
        self.clearedDataItemList = list()
        
    def readClearedDataFile(self,fileDir):
        with open(fileDir, 'r', encoding='utf-8') as fo:
            line = fo.readline()
            line = fo.readline()
            while line:
                clearedDataItem = ClearedDataItem()
                clearedDataItem.parseDateItem(line)
                self.clearedDataItemList.extend(clearedDataItem.obsList)

                line = fo.readline()
    
    # 设站站与目标点统一编号,为参数位置计算做准备
    def reOrderParaForAdj(self):
        targetOrderList = list()
        for obs in self.clearedDataItemList:
            targetOrderList.append(obs.indexStation)
        targetOrderList = util.removeDuplicatesList(targetOrderList)

        for obs in self.clearedDataItemList:
            for targetOrderIdex,targetOrder in enumerate(targetOrderList):
                if obs.indexTarget == targetOrder:
                    obs.targetOrderForAdj = targetOrderIdex
                
                if obs.indexStation == targetOrder:
                    obs.stationOrderForAdj = targetOrderIdex       

    def out2File(self,clearedObsFileDir):
        with open(clearedObsFileDir, 'w', encoding='utf-8') as file:
            stringCapital = ("测站点,观测方向,观测类型,观测值,测站高,棱镜高,站点序号(平差),目标序号(平差) \n")
            file.write(stringCapital)

            for item in self.clearedDataItemList:
                    info = (item.indexStation + "," + item.indexTarget + "," + 
                                item.obsTag + "," + str(item.obsValue) + "," +
                                str(item.stationHt) + "," + str(item.refHt) + "," + 
                                str(item.stationOrderForAdj) + "," +
                                str(item.targetOrderForAdj) + "\n") 
                    file.write(info)
                    # print("test..........")                                 

class ClearedDataItem():
    def __init__(self) -> None:
        self.obsList = list()

    def parseDateItem(self,strLine):
        # 水平、竖直、距离分别在行的第4，5，6位置
        obsPosInLine = [4,5,6]
        for pos in obsPosInLine:
            obs = Observation()
            if obs.parserObs(strLine,pos) != None:
                self.obsList.append(obs)

# 三个的观测量的一个：方向观测值，或竖直角，或距离
class Observation():
    def __init__(self) -> None:
        self.indexStation = ""
        self.indexTarget = ""
        # 标记：用来区分水平角、竖直角、距离
        self.obsTag = ""
        self.obsValue = 0.0
        self.stationHt = 0.0
        self.refHt = 0.0
        # 生成 B 矩阵中测站点、目标点的顺序号
        self.stationOrderForAdj = ""
        self.targetOrderForAdj = ""

        # 文件中的无效数据标记
        self.deletedTag = "999999"

    def parserObs(self,strLine,obsPos):        
        infoList = strLine.split(",")

        if infoList[obsPos] != self.deletedTag:
            self.obsTag = self.parseObsPos(obsPos)
            self.obsValue = float(infoList[obsPos])

            self.indexStation = infoList[0]
            self.indexTarget = infoList[1]
            self.stationHt = float(infoList[7])
            self.refHt = float(infoList[8]) 

            # self.codeStationPreAdjustment = int(infoList[9])
            #  To add.... 目标的ID

            return "OK"           
        else:
            return None
    
    # 在 clearedData文件的行中，水平角、竖直角、距离在以“,”分割的位置    
    def parseObsPos(self,obsPos):
        if obsPos == 4:
            return "Hz"
        if obsPos == 5:
            return "Vertical"
        if obsPos == 6:
            return "Sdist"

##### test clearData...............
clearedDataFileDir = "data\\02_clearedData_1.txt"
# clearedDataFileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\02_clearedData.txt"

clearData = ClearedData()
clearData.readClearedDataFile(clearedDataFileDir)
clearData.reOrderParaForAdj()

clearedObsFileDir = "data\\03_clearedObs_1.txt"
# clearedObsFileDir = "G:\\learn_python_202012\\adjustment-parameter-202404\\03_clearedObs.txt"
clearData.out2File(clearedObsFileDir)

##### test Adj_ts_3d...............
countObs = 535
countPara = 15  # 5个站点 * 3个参数值（XYZ）
X_0_intial = [(-0.8736609303775807, 14.967716963273462, -0.21748118731452684, 0.0),
       (0.0, 0.0, 0.0, 0.0),
       (23.172887334619638, -0.018205564173390653, -1.3273795874105865, 0.0),
       (31.72325757418823, 29.200592775320494, -1.1315456361540115, 0.0),
       (12.430182539213149, 25.38427122112945, -0.9749403607005105, 0.0)]

adj = Adj_ts_3d(countObs,countPara)
adj.getX_0(X_0_intial )
print("test: getX_0()....")

adj.generateB(clearData.clearedDataItemList)
print("test: B, L")

# TS06: 0.5, 0.6, 1
# TS09:   1, 1.5, 2
adj.generatePreObsP(clearData.clearedDataItemList, 1, 1.5, 2)
print("test: preObsP")

adj.adjCompute()
print("test: adj")

