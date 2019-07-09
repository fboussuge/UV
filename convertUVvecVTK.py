from OCC.Core.BRep import BRep_Tool
from QUBPythonoccUtils.OCCD_Basic import read_step_file, ask_point_normal_face, xyz_from_uv_face, ask_point_uv2, ask_point_uv, face_extreme, xyz_from_uv_face_unnormlized
import meshio
import numpy as np

sf = 1000.0

#read vtu file containing the vector field in UV coordinates
mesh = meshio.read('/home/flavien/0-WORK/RESULTS/cyl_face3_u_cross0000000.vtu')

print(mesh.points)
#print(mesh.cells)
#print(mesh.point_data)
#print(mesh)


#read the step file to get the corresponding face
topo = read_step_file('../../../../DATA/SALOME/cyl_face3.step')

faces = [x for x in topo.faces()]
face = faces[0]


#read the text file containing the XYZ coordinates of the nodes
with open('/home/flavien/0-WORK/DATA/SALOME/cyl_face3.txt', 'r') as f:
    lines = f.read().splitlines()

lxyz = []
for line in lines:
    spline = line[1:-1].split(', ')
    #print(spline)
    lxyz.append((float(spline[1]), float(spline[2]), float(spline[3])))


# calculate the vector in 3D projected on the plane tangent the face at the node

uvrange = face_extreme(face)
surface = BRep_Tool.Surface(face)  ### Handle_Geom_Surface
geom_surface = surface.GetObject()
tol = 0.001

ur = uvrange[1] - uvrange[0]
vr = uvrange[3] - uvrange[2]

ndata = []
for i, pt_data in enumerate(mesh.point_data['f_59']):
    pt1_2d = mesh.points[i]
    #print("pt1_2d")
    #print(pt1_2d)
    pt1_3d = lxyz[i]
    #print("pt1_3d")
    #print(pt1_3d)
    n = ask_point_normal_face((pt1_2d[0]*ur, pt1_2d[1]*vr), face)
    n_neg = (-n[0], -n[1], -n[2])
    #print("test")
    pt2_2d = [(pt1_2d[0] + pt_data[0]/1000)*ur, (pt1_2d[1] + pt_data[1]/1000)*vr]
    #print(pt2_2d)
    #if pt2_2d[0] < uvrange[0]:
    #    pt2_2d[0] = pt2_2d[0] + geom_surface.UPeriod()
    #if pt2_2d[0] > uvrange[1]:
    #    pt2_2d[0] = pt2_2d[0] - geom_surface.UPeriod()
    #print("pt2_2d")
    #print(pt2_2d)
    pt2_3d = xyz_from_uv_face_unnormlized(pt2_2d, face)
    pt2_3d = ((pt2_3d.X()/sf, pt2_3d.Y()/sf, pt2_3d.Z()/sf))
    #print("pt2_3d")
    #print(pt2_3d)

    #debug
    #print("aaaa")
    #print(ask_point_uv((83239.0, 55430.0, 172440.0), face, uvrange))
    #print(ask_point_uv2((83239.0, 55430.0, 172440.0), face))
    #print(2.0*ur)
    #tet = xyz_from_uv_face_unnormlized((6.28318530718, 0.0), face)
    #print((tet.X(), tet.Y(), tet.Z()))
    #print(uvrange)


    v_3d = (pt2_3d[0]-pt1_3d[0], pt2_3d[1]-pt1_3d[1], pt2_3d[2]-pt1_3d[2])
    dist = v_3d[0]*n_neg[0] + v_3d[1]*n_neg[1] + v_3d[2]*n_neg[2]
    pt3_3d = (pt2_3d[0]-dist*n_neg[0], pt2_3d[1]-dist*n_neg[1], pt2_3d[2]-dist*n_neg[2])
    npt_data = (pt3_3d[0]-pt1_3d[0], pt3_3d[1]-pt1_3d[1], pt3_3d[2]-pt1_3d[2])
    #print(npt_data)
    ndata.append(npt_data)

    #break

    #pt1_3d =
    #print(pt_data)

for x in ndata:
    print(x)

#print(ndata)
mesh.point_data['f_59'] = np.array(ndata)
for i,elt in enumerate(lxyz):
    mesh.points[i] = np.array(elt)

#print(mesh.points)

meshio.write('/home/flavien/0-WORK/RESULTS/toto.vtk', mesh)

#xyz = xyz_from_uv_face([5.834386356666759, 0.0], face)
#print("toto")
#print(xyz.Coord())