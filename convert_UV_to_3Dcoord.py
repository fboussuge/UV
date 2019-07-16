# from OCC.Core.BRep import BRep_Tool
from QUBPythonoccUtils.OCCD_Basic import read_step_file # to read step file
from QUBPythonoccUtils.OCCD_Basic import ask_point_normal_face, face_extreme, xyz_from_uv_face_unnormlized # to get uv coordinates

# from QUBPythonoccUtils.OCCD_Basic import ask_point_uv2, ask_point_uv
import meshio
import numpy as np

# VARIABLES
sf = 1000.0  # scale factor (issue with Salome export)....

#############################################################
####     Convert UV of vector to 3D coord               #####
#############################################################


def get_face_from_step(stepfile):
    """
    Given a path return first face of the step file
    """
    topo = read_step_file(stepfile)
    faces = [x for x in topo.faces()]
    return faces[0]


def read_vector_result(vtufile):
    """
    Read the vtu file generate by fenics
    """
    # read vtu file containing the vector field in UV coordinates
    mesh = meshio.read(vtufile)
    return mesh


def get_xyz_coordinates(txtfile):
    """
    Read the xyz coordinates from the txt file
    """
    # read the text file containing the XYZ coordinates of the nodes
    with open(txtfile, 'r') as f:
        lines = f.read().splitlines()

    lxyz = []
    for line in lines:
        spline = line[1:-1].split(', ')
        #print(spline)
        lxyz.append((float(spline[1]), float(spline[2]), float(spline[3])))
    return lxyz


def calculate_xyz_from_uv(lxyz, face, mesh, vtkfile):
    """
    Calculate the vector in 3D projected on the plane tangent the face at the node
    """
    # surface = BRep_Tool.Surface(face)  ### Handle_Geom_Surface
    # geom_surface = surface.GetObject()
    # tol = 0.001
    uvrange = face_extreme(face)
    ur = uvrange[1] - uvrange[0]
    vr = uvrange[3] - uvrange[2]

    ndata = []
    ldatakeys = list(mesh.point_data.keys())

    for i, pt_data in enumerate(mesh.point_data[ldatakeys[0]]):
        pt1_2d = mesh.points[i]
        # print("pt1_2d")
        # print(pt1_2d)
        pt1_3d = lxyz[i]
        # print("pt1_3d")
        # print(pt1_3d)
        n = ask_point_normal_face((pt1_2d[0]*ur, pt1_2d[1]*vr), face)
        n_neg = (-n[0], -n[1], -n[2])
        # print("test")
        pt2_2d = [(pt1_2d[0] + pt_data[0]/1000)*ur, (pt1_2d[1] + pt_data[1]/1000)*vr]
        # print(pt2_2d)
        # if pt2_2d[0] < uvrange[0]:
        #     pt2_2d[0] = pt2_2d[0] + geom_surface.UPeriod()
        # if pt2_2d[0] > uvrange[1]:
        #     pt2_2d[0] = pt2_2d[0] - geom_surface.UPeriod()
        # print("pt2_2d")
        # print(pt2_2d)
        pt2_3d = xyz_from_uv_face_unnormlized(pt2_2d, face)
        pt2_3d = ((pt2_3d.X()/sf, pt2_3d.Y()/sf, pt2_3d.Z()/sf))
        # print("pt2_3d")
        # print(pt2_3d)

        # ########## debug
        # print("aaaa")
        # print(ask_point_uv((83239.0, 55430.0, 172440.0), face, uvrange))
        # print(ask_point_uv2((83239.0, 55430.0, 172440.0), face))
        # print(2.0*ur)
        # tet = xyz_from_uv_face_unnormlized((6.28318530718, 0.0), face)
        # print((tet.X(), tet.Y(), tet.Z()))
        # print(uvrange)

        v_3d = (pt2_3d[0]-pt1_3d[0], pt2_3d[1]-pt1_3d[1], pt2_3d[2]-pt1_3d[2])
        dist = v_3d[0]*n_neg[0] + v_3d[1]*n_neg[1] + v_3d[2]*n_neg[2]
        pt3_3d = (pt2_3d[0]-dist*n_neg[0], pt2_3d[1]-dist*n_neg[1], pt2_3d[2]-dist*n_neg[2])
        npt_data = (pt3_3d[0]-pt1_3d[0], pt3_3d[1]-pt1_3d[1], pt3_3d[2]-pt1_3d[2])
        # print(npt_data)
        ndata.append(npt_data)

    # for x in ndata:
        # print(x)

    # print(ndata)
    mesh.point_data['f_10'] = np.array(ndata)  # replace the coordinates in the mesh object
    for i, elt in enumerate(lxyz):
        mesh.points[i] = np.array(elt)

    # print(mesh.points)

    meshio.write(vtkfile, mesh)


if __name__ == "__main__":
    face_ids = [3]  # list of ids of faces
    for faceid in face_ids:
        # 1_IMPORT THE STEP FILE
        facepath = '../../../../DATA/SALOME/cyl_face' + str(faceid) + '.step'
        face = get_face_from_step(facepath)

        # READ THE XYZ coordinates
        txtpath = '/home/flavien/0-WORK/DATA/SALOME/cyl_face' + str(faceid) + '.txt'
        lxyz = get_xyz_coordinates(txtpath)

        # READ THE VTU FILES
        for i in range(0, 4):
            vtupath = '/home/flavien/0-WORK/RESULTS/CYL/cyl_face' + str(faceid) + '_cross' + str(i) + '000000.vtu'
            mesh = read_vector_result(vtupath)

            # CALCULATE XYZ COORDINATES
            vtkpath = '/home/flavien/0-WORK/RESULTS/CYL/cyl_face' + str(faceid) + '_' + str(i) + '.vtk'
            calculate_xyz_from_uv(lxyz, face, mesh, vtkpath)
