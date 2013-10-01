from openmdao.lib.datatypes.api import Str, File, Geom
from openmdao.main.api import Component, Assembly, Variable

from openmdao.main.interfaces import IParametricGeometry, implements, IStaticGeometry


class SU2MeshComp(Component): 

    mesh = Str(iotype="in")

    surface = Geom(IStaticGeometry, iotype="out")

    def execute(self): 
        self.surface = SU2geom()
        #set the surface output to an SU2geom instance
        self.surface.set_fn(self.mesh)



class SU2geom(Variable):

    implements(IStaticGeometry)

    def __init__(self, iotype="out"):
        super(SU2geom, self).__init__(iotype=iotype)

    def set_fn(self, fn):
        self.fn = fn

    def get_visualization_data(self, wv):

        #xyzs = np.array(self.points).flatten().astype(np.float32)
        #tris = np.array(self.triangles).flatten().astype(np.int32)

        xyzs, tris = self.parse(self.fn)

        wv.set_face_data(xyzs.flatten(), tris.flatten(), name="surface")

    def parse(self):
        f = open(self.fn,'rb')

        connections = []
        locations = {}

        connect_done = False

        for line in f:
            if "NDIME" in line:
                ndim = int(line.split("=")[-1].strip())

            elif "NELEM" in line:
                nelem = int(line.split("=")[-1].strip())

            elif "NPOIN" in line:
                npoin = int(line.split("=")[-1].strip())
        f.close()
        f = open(fn,'rb')
        i=1
        for line in f:
            if "=" in line:
                continue
            if i <= nelem:
                data = [int(x) for x in line.split()]
                connections.append(data)
                i+=1
            else:
                break
        f.close()
        f = open(fn,'rb')
        i=1
        for line in f:
            if "=" in line:
                continue
            elif i <= nelem:
                i+=1
            elif i <= nelem + npoin:
                S = line.split()
                idx = int(S[-1])
                data = [float(x) for x in S[:-1]]
                locations[idx] = data
                i+=1
            else:
                break

        f.close()
        f = open(fn,'rb')

        inners = {}
        start, working = False, False
        for line in f:
            if "NMARK" in line:
                nmark = int(line.split("=")[-1].strip())
                start = True
            elif start:
                if "MARKER_TAG" in line:
                    name = line.split()[-1]
                    inners[name] = []
                elif "MARKER_ELEMS" in line:
                    marker_elems = int(line.split("=")[-1])
                else:
                    try:
                        data = [int(x) for x in line.split()[1:]]
                        inners[name].append(data)
                    except:
                        pass
        f.close()
        xyzs = []
        triangs = []
        for vertex in inners['LOWER_SIDE']:
            triangs.append(vertex)
            xyzs.extend([locations[idx] for idx in vertex])
        for vertex in inners['UPPER_SIDE']:
            triangs.append(vertex)
            xyzs.extend([locations[idx] for idx in vertex])

        return xyzs, triangs


