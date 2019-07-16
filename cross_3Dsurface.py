# IMPORT
from QUBPythonoccUtils.OCCD_Basic import read_step_file # to read step file
from QUBPythonoccUtils.OCCD_Basic import ask_point_uv, face_extreme # to get uv coordinates
import xml.etree.cElementTree as ET  # to read xml files

# VARIABLES
sf = 1000.0  # scale factor (issue with Salome export)....

#############################################################
####             Generate UV coordinates                #####
#############################################################


def get_face_from_step(stepfile):
    """
    Given a path return first face of the step file
    """
    topo = read_step_file(stepfile)
    faces = [x for x in topo.faces()]
    return faces[0]


def get_nodes_from_salome(meshfile):
    """
    Given a path return the nodes coordinates
    """
    with open(meshfile, 'r') as f:
        lines = f.read().splitlines()
    return lines


def get_uv_coordinates(nodes, face):
    """
    Get the UV coordinates of the nodes projected on the face
    """
    uvrange = face_extreme(face)
    # print("uvrange" + str(uvrange))
    ur = uvrange[1] - uvrange[0]
    vr = uvrange[3] - uvrange[2]
    lex = [] # list of node to return
    for line in nodes:
        spline = line[1:-1].split(', ')
        xyz = (float(spline[1])*sf, float(spline[2])*sf, float(spline[3])*sf)  # apply a scaling factor
        uv = ask_point_uv(xyz, face, uvrange)  # project the point on the face and get the UV coordinates
        uv = (uv[0]/ur, uv[1]/vr)  # scale the face in U and V to get a more uniform mesh

        ex = [spline[0], spline[1], spline[2], spline[3], spline[4], spline[5], str(uv[0]), str(uv[1])]
        lex.append(ex)

    return lex


def export_uv_coordinates(txtfile, luvs):
    """
    Export the list of node with UV coordinates into txt file (for DEBUG)
    """
    with open(txtfile, 'w') as f:  # export to a text file
        for item in luvs:
            f.write("%s\n" % str(item))


def export_uv_coordinates_to_xml(xmlfile, xmlfileexp, luvs):
    """
    Import an xml file of the mesh containing 3D coordinates and export the same mesh with UV coodinates
    """
    dnodes = dict()
    dids = dict()
    i = 0
    for line in luvs:
        dnodes[int(line[0]) - 1] = (line[6], line[7])
        dids[int(line[0]) - 1] = i
        i += 1

    tree = ET.parse(xmlfile)  # read the initial xml file containing the 3D coordinates
    root = tree.getroot()
    mesh = root.getchildren()[0]
    vertices = mesh.getchildren()[0]

    mesh.set('dim', '2')

    # change the coordinates of the vertices
    lvert_to_remove = []
    for vertex in vertices:
        nodeid = int(vertex.get('index'))
        # print(nodeid)
        if nodeid in dnodes:
            u = dnodes[nodeid][0]
            v = dnodes[nodeid][1]
            vertex.set('x', u)
            vertex.set('y', v)
            vertex.attrib.pop('z')
            vertex.set('index', str(dids[nodeid]))
        else:
            lvert_to_remove.append(vertex)
            # parent = m.getparent()

    # remove the non-used vertices
    vertices.set('size', str(len(dnodes)))
    for vertex in lvert_to_remove:
        # print(vertex.attrib)
        vertices.remove(vertex)

    # remove the non-used cells
    cells = mesh.getchildren()[1]
    lcells_to_remove = []
    lcells_to_keep = []
    for triangle in cells:
        # triid = int(triangle.get('index'))
        v0 = int(triangle.get('v0'))
        v1 = int(triangle.get('v1'))
        v2 = int(triangle.get('v2'))
        if (v0 in dnodes) and (v1 in dnodes) and (v2 in dnodes):
            triangle.set('v0', str(dids[v0]))
            triangle.set('v1', str(dids[v1]))
            triangle.set('v2', str(dids[v2]))
            triangle.set('index', str(len(lcells_to_keep)))
            lcells_to_keep.append(triangle)
        else:
            lcells_to_remove.append(triangle)

    cells.set('size', str(len(lcells_to_keep)))
    for triangle in lcells_to_remove:
        cells.remove(triangle)

    tree.write(xmlfileexp)


#############################################################
####     Calculate Cross Fields with Fenics             #####
#############################################################

if __name__ == "__main__":
    # 1_IMPORT THE STEP FILE
    facepath = '../../../../DATA/SALOME/cyl_face19.step'
    face = get_face_from_step(facepath)

    # GET THE MESH NODES
    meshpath = '/home/flavien/0-WORK/DATA/SALOME/cyl_face19_5.txt'
    nodes = get_nodes_from_salome(meshpath)

    # PROJECT NODES TO GET UV COORDINATES
    nodesUV = get_uv_coordinates(nodes, face)

    # EXPORT TO A TXT FILE
    # txtpath = '/home/flavien/0-WORK/DATA/SALOME/cyl_face19_5_m.txt'
    # export_uv_coordinates(txtpath, nodesUV)

    # EXPORT TO XML FILE
    xmlpath = '/home/flavien/0-WORK/DATA/SALOME/cyl_5.xml'
    xmlexportpath = '/home/flavien/0-WORK/DATA/SALOME/cyl_face19_5_m.xml'
    export_uv_coordinates_to_xml(xmlpath, xmlexportpath, nodesUV)
