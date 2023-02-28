import gsd.hoomd
from mdtrj import Topology

def read_gsd(gsd_fn):
    
    with gsd.hoomd.open(gsd_fn, 'rb') as snaps:
        topo = read_topology(snaps[0])
        coords = read_coords(snaps)
        velos = read_velos(snaps)
    
    return topo, coords, velos

def read_topology(gsd_fn=None, snap=None):

    topo = None
    if snap is None:
        pass
    else:
        topo = Topology()
        topo.bonds = snap.bonds.group
    
def read_coords(gsd_fn=None, snaps=None):
    pass
    
def read_velos(gsd_fn=None, snaps=None):
    pass