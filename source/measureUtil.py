import math

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
    deltaZ = SDist * math.sin(Vertical) + (stationHt - refHt)

    distHorizontal = SDist * math.cos(Vertical)

    deltaX = distHorizontal * math.cos(Hz)
    deltaY = distHorizontal * math.sin(Hz)

    X2 = X1 + deltaX
    Y2 = Y1 + deltaY
    Z2 = Z1 + deltaZ

    return (X2,Y2,Z2)

#  test....
p1 = (0, 0, 0, 1.474)
obsValueList = [("p2",6.282399666609 ,-0.055154182013 ,23.208185000000,1.522),
            ("p3",0.744014952392 ,-0.023433226870 ,43.128423250000,1.595),
            ("P4",1.115438349305 ,-0.033631888669 ,28.280292625000,1.498),
            ("p5",1.629099858481 ,-0.015237815201 ,14.994933750000,1.463)]

for obValue in obsValueList:
    coord = compute3DXYZ(p1,obValue[1],obValue[2],obValue[3],p1[3],obValue[4])
    print(obValue[0] + ":" + str(coord))
