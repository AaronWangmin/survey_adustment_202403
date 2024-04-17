import math
from decimal import Decimal
from enum import Enum


# 不包含重复元素的新列表，同时保持原始列表的顺序
def removeDuplicatesList(lst):
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

# angle tools
#

# 定义角度的枚举类型
class AngleType(Enum):
    radians = 0
    degrees = 1
    seconds = 2
    dms = 3    

class Angle():
    def __init__(self,value = 999999,angleType = AngleType.radians) -> None:
        self.value = value
        self.angleType = angleType
        pass  

    def dms2degrees(self):
        if self.angleType == AngleType.dms:       
            d = self.value[0]
            m = self.value[1]
            s = self.value[2]

            degrees = d + (m / 60.0) + (s / 3600.0)

            self.value = degrees
            self.angleType = AngleType.degrees
            return self
        else:
            print(str(self.value) + "  : Error: angle type is not dms")       

    def degrees2dms(self):
        if self.angleType == AngleType.degrees:
            degrees = self.value            

            dd = int(degrees)
            mm = int((degrees - dd) * 60.0) 
            ss = ((degrees - dd) * 60 - mm) * 60.0

            self.value = (dd, mm, ss)
            self.angleType = AngleType.dms  
            return self
        else:
            print(str(self.value) + "  : Error: angle type is not degrees")      

    def degrees2radians(self):
        if self.angleType == AngleType.degrees:            
            radians = math.radians(self.value)

            self.angleType = AngleType.degrees
            self.value = radians 
            return self
        else:
            print(str(self.value) + "  : Error: angle type is not degrees")   
    
    def dms2seconds(self):
        if self.angleType == AngleType.dms:
            self.angleType = AngleType.seconds
            self.value = self.value[0] * (3600.0) + self.value[1] * (60.0) + self.value[2]  
            return self           
        else:            
            print(str(self.value) + "  : Error: angle type is not seconds") 


    def dms2radians(self):
        if self.angleType == AngleType.dms:
            self.dms2degrees()

            """将十进制度数转换为弧度"""
            radians = math.radians(self.value)

            self.value = radians
            self.angleType = AngleType.radians 
            return self       
        else:
            print(str(self.value) + "  : Error: angle type is not dms")  

    def seconds2radians(self):
        if self.angleType == AngleType.seconds:  
            degrees = self.value / (3600.0)

            self.value = degrees
            self.angleType = AngleType.degrees

            self.degrees2radians()
            return self
        else:
            print(str(self.value) + "  : Error: angle type is not seconds")

   
    def radians2dms(self): 
        if self.angleType == AngleType.radians:      
            degrees = math.degrees(self.value) # 将弧度转换为十进制度数

            self.value = degrees
            self.angleType = AngleType.degrees

            self.degrees2dms()
            return self

        else:
            print(str(self.value) + "  : Error: angle type is not radians") 

    def extractDmsFromDdmmssStr(self,ddmmssStr):
        """从dd.mmssss字符串中提取dms"""
        info = ddmmssStr.split(".")
        dd =   float(info[0])

        if info[0][0] == "-":       
            mm = - float(info[1][0:2])
            ss = - float(info[1][2:4] + "." + info[1][4:])
        else:
            mm = float(info[1][0:2])
            ss = float(info[1][2:4] + "." + info[1][4:])

        self.value = (dd, mm, ss)
        self.angleType = AngleType.dms
        return self       

    def ddmmssString2radians(self,ddmmssStr):
        """将 dd.mmssss字符串转化为 弧度 """
        self.extractDmsFromDdmmssStr(ddmmssStr)        

        self.dms2radians()
        return self

    def ddmmssString2dd(self,ddmmssStr):
        """将 dd.mmssss字符串转化为 度 """
        self.extractDmsFromDdmmssStr(ddmmssStr)

        self.dms2degrees()
        return self


    def ddmmssString2ss(self,ddmmssStr):
        """将 dd.mmssss字符串转化为 秒 """
        self.extractDmsFromDdmmssStr(ddmmssStr)

        dd, mm, ss = self.value

        seconds = dd * (3600.0) + mm * (60.0) + ss

        self.value = seconds
        self.angleType = AngleType.seconds
        return self

    def radians2dmsString(self):
        if self.angleType == AngleType.radians:
            self.radians2dms()

            dmsString = (str(self.value[0]) + "," + str(self.value[1]) + "," + str(self.value[2]))        
            
            self.dms2radians()
            return dmsString
        else:
            print(str(self.value) + "  : Error: angle type is not radians") 

########## angle tools test...........

# 以 ddmmss.sss 测试这个字符串"-180.3030123"

# ddmmssStr = "-180.3030123"

# angle_test = Angle()

# angle_test.extractDmsFromDdmmssStr(ddmmssStr)
# assert float(angle_test.value[0]) == - 180
# assert float(angle_test.value[1]) == - 30
# assert float(angle_test.value[2]) == - 30.123

# angle_test.dms2seconds()
# assert float(angle_test.value) - (- 649830.123) <= 0.001

# angle_test.ddmmssString2dd(ddmmssStr)
# assert float(angle_test.value) == -180.5083675

# angle_test.ddmmssString2ss(ddmmssStr)
# assert float(angle_test.value) == -649830.123

# angle_test.seconds2radians()
# assert float(angle_test.value) == - 180.5083675 * math.pi /180.0

# angle_test.ddmmssString2radians(ddmmssStr)
# assert float(angle_test.value) == - 180.5083675 * math.pi /180.0

# angle_test.radians2dms()
# assert float(angle_test.value[0]) == - 180
# assert float(angle_test.value[1]) == - 30
# assert float(angle_test.value[2]) - (- 30.123) <= 0.001

# print("Angle tools is ok!" )
