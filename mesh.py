import numpy as np

ASCII_FACET = """  facet normal  {face[0]:e}  {face[1]:e}  {face[2]:e}
    outer loop
      vertex    {face[3]:e}  {face[4]:e}  {face[5]:e}
      vertex    {face[6]:e}  {face[7]:e}  {face[8]:e}
      vertex    {face[9]:e}  {face[10]:e}  {face[11]:e}
    endloop
  endfacet"""

def parse(fn, marker_tags = ['UPPER_SIDE','LOWER_SIDE', 'SYMMETRY_FACE', 'TIP']):
    f = open(fn,'rb')

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
    for vertex in inners['UPPER_SIDE']+inners['LOWER_SIDE']+inners['TIP']:
        triangs.append(vertex)
        locs = [0,0,0]
        for idx in vertex:
            locs.extend(locations[idx])
        xyzs.append(locs)

    return np.array(xyzs)

def _build_ascii_stl(facets): 
    """returns a list of ascii lines for the stl file """

    lines = ['solid ffd_geom',]
    for facet in facets: 
        lines.append(ASCII_FACET.format(face=facet))
    lines.append('endsolid ffd_geom')
    return lines

def writeSTL(facets, file_name, ascii=True): 
    """outputs an STL file"""

    f = open(file_name,'w')
    if ascii: 
        lines = _build_ascii_stl(facets)
        f.write("\n".join(lines))
    else: 
        data = _build_binary_stl(facets)
        f.write("".join(data))

    f.close()


facets = parse("mesh_ONERAM6_inv.su2")
writeSTL(facets, "mesh.stl")



