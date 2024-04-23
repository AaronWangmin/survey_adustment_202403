import numpy as np
import math

import util
import measureUtil
import ellipsoild as eps

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
        self.t = self.countPara - 7

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
            stationCoord_0 = self.X_0[obs.stationOrderForAdj * 5 : obs.stationOrderForAdj * 5 + 5]
            targetCoord_0 = self.X_0[obs.targetOrderForAdj * 5 : obs.targetOrderForAdj * 5 + 5]

            b,constantItem = self.b_computer(obs,
                                obs.stationOrderForAdj,stationCoord_0,
                                obs.targetOrderForAdj,targetCoord_0)
            self.B[index_obs] = b
            self.consL[index_obs] = constantItem 
    
    # 计算三个观测值的系数,测站定向角系数 theta，以及常数项：bHz, bVz, bSdist，constant
    #   待求解参数（测站点，目标点）在列向量中的的序列号，从 0 开始：index_station, index_target
    # 
    def b_computer(self,observation,
                   index_station,stationCoord_0, 
                   index_target,targetCoord_0):        
        
        deltaENU, distance,distance_2D = self.diffTwoPoints(stationCoord_0[0:3],targetCoord_0[0:3])
        
        # 测站初始坐标增量
        deltaX = deltaENU[0]
        deltaY = deltaENU[1]
        deltaZ = deltaENU[2] 
        
        # 测站初始定向角
        theta_0 = stationCoord_0[3]
        # 测站初始折光系数
        k0 = stationCoord_0[4]        
        
        rho =  180 * 3600.0 / math.pi
        
        # 平均曲率
        latitude = util.Angle(31.10012878,util.AngleType.degrees)
        latitude.degrees2radians()
        ellip = eps.Ellipsoild()
        R = ellip.computeRn(latitude.value)        
        
        # 折光系数初值,及改正项        
        deltaLight = - distance_2D * distance_2D * (1 - k0) / (2 * R) 

        b = np.zeros(self.countPara)
        constantItem = 0.0         

        #  方向观测值系数
        if observation.obsTag == "Hz":
            # 测站点dx,dy的系数
            b[index_station * 5]     =   rho * deltaY / (distance_2D * distance_2D)
            b[index_station * 5 + 1] = - rho * deltaX / (distance_2D * distance_2D)            

            # 测站定向角 dTheta的 系数
            b[index_station * 5 + 3] = -1
            
            # 目标点dx,dy,dz的系数
            b[index_target * 5]     = - rho * deltaY / (distance_2D * distance_2D)
            b[index_target * 5 + 1] =   rho * deltaX / (distance_2D * distance_2D)            

            # arrtan 可能有问题。。。。。。。。。
            # 常数项            
            oriental = measureUtil.computeOriental(deltaY,deltaX)
            L0_angle = observation.obsValue + theta_0
            
            if L0_angle >= 2 * math.pi:
                L0_angle = L0_angle - 2 * math.pi
                                
            constantItem = rho * (L0_angle - oriental)
            # np.arctan2(deltaY, deltaX)
            print("test... theta_0....")

        # To add light correct...........
        # 距离观测值系数
        if observation.obsTag == "Sdist":
            b = np.zeros(self.countPara)
            # 测站点dx,dy,dh的系数
            b[index_station * 5]     = - deltaX / distance
            b[index_station * 5 + 1] = - deltaY / distance   
            b[index_station * 5 + 2] = - deltaZ / distance         

            # 站点折光改正系数           
            b[index_station * 5 + 4] = deltaZ * distance_2D / (2 * R * distance)
            
            # 目标点dx,dy,dz的系数
            b[index_target * 5]     =   deltaX / distance
            b[index_target * 5 + 1] =   deltaY / distance   
            b[index_target * 5 + 2] =   deltaZ / distance            
            
            # 常数项  
            constantItem = observation.obsValue - \
                math.pow(deltaX * deltaX + deltaY * deltaY + 
                         (deltaZ + observation.refHt - observation.stationHt + deltaLight) * 
                         (deltaZ + observation.refHt - observation.stationHt + deltaLight) 
                         ,0.5)
            print("test... sdist constant ....")

        # To add light correct..........
        # 竖直角观测值系数
        if observation.obsTag == "Vertical":
            b = np.zeros(self.countPara)
            # 测站点dx,dy,dz的系数
            b[index_station * 5]     = - rho * deltaZ * deltaX / (distance * distance * distance_2D)
            b[index_station * 5 + 1] = - rho * deltaZ * deltaY / (distance * distance * distance_2D) 
            b[index_station * 5 + 2] =   rho * distance_2D * deltaX / (distance * distance)            

            # 平均地球曲率及折光改正
            b[index_station * 5 + 4] = - rho * pow(distance_2D,3) / (2 * R * distance * distance)
            
            # 目标点dx,dy,dz的系数
            b[index_target * 5]     =   rho * deltaZ * deltaX / (distance * distance * distance_2D * distance_2D)
            b[index_target * 5 + 1] =   rho * deltaZ * deltaY / (distance * distance * distance_2D * distance_2D) 
            b[index_target * 5 + 2] = - rho * distance_2D / (distance * distance)

            # 常数项            
            vertical_0 = math.acos((deltaZ + observation.refHt - observation.stationHt + deltaLight) / distance)
            constantItem = rho * (observation.obsValue - vertical_0)
            print("test... vertical_0....")
        
        if(abs(constantItem) >= 16 and observation.obsTag == "Hz"):
            # Hz Vertical Sdist
            print(observation.obsTag)
        
        if(abs(constantItem) >= 29 and observation.obsTag == "Vertical"):
            # Hz Vertical Sdist
            print(observation.obsTag)
            
        if(abs(constantItem) >= 0.002 and observation.obsTag == "Sdist"):
            # Hz Vertical Sdist
            print(observation.obsTag)
            
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
    def adjCompute(self):
        N = np.transpose(self.B) @ self.P_obs @ self.B
        W = np.transpose(self.B) @ self.P_obs @ self.consL
        
        Nm_inverse = np.transpose(N) @ np.linalg.pinv(N @ np.transpose(N))
        
        self.dX = Nm_inverse @ W
        
        self.V = self.B @ self.dX - self.consL
        
        self.L_computed = self.L + self.V
        
        self.X = self.X_0 + self.dX        
        
        self.Q_para = Nm_inverse @ Nm_inverse @ N
        
        sigama_2 = np.transpose(self.V) @ self.P_obs @ self.V / (self.countObs - self.t)
        
        self.sigama_0 = np.sqrt(sigama_2)
        
        self.sigama_para = np.sqrt(sigama_2 * np.diag(self.Q_para))
        
        test = np.diag(self.Q_para)
        
        print("test: adj compute...")
       
class ClearedData():
    def __init__(self) -> None:
        self.clearedDataItemList = list()
    
    # 直接读取平差所需要的观测值数据
    def readObsForAdjFile(self,fileDir):
        with open(fileDir, 'r', encoding='utf-8') as fo:
            line = fo.readline()
            line = fo.readline()
            while line:
                infoList = line.split(",")
                obs = Observation()
                obs.indexStation = infoList[0]
                obs.indexTarget = infoList[1]
                obs.obsTag = infoList[2]
                obs.obsValue = float(infoList[3])
                obs.stationHt = float(infoList[4])
                obs.refHt = float(infoList[5])
                obs.stationOrderForAdj = int(infoList[6])
                obs.targetOrderForAdj = int(infoList[7])                
                
                self.clearedDataItemList.append(obs)

                line = fo.readline()
    
    # 解析ClearDataFile, 得到平差所需要的观测值数据
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

##### test clearData.............
# clearedDataFileDir = "data\\02_clearedData_1.txt"
clearedDataFileDir = "data\\sh20240418-1_02_clearedData.txt"

outPutPrefix = clearedDataFileDir.split("_")[0]

clearData = ClearedData()
clearData.readClearedDataFile(clearedDataFileDir)
clearData.reOrderParaForAdj()

clearedObsFileDir = str(outPutPrefix + "_03_clearedObs.txt")
clearData.out2File(clearedObsFileDir)



##### test Adj_ts_3d...............
clearedObsFile = "data\\sh20240418-1_03_clearedObs_2.txt"
clearData = ClearedData()
clearData.readObsForAdjFile(clearedObsFile)
countObs = 1026
countPara = (5 * 5)   # 5个站点 * （3个参数值（XYZ）+ 1个测站定向角 + 1个大气折光改正） 
X_0_intial = [(0,0,0,0,1.3),
       (7.5328586172298335,42.71975085507182,-0.08396228993803155,3.141587459,1.3),
       (-44.10333955843989,46.53699782891333,0.04998859829709336,1.470014085,1.3),
       (-58.541570409993184,64.11429275705768,-0.14503027655293566,2.279357124,1.3),
       (-59.8831692809281,22.290795727095485,-0.04903186626487553,6.140707647,1.3)]

adj = Adj_ts_3d(countObs,countPara)
adj.getX_0(X_0_intial )
print("test: getX_0()....")

adj.generateB(clearData.clearedDataItemList)

# test.... conL
# k = 10
# ind = np.argpartition(adj.consL, -k)[-k:]
# sorted_indices_1d = adj.consL.argsort()[::-1]
# sorted_array_1d = adj.consL[sorted_indices_1d]
# sorted_array_1d = np.sort(adj.consL, kind='quicksort',reverse=True)

print("test: B, L")

# TS06: 0.5, 0.6, 1
# TS09:   1, 1.5, 2
adj.generatePreObsP(clearData.clearedDataItemList, 0.5, 0.6, 1)

# sorted_indices_2d = adj.P_obs.flatten().argsort()[::-1]
# sorted_array_2d = adj.P_obs.flatten()[sorted_indices_2d].reshape(adj.P_obs.shape)
print("test: preObsP")

adj.adjCompute()
print("test: adj")

# test.... adj.V
# max_row_index = np.argmax(adj.V)
# k = 10
# ind = np.argpartition(adj.V, -k)[-k:]
# sorted_indices_1d = adj.V.argsort()[::-1]
# sorted_array_1d = adj.V[sorted_indices_1d]
print("test...v")

