import math

import util
import round_measure as rm
import ellipsoild as es

# 根据方位角、竖直角、斜距计算另外一个点的 XYZ坐标
# 
#   坐  标：X：为北方向， Y：东方向 ，Z: 
#  
#   竖直角：-90~90， 以水平面为起始0度
#   
def compute3DXYZ(startXYZ,Hz,Vertical,SDist,stationHt = 0, refHt =0):
    X1 = startXYZ[0]
    Y1 = startXYZ[1]
    Z1 = startXYZ[2]

    # TODO: + -
    deltaZ = SDist * math.cos(Vertical) + (stationHt - refHt)

    distHorizontal = SDist * math.sin(Vertical)

    deltaX = distHorizontal * math.cos(Hz)
    deltaY = distHorizontal * math.sin(Hz)

    X2 = X1 + deltaX
    Y2 = Y1 + deltaY
    Z2 = Z1 + deltaZ

    return (X2,Y2,Z2)

def computerX0(fileDir):
    obsValueList = []
    with open(fileDir, 'r', encoding='utf-8') as fo:
            line = fo.readline()
            while line:
                infoLine = line.split(",")
                obsInfo = rm.halfRoundObs()
                obsInfo.startId = infoLine[0] 
                obsInfo.endId = infoLine[1]                
                             
                obsInfo.Hz =  util.Angle(float(infoLine[2]),util.AngleType.radians)                
                               
                obsInfo.vertical =  util.Angle(float(infoLine[3]),util.AngleType.radians)
                
                obsInfo.SDist = float(infoLine[4]) 
                
                obsInfo.stationHt = float(infoLine[5])              
                
                obsInfo.refHt = float(infoLine[6].strip())  
                
                obsValueList.append(obsInfo)
                
                line = fo.readline()
                
    p1 = (0, 0, 0)
    
    p2 = compute3DXYZ(p1,obsValueList[0].Hz.value,
                      obsValueList[0].vertical.value,
                      obsValueList[0].SDist,
                      obsValueList[0].stationHt,
                      obsValueList[0].refHt)
    
    p5 = compute3DXYZ(p1,obsValueList[1].Hz.value,
                      obsValueList[1].vertical.value,
                      obsValueList[1].SDist,
                      obsValueList[1].stationHt,
                      obsValueList[1].refHt)
    
    p3 = compute3DXYZ(p2,obsValueList[2].Hz.value,
                    obsValueList[2].vertical.value,
                    obsValueList[2].SDist,
                    obsValueList[2].stationHt,
                    obsValueList[2].refHt)
    
    p4 = compute3DXYZ(p2,obsValueList[3].Hz.value,
                    obsValueList[3].vertical.value,
                    obsValueList[3].SDist,
                    obsValueList[3].stationHt,
                    obsValueList[3].refHt)
    
    
    return p1,p2,p3,p4,p5
    
def generateX0File(X0ObsFileDir,X0CoordFileDir):
    with open(X0CoordFileDir, 'w', encoding='utf-8') as file:
        stringCapital = ("测站点,观测方向,左盘方位角,竖直角,距离,测站高,棱镜高, \n")
        X0List = computerX0(X0ObsFileDir)
        for x0 in X0List:
            for xyz in x0:
                file.write(str(xyz) + ",")
            file.write("\n")

def computeOriental(deltaN,deltaE):
    angle = math.atan2(deltaN,deltaE)
    
    if deltaN >= 0 and deltaE >= 0:
        orientl = math.pi / 2 - angle
        print("test... oriental...")
        return orientl 
           
    
    if deltaN >= 0 and deltaE < 0:
        orientl = 5 * math.pi / 2 - angle
        return orientl
    
    if deltaN < 0 and deltaE <= 0:
        return math.pi / 2 - angle
    
    if deltaN < 0 and deltaE >= 0:
        return math.pi / 2 - angle

# #   test...
assert(abs(computeOriental(  math.pow(3, 0.5),   3) -     math.pi / 3) <= 0.000001)     # 第一象限
assert(abs(computeOriental(  math.pow(3, 0.5), - 3) - 5 * math.pi / 3) <= 0.000001)     # 第二象限
assert(abs(computeOriental(- math.pow(3, 0.5), - 3) - 4 * math.pi / 3) <= 0.000001)     # 第三象限
assert(abs(computeOriental(- math.pow(3, 0.5),   3) - 2 * math.pi / 3) <= 0.000001)     # 第四象限

print("test.. oriental computer ok !")

print(math.acos(-0.00168))


        
        
    
    

#  test xa- data....
# p2 = (163.563,130.365,9.965, 0.2713)
# obsValueList = [("L3",2.959526945,1.486640161,76.51619765,1.5644),
#             ("L4",2.925374636,1.480462114,70.43622299,1.446),
#             ("P1",2.485149513,1.568899668,43.37952142,0.2763)]

# L3 = (88.5778, 144.1701, 15.1036, 1.5142)
# obsValueList = [("L1",3.249001156,1.681580305,60.48239689,0.2741),
#             ("L2",2.104850922,1.6339002,103.2164995,0.2697),
#             ("P5",4.965463924,1.710045344,46.06360803,0.2734)]


# for obValue in obsValueList:
#     coord = compute3DXYZ(L3,obValue[1],obValue[2],obValue[3],L3[3],obValue[4])
#     print(obValue[0] + ":" + str(coord))

# test....

X0obsFiledir = "data\\sh20240418-1_04_obsForCoorComputer.txt"
# computerX0(dir)

# generateX0File(X0obsFiledir,"data\\sh20240418-1_05_X0Coord.txt")