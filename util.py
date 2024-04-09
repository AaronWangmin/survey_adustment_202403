
# 不包含重复元素的新列表，同时保持原始列表的顺序
def removeDuplicatesList(lst):
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]