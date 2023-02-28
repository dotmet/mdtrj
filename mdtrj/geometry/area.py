from pypolymer.util import geometry_approximate

import numpy as np

from mdtrj.geometry.rcm import compute_rcm

def geometry_construct(trj=None, coords=None, atom_selections=None):

    if isinstance(atom_selections, list) or isinstance(atom_selections, np.ndarray):
        atom_selections = np.array(atom_selections, dtype=int)
    elif isinstance(atom_selections, int):
        if atom_selections>0:
            atom_selections = np.array(list(range(atom_selections)), dtype=int)
        else:
            atom_selections = np.array([])
    else:
        atom_selections = np.array([])
    
    Nvecs = []
    all_coords = []
    
    if trj is not None:
        all_coords = trj.coords
    elif (trj is None) and (coords is not None):
        Nvecs = []
        if coords.ndim == 2:
            all_coords = np.array([coords], dtype=float)
        elif coords.ndim == 3:
            all_coords = np.array(coords, dtype=float)
        else:
            raise ValueError(f'Wrong position data: {coords.shape}, the dimesion must be 2D or 3D')
    else:
        raise ValueError(f'No geometry data provided!')
        
    if len(all_coords) >= 1:
    
        if len(atom_selections)>0:
            for coord in all_coords:
                _coord = coord[atom_selections]
                nvec = geometry_approximate(_coord)
                Nvecs.append(np.squeeze(nvec))
        else:
            print('No atoms selected, this function will do nothing!')
        Nvecs = np.array(Nvecs, dtype=float)
        
    if len(all_coords) == 1:
        return Nvecs[0]
    else:
        return Nvecs
    

def compute_area_3d(trj=None, coords=None, atom_selections=None):
    '''
    Construct the surface of a closed line.
    
    Parameters
    ----------
    trj: MDTrj.trajectory
    
    Returns
    -------
    Areas : 1D Numpy Array
        The surface areas
        
    xyz_Areas : 3D Numpy Array
        The components of projections of surface on each plane.
    '''

    Nvecs = geometry_construct(trj, coords, atom_selections)
    
    Areas = Nvecs[:,-1]
    xyz_Areas = Nvecs[:,3:6]
    
    return Areas, xyz_Areas
    
def compute_normal_vector_3d(trj=None, coords=None, atom_selections=None):
    
    '''
    Construct the surface of a closed line.
    
    Parameters
    ----------
    trj: MDTrj.trajectory
    atom_selections: list
    
    Returns
    -------
    Nvecs: normal vector of all constructed surfaces.
    '''
    
    Nvecs = geometry_construct(trj, coords, atom_selections)
    
    return Nvecs[:, :3]