import math
from decimal import Decimal

# 不包含重复元素的新列表，同时保持原始列表的顺序
def removeDuplicatesList(lst):
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

# angle tools
#
def dms2degrees(d, m, s):
    """将度分秒转换为十进制度数"""

    degrees = d + (m / Decimal(str(60.0))) + (s / Decimal(str(3600.0)))
    return degrees

def degrees2dms(degrees):
    """将十进制度数转换为度分秒"""
    seconds = int(degrees * 3600) % 60
    minutes = int((degrees * 3600) // 60) % 60
    degrees = int(degrees * 3600) // 3600
    return degrees, minutes, seconds

def dms2radians(d, m, s):
    degrees = dms2degrees(d, m, s)

    """将十进制度数转换为弧度"""
    radians = math.radians(degrees)
    return radians

def radians_to_dms(radians):
    """将弧度转换为十进制度数"""
    degrees =math.degrees(radians)

    dms = degrees2dms(degrees)
    return dms

def extractDmsFromDdmmssStr(ddmmssStr):
    """从dd.mmssss字符串中提取dms"""
    info = ddmmssStr.split(".")
    dd = Decimal(info[0])
    mm = Decimal(info[1][0:2])
    ss = Decimal(info[1][2:4] + "." + info[1][4:])

    return dd, mm, ss

def ddmmssString2radians(ddmmssStr):
    """将 dd.mmssss字符串转化为 弧度 """
    dd, mm, ss = extractDmsFromDdmmssStr(ddmmssStr)

    radians = dms2radians(dd,mm,ss)
    return radians

def ddmmssString2dd(ddmmssStr):
    """将 dd.mmssss字符串转化为 度 """
    dd, mm, ss = extractDmsFromDdmmssStr(ddmmssStr)

    degrees = dms2degrees(dd, mm, ss)
    
    return degrees

def ddmmssString2ss(ddmmssStr):
    """将 dd.mmssss字符串转化为 秒 """
    dd, mm, ss = extractDmsFromDdmmssStr(ddmmssStr)

    seconds = dd * Decimal(str(3600)) + mm * Decimal(str(60.0)) + ss
    return seconds



########## test...........
ddmmssStr = "12.234290"
extractDmsFromDdmmssStr(ddmmssStr)

ddmmssString2radians(ddmmssStr)

ddmmssString2dd(ddmmssStr)

ddmmssString2ss(ddmmssStr)
