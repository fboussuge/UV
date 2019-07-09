import xml.etree.cElementTree as ET

#read the text file containing the nodes with the uv coordinates
with open('/home/flavien/0-WORK/DATA/SALOME/cyl_face3_m.txt', 'r') as f:
    lines = f.read().splitlines()

dnodes = dict()
dids = dict()
i=0
for line in lines:
    spline = line[1:-1].split(', ')
    spline0 = spline[0][1:-1]
    spline6 = spline[6][1:-1]
    spline7 = spline[7][1:-1]
    dnodes[int(spline0)-1] = (spline6, spline7)
    dids[int(spline0)-1] = i
    i+=1

#for key, value in dnodes.items():
#    print((key, value))


#read the xml file and replace the XYZ coordinates by the UV coordinates
xmlfile = '/home/flavien/0-WORK/DATA/SALOME/cyl_face3.xml'


tree = ET.parse(xmlfile)
root = tree.getroot()

mesh = root.getchildren()[0]
vertices = mesh.getchildren()[0]

mesh.set('dim', '2')

# change the coordinates of the vertices
lvertToRemove = []
for vertex in vertices:
    nodeid = int(vertex.get('index'))
    #print(nodeid)
    if nodeid in dnodes:
        u = dnodes[nodeid][0]
        v = dnodes[nodeid][1]
        vertex.set('x', u)
        vertex.set('y', v)
        vertex.attrib.pop('z')
        vertex.set('index', str(dids[nodeid]))
    else:
        lvertToRemove.append(vertex)
        #parent = m.getparent()

#remove the non-used vertices
vertices.set('size', str(len(dnodes)))
for vertex in lvertToRemove:
    #print(vertex.attrib)
    vertices.remove(vertex)

#remove the non-used cells
cells = mesh.getchildren()[1]
lcellsToRemove = []
lcellsToKeep = []
for triangle in cells:
    triid = int(triangle.get('index'))
    v0 = int(triangle.get('v0'))
    v1 = int(triangle.get('v1'))
    v2 = int(triangle.get('v2'))
    if ((v0 in dnodes) and (v1 in dnodes) and (v2 in dnodes)):
        lcellsToKeep.append(triangle)
        triangle.set('v0', str(dids[v0]))
        triangle.set('v1', str(dids[v1]))
        triangle.set('v2', str(dids[v2]))
    else:
        lcellsToRemove.append(triangle)

print(len(lcellsToRemove))

cells.set('size', str(len(lcellsToKeep)))
for triangle in lcellsToRemove:
    #print(vertex.attrib)
    cells.remove(triangle)

tree.write('/home/flavien/0-WORK/DATA/SALOME/cyl_face3_m.xml')