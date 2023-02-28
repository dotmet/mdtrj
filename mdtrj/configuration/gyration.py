
import numpy as np
from numba import njit, prange
from multiprocessing import Pool
import copy

import mdtrj.settings as set

def release_gyration_memory():

    set.gyration_results_collector = {
    'gyration tensor':None,
    'Rg' : None,
    'tan2XG' : None,
    'Asphericity' : None,
    'Acylindericity' : None,
    'Anistropy' : None,
}

def gyration_analyze(trajectory, atom_selections=[], parallel=False, processes=10):

    '''
    
    Parameters
    ----------
    trajectory : mdtrj.trajectory or [mdtrj.trajecotry, ]
        A mdtrj.trajectory object or a list of trajecory.
    atom_selections : list
        The atom ids for gyration analyzing.
    parallel : bool
        Using parallel for calculation.
    processes : int
        Number of processes for parallel.
        
    Returns
    -------
    gyration tensors : list or 3D numpy array
        3D numpy array or a bunch of 3D numpy array
    
    Notice : For less computational costs, all the characteristic parameters
             based on gyration tensors has been calculated in this function.
    '''
    
    results = {}
    for key in set.gyration_results_collector.keys():
        results.update({key:[]})
        
    for key in results.keys():
        results[key] = []
        
    if not isinstance(trajectory, list):
        _results = _perform_gyration_compute(trajectory, atom_selections)
        for key,i in zip(results.keys(), range(len(results.keys()))):
            results[key] = _results[i]
        
    else:
        if np.array(atom_selections, dtype=int).ndim != 2:
            atom_selections = [atom_selections]*len(trajectory)
        if parallel:
            params = []
            for i, trj in enumerate(trajectory):
                params.append([trj, atom_selections[i]])
            with Pool(processes=processes) as pool:
                multi_results = pool.starmap(_perform_gyration_compute, params)
                pool.close()
                pool.join()
        else:
            multi_results = []
            for i, trj in enumerate(trajectory):
                multi_results.append(_perform_gyration_compute(trj, atom_selections[i]))
        
        for res in multi_results:
            for key,i in zip(results.keys(), range(len(results.keys()))):
                results[key].append(res[i])
                
    # set.gyration_results_collector = copy.deepcopy(results)
    # set.gyration_atom_selections = atom_selections
        
    return results

def compute_gyration_tensor(trajectory, atom_selections=[], parallel=False, processes=8):
    ''''A function computes the gyration tensors for a trajectory.'''
    set.gyration_results_collector = gyration_analyze(trajectory, atom_selections, parallel, processes)
    return set.gyration_results_collector['gyration tensor']

def compute_rg(trajectory, atom_selections=[], parallel=False, processes=8):
    '''A function computes the radius of gyration for a trajectory.'''
    return set.gyration_results_collector['Rg']
    
def compute_tan2xg(trajectory, atom_selections=[], parallel=False, processes=8):
    '''A function computes the alignment of gyration tensor for a trajectory.'''
    return set.gyration_results_collector['tan2XG']

def compute_asphericity(trajectory, atom_selections=[], parallel=False, processes=8):
    '''A function computes the asphericity for a trajectory.'''
    return set.gyration_results_collector['Asphericity']
    
def compute_acylindericity(trajectory, atom_selections=[], parallel=False, processes=8):
    '''A function computes the acylindericity for a trajectory.'''
    return set.gyration_results_collector['Acylindericity']

def compute_anistropy(trajectory, atom_selections=[], parallel=False, processes=8):
    '''A function computes the anistropy for a trajectory.'''
    return set.gyration_results_collector['Anistropy']


def _perform_gyration_compute(trajectory, atom_selections=[]):
    '''Compute the gyration tensor of polymer
    
    Parameters:
    trajectory : mdtrj.Trajectory
    atom_selections : 1d Numpy Array, optional
        If selections are not sepcified, the whole polymer will be considered.
    
    Returns:
    results : list
        A collelection of gyration analysis results along trajectory.
    '''
    results = []
    
    coords = []
    
    if len(atom_selections) != 0:
        atom_selections = np.array(atom_selections, dtype=int)

        for crd in trajectory.coords:
            coords.append(crd[atom_selections])
            
        coords = np.array(coords, dtype=float)
    
    else:
        coords = trajectory.coords
   
    results = list(_cal_gyra_full(coords)) 
    
    for i in range(len(results)):
        results[i] = np.array(results[i], dtype=float)
        
    return results

# @njit(cache=True)
def _cal_gyra_full(coords):

    ''''A function calculates the gyrations of a trajectory.
    
    Parameters
    ----------
    coords : 3D numpy array
        First dimension must be the time line.
        
    Returns
    -------
    gyrations : 3D numpy array
        Gyration tesnors.
    Rgs : 1D Numpy array
        Radius of gyration tensors.
    tan2XGs : 3D numpy array
        Alignment of gyration tensors at three dimension.
    asphers : 1D Numpy array
        Asphericity of gyration tensors.
    acylinds : 1D Numpy array
        Acylindricity of gyrations tensors.
    anisos : 1D Numpy array
        Anistropy of gyration tensors.
    '''

    nsteps = coords.shape[0]
    
    gyrations = np.zeros((nsteps, 3, 3))
    Rgs = np.zeros(nsteps)
    tan2XGs = np.zeros((nsteps, 3))
    asphers = np.zeros(nsteps)
    acylinds = np.zeros(nsteps)
    anisos = np.zeros(nsteps)
    
    # for step_id in prange(coords.shape[0]):
    for step_id in range(coords.shape[0]):
        coords_i = coords[step_id]
        res = _cal_gyra(coords_i)
        
        gyrations[step_id] = res[0]
        Rgs[step_id] = res[1]
        tan2XGs[step_id] = res[2]
        asphers[step_id] = res[3]
        acylinds[step_id] = res[4]
        anisos[step_id] = res[5]
    
    return gyrations, Rgs, tan2XGs, asphers, acylinds, anisos
        
    
@njit(cache=True)
def _cal_gyra(coords):
    '''Calculate gyration of polymer at specific step.
    
    Parameters:
        coords : 2D Numpy array
        
    Returns:
        gyration : 2D [3x3] numpy array.
    '''
    
    gyration = np.zeros((3,3)) # Gyration tensor
    Rg = 0.0 # Radius of gyration tensor
    tan2XG = np.zeros(3) # Alignment angle of gyration tensor
    b = 0.0 # Asphericity
    c = 0.0 # Acylindricity
    k_sq = 0.0 # Anisotropy 
    
    rcm = np.sum(coords, axis=0)/coords.shape[0]
    r_to_rcm = coords - rcm
    
    for atom_id in prange(coords.shape[0]):
        for i in prange(3):
            for j in prange(3):
                vec = r_to_rcm[atom_id]
                gyration[i, j] += vec[i]*vec[j]
                
    gyration = gyration/coords.shape[0]
    
    gxx, gyy, gzz = gyration[0,0], gyration[1,1], gyration[2,2]
    gxy, gxz, gyz = gyration[0,1], gyration[0,2], gyration[1,2]
    tan2XG[0] = 2*gxy/(gxx-gyy)
    tan2XG[1] = 2*gxz/(gxx-gzz)
    tan2XG[2] = 2*gyz/(gyy-gzz)
    
    ex, ey, ez = np.sort(np.linalg.eigvals(gyration))
    Rg_sq = ex + ey +ez
    Rg = np.sqrt(Rg_sq)
    
    b = ez - (ex + ey)/2
    c = ey - ex
    k_sq = (b*b + (3/4)*c*c)/(Rg_sq*Rg_sq)

    return gyration, Rg, tan2XG, b, c, k_sq
    
            
    