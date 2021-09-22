# R is a set of restrictions
# this functions colors the given province with the given color
# returns false if not possible, returns the set of new restrictions if possible
def addColor(R, province, color):
    ans = []
    for rr in R:
        res = checkRestriction(rr, province, color)
        if res == False:
            return False
        elif res == None:
            continue
        else:
            ans.append(res)
    return ans


# checks if the restrition rr allows the given province to have the given color
# returns false if not possible, otherwise returns the new restriction
def checkRestriction(rr, province, color):
    # finding the index of the province (saved to index)
    index = -1
    other = -1
    if rr[0] == province:
        index = 0
        other = 1
    elif rr[1] == province:
        index = 1
        other = 0
    else:
        return rr

    if isinstance(rr[other], int):
        # other component is a color
        if (color != rr[other]):
            return None
        else:
            return False
    else:
        return [rr[other], color]


# solving the CSP by variable elimination
# recursive structure: ci is the province index to be colored (0 = bc, 1 = ab, etc)
# n is the number of colors
# provinces is a list of provinces
# if coloring is possible returns the province-> color map, otherwise False
# for 3 colors outputs should be like {'ab': 1, 'bc': 2, 'mb': 1, 'nb': 1, 'ns': 2, 'nl': 1, 'nt': 3, 'nu': 2, 'on': 2, 'pe': 3, 'qc': 3, 'sk': 2, 'yt': 1}
def solveCSP(provinces, n, R, colorDic):
   # colorDic = {provinces[0]:None}
    if None not in colorDic.values():
        return colorDic

    # choose a province
    for p in provinces:
        if p not in colorDic:
            colorDic[p] = None
        if colorDic[p] == None:
            province = p

    # color
    for color in range(1, n+1):
        newR = addColor(R, province, color)
        if not newR is False: # No color collision, you're good
            colorDic[province] = color
            result = solveCSP(provinces, n, newR, colorDic)
            if not result is False:
                return result
        colorDic[province] = None # If you hit this, backtrack by setting the (k,v) as None
    return False


# main program starts
# ===================================================

n = 5  # int(input("Enter the number of color"))
colors = []
for i in range(1, n + 1):
    colors.append(i)
# print(colors)

# creating map of canada
# cmap[x] gives the neighbors of the province x
cmap = {}
cmap["ab"] = ["bc", "nt", "sk"]
cmap["bc"] = ["yt", "nt", "ab"]
cmap["mb"] = ["sk", "nu", "on"]
cmap["nb"] = ["qc", "ns", "pe"]
cmap["ns"] = ["nb", "pe"]
cmap["nl"] = ["qc"]
cmap["nt"] = ["bc", "yt", "ab", "sk", "nu"]
cmap["nu"] = ["nt", "mb"]
cmap["on"] = ["mb", "qc"]
cmap["pe"] = ["nb", "ns"]
cmap["qc"] = ["on", "nb", "nl"]
cmap["sk"] = ["ab", "mb", "nt"]
cmap["yt"] = ["bc", "nt"]

# CSP restrictions
# each restriction is modeled as a pair [a,b] which means the province a's
# color is not equal to b, where b is either a color (a number 1 to n) or
# another province. Examples ['bc', 'ab'] means the color of bc should
# not be equal to ab -- ["bc",4] means the color of bc should not be 4
# R is the list of restrictions

R = []

# initiaitiong restrictions based on the province neighborhood

for x in cmap:
    for y in cmap[x]:
        R.append([x, y])

# initiating a list of provinces
provinces = []
for p in cmap:
    provinces.append(p)



while (1):
    num = int(input("Enter number of colors? "))
    colorDic = {provinces[0]:None}
    colorDict = solveCSP(provinces, num, R, colorDic)
    if colorDict == False:
        print("No solution for num",num)
    else:
        print(colorDict)

