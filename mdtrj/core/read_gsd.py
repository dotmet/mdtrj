import gsd.hoomd
from mdtrj import Topology
import numpy as np

import warnings

def read_gsd_file(gsd_fn, read_velo=False, start=0, end=None, skip=1):

    with gsd.hoomd.open(gsd_fn, 'r') as snaps:
        
        topo = Topology()
        
        if end is None:
            end = len(snaps)
            
        s0 = snaps[0]
        
        bonds, box, atom_types, masses = read_snapshot_topo(s0)
        topo.bonds = bonds
        topo.box = box
        topo.atom_types = atom_types
        topo.masses = masses
        topo.atoms = s0.particles.N
        
        coords = []
        velos = None
        
        if read_velo:
            velos = []
            for snap in snaps[start:end:skip]:
                coords.append(read_snapshot_coords(snap))
                velos.append(read_snapshot_velos(snap))
                
            velos = np.array(velos, dtype=float)
        else:
            for snap in snaps[start:end:skip]:
                coords.append(read_snapshot_coords(snap))
        
        try:
            coords = np.array(coords, dtype=float)
        except:
            k=0
            for i,coord in enumerate(coords):
                if len(coord)==0:
                    k=i
            warnings.warn(f'Some atoms lost, file \n{gsd_fn}\n may be incomplete, please check!')
            coords = np.array(coords[k+1:], dtype=float)
        
        snaps.close()
            
    return coords, velos, topo
    
def read_snapshot_topo(snap):
    
    bonds = np.zeros(snap.bonds.group.shape)
    box = np.zeros(snap.configuration.box.shape)
    atom_typs = 1.0
    masses = 1.0
    
    for i, bond in enumerate(snap.bonds.group):
        bonds[i][0], bonds[i][1] = bond[0], bond[1]
    
    for i, bl in enumerate(snap.configuration.box):
        box[i] = bl
        
    if not isinstance(snap.particles.typeid, np.ndarray):
        atom_typs = snap.particles.typeid
    else:
        atom_typs = np.zeros(snap.particles.typeid.shape)
        for i, at in enumerate(snap.particles.typeid):
            atom_typs[i] = at
    
    if not isinstance(snap.particles.mass, np.ndarray):
        masses = float(snap.particles.mass)
    else:
        masses = np.zeros(snap.particles.mass.shape)
        for i, mass in enumerate(snap.particles.mass):
            masses[i] = mass
    
        if len(np.unique(masses)) == 1:
            masses = float(masses[0])
    
    return bonds, box, atom_typs, masses
    
def read_snapshot_coords(snap):

    coords = snap.particles.position
    _coords = np.zeros(coords.shape)
    _coords[:] = coords[:]
    
    return _coords

def read_snapshot_velos(snap):

    velos = snap.particles.velocity
    _velos = np.zeros(velos.shape)
    _velos[:] = velos[:]
    
    return _velos