import numpy as np

def eig(a):
    return np.linalg.eig(a)
    
def max_eig_abs(a):
    eigvals, eigvecs = eig(a)
    return _choose_eig(eigvals, eigvecs, np.max, True)

def min_eig_abs(a):
    eigvals, eigvecs = eig(a)
    return _choose_eig(eigvals, eigvecs, np.min, True)

def max_eig_real(a):
    eigvals, eigvecs = eig(a)
    return _choose_eig(eigvals, eigvecs, np.max, False)

def min_eig_real(a):
    eigvals, eigvecs = eig(a)
    return _choose_eig(eigvals, eigvecs, np.min, False)
    
def _choose_eig(eigval, eigvec, filt_func=np.max, absolute=True):
    '''
    Parameters
    ----------
    eigval : numpy.ndarray
    eigvec : numpy.ndarray
    absolute : bool
        If only consider absolute value of eigen values
    
    Returns
    -------
    eigval : numpy.ndarray
    eigvec : numpy.ndarray
    '''
    
    if absolute:
        eigval_ = np.abs(eigval)
    else:
        eigval_ = eigval
        
    def filt_1dim(eva, eve):
        _eva = filt_func(eva)
        _idx = np.where(eva==_eva)[0][0]
        return _idx, eve[_idx]
        
    if eigval.ndim==1:
        res = filt_1dim(eigval_, eigvec)
        return eigval[res[0]], res[1]
    else:
        _eigvals = []
        _eigvecs = []
        for eval, evec in zip(eigval_, eigvec):
            res = filt_1dim(eval, evec)
            _eigvals.append(eigval[res[0]])
            _eigvecs.append(res[1])
        return np.array(_eigvals, dtype=float), np.array(_eigvecs, dtype=float)
        
    
    