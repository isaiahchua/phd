# setup viewport
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=294.882293701172, 
    height=230.850006103516)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
import sys
excel_utilities_fp = r'D:\xxxxxxx\excelUtilities'
sys.path.insert(15, excel_utilities_fp) 
import abq_ExcelUtilities.excelUtilities

# setup variables

# open odb and extract data from specified node
def to_excel(sample, node, assembly_name, wd):
    xyDataSet = []
    for n in range(1,31):
        filepath = wd + r'\{0}.odb'.format(sample + '-' + str(n))
        o1 = session.openOdb(name=filepath)
        session.viewports['Viewport: 1'].setValues(displayedObject=o1)
        odb = session.odbs[filepath]
        session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('U', 
            NODAL, ((COMPONENT, 'U2'), )), ), nodeLabels=((assembly_name, (node, )), ))
        if n < 2:
            xyDataSet.append('U:U2 PI: {0} N: {1}'.format(assembly_name, node))
        else:
            xyDataSet.append('U:U2 PI: {0} N: {1}'.format(assembly_name, node + '_' + str(n-1)))
    # export to excel
    xystring = ','.join(xyDataSet)
    abq_ExcelUtilities.excelUtilities.XYtoExcel(xyDataNames=xystring, trueName='')
