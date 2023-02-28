import numpy as np
from numba import njit, prange

from multiprocessing import Pool

def compute_distance(trajectory, atom_pairs=None, parallel=False, procs=10):
    '''Compute the distance of two points along trajectory(s)
    
    Parameters
    ----------
    trajectory : mdtrj.trajectory or [mdtrajectory, ]
    atom_pairs : 2D list or 2D numpy array
    parallel : bool
    procs : int
    
    Returns
    -------
    distances : a list with len(atom_pairs) distances list
    '''
    distances = []
    if isinstance(trajectory, list):
        if parallel:
            params = []
            for i in range(len(trajectory)):
                params.append([trajectory[i], atom_pairs])
            with Pool(processes=procs) as pool:
                distances = pool.starmap(_compute_distance, params)
                pool.close()
                pool.join()
        else:
            for trj in trajectory:
                distances.append(_compute_distance(trj, atom_pairs))
    
    else:
        distances = _compute_distance(trajectory, atom_pairs)
        
    _distances = np.array(distances, dtype=float)
    
    distances = []
    for i in range(len(atom_pairs)):
        distances.append(_distances[:,i])
        
    return distances
    
def _compute_distance(trajectory, pairs):
    '''Perform distance computation
    
    Parameters
    ----------
    trajectory : mdtrj.trajectory
    pairs : 2D list
    
    Returns
    -------
    distances : 1D list with len(paris) 1d array
    '''
    
    distances = []
    if trajectory.is_iterator:
        for coords in trajectory.coords:
            dist = []
            for pair in pairs:
                dist.append(np.linalg.norm(coords[pair[0]]-coords[pair[1]]))
            distances.append(dist)
    else:
        pairs = np.array(pairs, dtype=int)
        coords = np.array(trajectory.coords, dtype=float)
        distances = _compute_distance_all(coords, pairs)
 
@njit(cache=True)   
def _compute_distance_all(coords, pairs):
    '''
    A function calculates all distance use numba
    '''
    nsteps = coords.shape[0]
    npairs = pairs.shape[0]
    distances = np.zeros((nsteps, npairs))
    for i in prange(nsteps):
        for j in prange(npairs):
            distances[i][j] = np.linalg.norm(coords[i][pairs[j][0]]- coords[i][pairs[j][1]])
    
    return distances