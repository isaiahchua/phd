"""
Create the input files (.inp) given the microcantilever dimensions and properties
for running finite element simulations

Code written for use with Abaqus 2019
"""
import os
from math import pi, atan, floor
#import Abaqus libraries
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

materialList = {}
materialList['MSDC_dry'] = [34641.0, 0.25]
materialList['MSDC_wet'] = [29212.0, 0.25]
materialList['Fused Quartz'] = [72000.0, 0.17]
materialList['Fused Quartz 2'] = [72373.08, 0.17]
materialList['MSDC_Dry_2'] = [61100.0, 0.25]
notchList = ['Chevron', 'Straight']
tempName = 'temp'
Wdim = 1
Bdim = 0
crackdim = 3
angledim = 5
a1dim = 8
ddim = 0
Sdim = 1


#Helper functions
def checkPath(wd):
    try:
        os.chdir(wd)
    except:
        print("{0} not a valid path".format(wd))
        raise ValueError


def checkName(name):
    try:
        if isinstance(name, str):
            pass
        else:
            raise TypeError
    except TypeError:
        print("{0} is not a string".format(name))
        raise TypeError


def checkNotch(notch):
    try:
        if isinstance(notch, str):
            pass
        else:
            raise TypeError
        if notch in notchList:
            pass
        else:
            raise ValueError
    except TypeError:
        print("{0} is not a string".format(notch))
        raise TypeError
    except ValueError:
        print("{0} is not in the list".format(notch))
        print("Present list contains the following notch types:")
        print(notchList)
        raise ValueError


def checkMaterial(material):
    try:
        if isinstance(material, str):
            pass
        else:
            raise TypeError
        if material in materialList:
            pass
        else:
            raise ValueError
    except TypeError:
        print("{0} is not a string".format(material))
        raise TypeError
    except ValueError:
        print("{0} is not in the list".format(material))
        print("Present list contains the following material types:")
        print(materialList)
        raise ValueError


def checkGeometries(W, B, a0, a1, L, S, cracklen, crackdiv, d):
    geolist = [W, B, a0, a1, L, S, cracklen, crackdiv, d]
    try:
        for dim in geolist:
            if isinstance(dim, float):
                pass
            else:
                raise TypeError
    except TypeError:
        print("{0} is not a float".format(dim))
        print("If straight notch input 0.0 for a1")
        raise TypeError


def checkinputs(wd, sample, notch, material, W, B, a0, a1, L, S, cracklen, crackdiv, d):
    checkPath(wd)
    checkName(sample)
    checkNotch(notch)
    checkMaterial(material)
    checkGeometries(W, B, a0, a1, L, S, cracklen, crackdiv, d)


def angle(W, B, a0, a1):
    b = (B/2)/W*(W-a1)
    return atan(b/(a1-a0))*180/pi+90


def editDim(sample, notch, material, W, B, a0, a1, L, S, cracklen, d):
    if notch == "Chevron":
        mdb.models.changeKey(fromName=tempName, toName=sample)
        assm = mdb.models[sample].rootAssembly
        mdb.models[sample].sections['CantiSection'].setValues(material=material, 
            thickness=None)
        theta = angle(W, B, a0, a1)
        # Edit W and B dimensions
        mdb.models[sample].ConstrainedSketch(name='__edit__', objectToCopy=
            mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'].sketch)
        mdb.models[sample].parts['Cantilever'].projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models[sample].sketches['__edit__'], upToFeature=
            mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'])
        mdb.models[sample].sketches['__edit__'].dimensions[Wdim].setValues(value=W)
        mdb.models[sample].sketches['__edit__'].dimensions[Bdim].setValues(value=B)
        mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'].setValues(
            sketch=mdb.models[sample].sketches['__edit__'])
        del mdb.models[sample].sketches['__edit__']
        mdb.models[sample].parts['Cantilever'].regenerate()
        # Edit cantilever length
        mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'].setValues(
            depth=L+S)
        mdb.models[sample].parts['Cantilever'].regenerate()
        # Edit Partition face-1
        mdb.models[sample].ConstrainedSketch(name='__edit__', objectToCopy=
            assm.features['Partition face-1'].sketch)
        assm.projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models[sample].sketches['__edit__'], 
            upToFeature=
            assm.features['Partition face-1'])
        mdb.models[sample].sketches['__edit__'].dimensions[angledim].setValues(value=
            theta)
        mdb.models[sample].sketches['__edit__'].dimensions[crackdim].setValues(value=
            cracklen) #note the dimension number would depend on the file used make sure to check before using
        mdb.models[sample].sketches['__edit__'].dimensions[a1dim].setValues(value=
            a1)
        assm.features['Partition face-1'].setValues(
            sketch=mdb.models[sample].sketches['__edit__'])
        del mdb.models[sample].sketches['__edit__']
        # Edit Partition face-2
        mdb.models[sample].ConstrainedSketch(name='__edit__', objectToCopy=
            assm.features['Partition face-2'].sketch)
        assm.projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models[sample].sketches['__edit__'], 
            upToFeature=
            assm.features['Partition face-2'])
        mdb.models[sample].sketches['__edit__'].dimensions[ddim].setValues(value=
            d) #note the dimension number would depend on the file used make sure to check before using
        mdb.models[sample].sketches['__edit__'].dimensions[Sdim].setValues(value=
            S)
        assm.features['Partition face-2'].setValues(
            sketch=mdb.models[sample].sketches['__edit__'])
        del mdb.models[sample].sketches['__edit__']
        assm.regenerate()
    elif notch == "Straight":
        mdb.models.changeKey(fromName=tempName, toName=sample)
        assm = mdb.models[sample].rootAssembly
        mdb.models[sample].sections['CantiSection'].setValues(material=material, 
            thickness=None)
        # Edit W and B dimensions
        mdb.models[sample].ConstrainedSketch(name='__edit__', objectToCopy=
            mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'].sketch)
        mdb.models[sample].parts['Cantilever'].projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models[sample].sketches['__edit__'], upToFeature=
            mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'])
        mdb.models[sample].sketches['__edit__'].dimensions[Wdim].setValues(value=W)
        mdb.models[sample].sketches['__edit__'].dimensions[Bdim].setValues(value=B)
        mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'].setValues(
            sketch=mdb.models[sample].sketches['__edit__'])
        del mdb.models[sample].sketches['__edit__']
        mdb.models[sample].parts['Cantilever'].regenerate()
        # Edit cantilever length
        mdb.models[sample].parts['Cantilever'].features['Solid extrude-2'].setValues(
            depth=L+S)
        mdb.models[sample].parts['Cantilever'].regenerate()
        # Edit Partition face-1
        mdb.models[sample].ConstrainedSketch(name='__edit__', objectToCopy=
            assm.features['Partition face-1'].sketch)
        assm.projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models[sample].sketches['__edit__'], 
            upToFeature=
            assm.features['Partition face-1'])
        mdb.models[sample].sketches['__edit__'].dimensions[0].setValues(value=
            cracklen) #note the dimension number here is zero
        assm.features['Partition face-1'].setValues(
            sketch=mdb.models[sample].sketches['__edit__'])
        del mdb.models[sample].sketches['__edit__']
        # Edit Partition face-2
        mdb.models[sample].ConstrainedSketch(name='__edit__', objectToCopy=
            assm.features['Partition face-2'].sketch)
        assm.projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models[sample].sketches['__edit__'], 
            upToFeature=
            assm.features['Partition face-2'])
        mdb.models[sample].sketches['__edit__'].dimensions[ddim].setValues(value=
            d) #note the dimension number would depend on the file used make sure to check before using
        mdb.models[sample].sketches['__edit__'].dimensions[Sdim].setValues(value=
            S)
        assm.features['Partition face-2'].setValues(
            sketch=mdb.models[sample].sketches['__edit__'])
        del mdb.models[sample].sketches['__edit__']
        assm.regenerate()
        return


def seedCantilever(sample, notch, d):
    if notch == 'Straight':
        seedStraightModel(sample, d)
    if notch == 'Chevron':
        seedChevronModel(sample, d)


def seedChevronModel(sample, d):
    assm = mdb.models[sample].rootAssembly
    edges = assm.sets['edges'].edges
    end1edges0 = assm.sets['end1edges0'].edges
    end2edges0 = assm.sets['end2edges0'].edges    
    end1edges2 = assm.sets['end1edges2'].edges
    end2edges2 = assm.sets['end2edges2'].edges
    end1edges3 = assm.sets['end1edges3'].edges
    end2edges3 = assm.sets['end2edges3'].edges
    edges10 = assm.sets['edges10'].edges
    edges11 = assm.sets['edges11'].edges
    end1edges12 = assm.sets['end1edges12'].edges
    end2edges12 = assm.sets['end2edges12'].edges
    end1edges13 = assm.sets['end1edges13'].edges
    end2edges13 = assm.sets['end2edges13'].edges
    edges14 = assm.sets['edges14'].edges
    #4 node edges
    assm.seedEdgeByNumber(constraint=FIXED, edges=edges
        , number=4)
    #n0
    s = end1edges0[0].getSize() + d
    ratio0 = 5.0*s/(6.0*d)
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FIXED
        , end1Edges=end1edges0
        , end2Edges=end2edges0
        , number=12
        , ratio=ratio0)
    #n3
    l = end1edges3[0].getSize() + s
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FIXED
        , end1Edges=end1edges3
        , end2Edges=end2edges3
        , minSize=s/5.0
        , maxSize=l/6.0)
    #n10 and n11
    n10 = edges10[0].getSize()/(d*5.0)
    if n10 > 5:
        n10 = int(floor(n10))
        assm.seedEdgeByNumber(constraint=FIXED, edges=edges10, 
            number=n10)
    else:
        n10 = 5
        assm.seedEdgeByNumber(constraint=FIXED, edges=edges10, 
            number=n10)
    n11 = edges11[0].getSize()/(d*5.0)
    if n11 > 5:
        n11 = int(floor(n11))
        assm.seedEdgeByNumber(constraint=FIXED, edges=edges11, 
            number=n11)
    else:
        n11 = 5
        assm.seedEdgeByNumber(constraint=FIXED, edges=edges11, 
            number=n11)
    #n2 and n14, same number of seeds as n11
    assm.seedEdgeByNumber(constraint=FIXED, edges=end1edges2 + end2edges2
        , number=n11)
    assm.seedEdgeByNumber(constraint=FIXED, edges=edges14
        , number=n11)
    #n7 and n13, same number of seeds as n3
    n3 = assm.getEdgeSeeds(edge=end1edges3[0], attribute=NUMBER)
    ratio3 = assm.getEdgeSeeds(edge=end1edges3[0], attribute=BIAS_RATIO)
    l = end1edges13[0].getSize() + s
    n3 = assm.getEdgeSeeds(edge=end1edges3[0], attribute=NUMBER)
    ratio13 = 5.0*l/(6.0*s)
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FIXED
        , end1Edges=end1edges13
        , end2Edges=end2edges13
        , number=n3
        , ratio=ratio13)
    #n12, same number of seeds as n10
    assm.seedEdgeByNumber(constraint=FIXED, edges=end1edges12 + end2edges12
        , number=n10)
    assm.seedPartInstance(deviationFactor=0.1, 
        minSizeFactor=0.1, regions=(
        assm.instances['Cantilever-1'], ), size=0.5)


def seedStraightModel(sample, d):
    assm = mdb.models[sample].rootAssembly
    edges = assm.sets['edges'].edges
    end1edges0 = assm.sets['end1edges0'].edges
    end2edges0 = assm.sets['end2edges0'].edges
    edges1 = assm.sets['edges1'].edges
    end1edges2 = assm.sets['end1edges2'].edges
    end2edges2 = assm.sets['end2edges2'].edges
    end1edges3 = assm.sets['end1edges3'].edges
    end2edges3 = assm.sets['end2edges3'].edges
    end1edges4 = assm.sets['end1edges4'].edges
    end2edges4 = assm.sets['end2edges4'].edges
    end1edges5 = assm.sets['end1edges5'].edges
    end2edges5 = assm.sets['end2edges5'].edges
    #Seed 4 seed edges
    assm.seedEdgeByNumber(constraint=FIXED, edges=edges
            , number=4)
    #Seed edges normal to singularity
    l = end1edges0[0].getSize()
    ratio0 = 5.0*(d+l)/(6.0*d)
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FIXED
        , end1Edges=end1edges0
        , end2Edges=end2edges0
        , number=12
        , ratio=ratio0)
    l = edges1[0].getSize()
    n1 = l/(d*10)
    if n1 > 5:
        n1 = int(floor(n1))
        assm.seedEdgeByNumber(constraint=FIXED, edges=edges1, 
            number=n1)
    else:
        n1 = 5
        assm.seedEdgeByNumber(constraint=FIXED, edges=edges1, 
            number=n1)
    #n2&3
    s = end1edges0[0].getSize() + d
    l = end1edges2[0].getSize()
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FINER
        , end1Edges=end1edges2
        , end2Edges=end2edges2
        , minSize=s/5.0
        , maxSize=(l+s)/6.0)
    l = end1edges3[0].getSize()
    n2 = assm.getEdgeSeeds(edge=end1edges2[0], attribute=NUMBER)
    ratio3 = 5.0*(l+s)/(6.0*s)
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FINER
        , end1Edges=end1edges3
        , end2Edges=end2edges3
        , number=n2
        , ratio=ratio3)
    #n4&5
    l = end1edges4[0].getSize()
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FINER
        , end1Edges=end1edges4
        , end2Edges=end2edges4
        , minSize=s/5.0
        , maxSize=(l+s)/6.0)
    l = end1edges5[0].getSize()
    n4 = assm.getEdgeSeeds(edge=end1edges4[0], attribute=NUMBER)
    ratio5 = 5.0*(l+s)/(6.0*s)
    assm.seedEdgeByBias(biasMethod=SINGLE, constraint=FINER
        , end1Edges=end1edges5
        , end2Edges=end2edges5
        , number=n4
        , ratio=ratio5)
    assm.seedPartInstance(deviationFactor=0.1, minSizeFactor=0.1
                          , regions=(assm.instances['Cantilever-1'], )
                          , size=0.5)

def create30sim(sample, notch, cracklen, crackdiv, d):
    ## create 30 new models, changing crack length with remeshing
    if notch == "Straight":
        crackdim = 0
    else:
        crackdim = 3
    for n in range(2, 31):
        m = sample + '-' + str(n)
        cracklen += crackdiv
        mdb.Model(name=m, objectToCopy=mdb.models[sample])
        assm = mdb.models[m].rootAssembly
    # change the crack length and remesh
        mdb.models[m].ConstrainedSketch(name='__edit__', objectToCopy=
            assm.features['Partition face-1'].sketch)
        assm.projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models[m].sketches['__edit__'], 
            upToFeature=
            assm.features['Partition face-1'])
        mdb.models[m].sketches['__edit__'].dimensions[crackdim].setValues(value=
            cracklen) #note the dimension number would depend on the file used make sure to check before using
        assm.features['Partition face-1'].setValues(
            sketch=mdb.models[m].sketches['__edit__'])
        del mdb.models[m].sketches['__edit__']
        assm.regenerate()
        seedCantilever(m, notch, d)
        assm.generateMesh(regions=(
            assm.instances['Cantilever-1'], ))
    # create mesh and rename first model
    seedCantilever(sample, notch, d)
    mdb.models[sample].rootAssembly.seedPartInstance(deviationFactor=0.1, 
        minSizeFactor=0.1, regions=(
        mdb.models[sample].rootAssembly.instances['Cantilever-1'], ), size=0.5)
    mdb.models[sample].rootAssembly.generateMesh(regions=(
            assm.instances['Cantilever-1'], ))
    mdb.models.changeKey(fromName=sample, toName=sample+'-1')


def inpwriter(sample):
    # create 30 jobs from the 30 models and write input files
    for n in range(1, 31): 
        mod = sample + '-' + str(n)
        mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
            explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
            memory=90, memoryUnits=PERCENTAGE, model=mod, modelPrint=OFF, 
            multiprocessingMode=DEFAULT, name=mod, nodalOutputPrecision=SINGLE, 
            numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
            ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
        mdb.jobs[mod].writeInput(consistencyChecking=OFF)


#Main function
def makeinp(wd, sample, notch, material, W, B, a0, a1, L, S, cracklen, crackdiv, d):
    checkinputs(wd, sample, notch, material, W, B, a0, a1, L, S, cracklen, crackdiv, d)
    os.chdir(wd)
    editDim(sample, notch, material, W, B, a0, a1, L, S, cracklen, d)
    create30sim(sample, notch, cracklen, crackdiv, d)
    inpwriter(sample)
        
