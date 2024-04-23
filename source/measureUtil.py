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
# p1 = (0, 0, 0, 1.474)
# obsValueList = [("p2",6.282399666609 ,-0.055154182013 ,23.208185000000,1.522),
#             ("p3",0.744014952392 ,-0.023433226870 ,43.128423250000,1.595),
#             ("P4",1.115438349305 ,-0.033631888669 ,28.280292625000,1.498),
#             ("p5",1.629099858481 ,-0.015237815201 ,14.994933750000,1.463)]

# for obValue in obsValueList:
#     coord = compute3DXYZ(p1,obValue[1],obValue[2],obValue[3],obValue[4])
#     print(obValue[0] + ":" + str(coord))

# test....

X0obsFiledir = "data\\sh20240418-1_04_obsForCoorComputer.txt"
# computerX0(dir)

# generateX0File(X0obsFiledir,"data\\sh20240418-1_05_X0Coord.txt")