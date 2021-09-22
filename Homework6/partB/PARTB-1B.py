# coding:utf-8

from math import log
import operator
import treePlotter
import pandas as pd


def read_dataset(filename):
    labels = ['hair','feathers','eggs','milk','airborne','aquatic','predator','toothed','backbone','breathes','venomous','fins','legs','tail','domestic','catsize','type']
    df = pd.read_csv(filename)
    df = df.drop(columns='1. animal name:')
    dataset = df.values.tolist()
    return dataset, labels


def cal_entropy(dataset):
    numEntries = len(dataset)
    labelCounts = {}
    for featVec in dataset:
        currentlabel = featVec[-1]
        if currentlabel not in labelCounts.keys():
            labelCounts[currentlabel] = 0
        labelCounts[currentlabel] += 1
    Ent = 0.0
    for key in labelCounts:
        p = float(labelCounts[key]) / numEntries
        Ent = Ent - p * log(p, 2)
    return Ent


def splitdataset(dataset, axis, value):
    retdataset = []
    for featVec in dataset:
        if featVec[axis] == value:
            reducedfeatVec = featVec[:axis]
            reducedfeatVec.extend(featVec[axis + 1:])
            retdataset.append(reducedfeatVec)
    return retdataset


def chooseBestFeatureToSplit(dataset,labels):
    numFeatures = len(dataset[0]) - 1
    baseEnt = cal_entropy(dataset)
    bestInfoGain = 0.0
    bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataset]
        uniqueVals = set(featList)
        newEnt = 0.0
        for value in uniqueVals:
            subdataset = splitdataset(dataset, i, value)
            p = len(subdataset) / float(len(dataset))
            newEnt += p * cal_entropy(subdataset)
        infoGain = baseEnt - newEnt
        print(u"The IG for feature %s：%.3f" % (labels[i], infoGain))
        if (infoGain > bestInfoGain):
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature


#Handle the majority class
def majorityCnt(classList):
    classCont = {}
    for vote in classList:
        if vote not in classCont.keys():
            classCont[vote] = 0
        classCont[vote] += 1
    sortedClassCont = sorted(classCont.items(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCont[0][0]


#create the ID3 Tree
def createTree(dataSet,labels):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    if len(dataSet[0]) ==1:
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSplit(dataSet,labels)
    bestFeatLabel = labels[bestFeat]
    print(u"Optimal features：" + (bestFeatLabel) + "\n")
    myTree = {bestFeatLabel:{}}
    del labels[bestFeat]
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitdataset(dataSet,bestFeat,value),subLabels)
    return myTree


if __name__ == '__main__':
    dataset, labels = read_dataset("AnimalData.csv")
    labels_tmp = labels[:]
    ID3desicionTree = createTree(dataset, labels_tmp)
    print('ID3desicionTree:\n', ID3desicionTree)
    treePlotter.ID3_Tree(ID3desicionTree)
