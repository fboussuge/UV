from QUBPythonoccUtils.OCCD_Basic import read_step_file, ask_point_uv2, xyz_from_uv_face, ask_point_uv, face_extreme
from OCC.Core.BRep import BRep_Tool

sf = 1000.0
topo = read_step_file('../../../../DATA/SALOME/cyl_face3.step')

faces = [x for x in topo.faces()]
face = faces[0]

uvrange = face_extreme(face)
print("uvrange" + str(uvrange))

surface = BRep_Tool().Surface(face)  ### Handle_Geom_Surface
geom_surface = surface.GetObject()


#print(faces)

#apt = xyz_from_uv_face((0.5,0.5),face)
#print((apt.X(), apt.Y(), apt.Z()))

#xyz = [-85.95321781066448, -51.10816322264448, 45.74832762027226]
#uv = ask_point_uv2(xyz,face)
#print(uv)

#read the text file containing the nodes
with open('/home/flavien/0-WORK/DATA/SALOME/cyl_face3.txt', 'r') as f:
    lines = f.read().splitlines()

ur = uvrange[1] - uvrange[0]
vr = uvrange[3] - uvrange[2]
lex = []
for line in lines:
    spline = line[1:-1].split(', ')
    #print(spline)

    shptype = spline[5]
    if shptype == 'VERTEX' or shptype == 'EDGE' or shptype == 'FACE':
        xyz = (float(spline[1])*sf, float(spline[2])*sf, float(spline[3])*sf)
        uv = ask_point_uv(xyz, face, uvrange)

        uv = (uv[0]/ur, uv[1]/vr)

        print(spline[0])
        print(xyz)
        print(uv)

        ex = [spline[0], spline[1], spline[2], spline[3], spline[4], spline[5], str(uv[0]), str(uv[1])]
    else:
        ex = spline
    lex.append(ex)



    #print(ex)

xyz = xyz_from_uv_face([5.834386356666759, 0.0], face)
print("toto")
print(xyz.Coord())

# export to a text file
with open('/home/flavien/0-WORK/DATA/SALOME/cyl_face3_m.txt', 'w') as f:
    for item in lex:
        f.write("%s\n" % str(item))