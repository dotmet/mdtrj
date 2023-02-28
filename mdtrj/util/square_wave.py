import copy
import warnings
import numpy as np

def find_sqw_period(a, return_all=False):
    
    if return_all:
        peak_arrs, vall_arrs, npeak_arrs, nvall_arrs = filt_sqw_data(a, full_data=True)
    else:
        npeak_arrs, nvall_arrs = filt_sqw_data(a, count=True, full_data=False)
    _npeak_arrs, _nvall_arrs = copy.deepcopy(npeak_arrs), copy.deepcopy(nvall_arrs)
    
    avgnp, avgnv = np.mean(npeak_arrs), np.mean(nvall_arrs)
    
    for nvp,nvv in zip(_npeak_arrs, _nvall_arrs):
        if nvp <= avgnp/2:
            _npeak_arrs.remove(nvp)
        if nvv <= avgnv/2:
            _nvall_arrs.remove(nvv)
    
    if len(_npeak_arrs)<1 and len(_nvall_arrs)<1:
        warnings.warn('The data may not contain 1 full cycle, return the length of data!')
        return np.sum(npeak_arrs+nvall_arrs)
    else:
        if len(_npeak_arrs)>=5:
            _npeak_arrs = _npeak_arrs[1:-1]
        if len(_nvall_arrs)>=5:
            _nvall_arrs = _nvall_arrs[1:-1]
            
        all_counts = _npeak_arrs + _nvall_arrs
        T = np.mean(all_counts)*2
        
        if return_all:
            return T, _npeak_arrs, _nvall_arrs, peak_arrs, vall_arrs
        else:
            return T

def filt_sqw_data(a, count=True, full_data=False):
    
    peak_arrs = []
    vall_arrs = []
    
    npeak_arrs = []
    nvall_arrs = []
    
    base_val = a[0]
    
    _pal = []
    _val = []
    
    for i,v in enumerate(a):
        
        if v==1:
            _pal.append(i)
        else:
            _val.append(i)
            
        if v!=base_val:

            if base_val==1:
                peak_arrs.append(_pal)
                npeak_arrs.append(len(_pal))
                _pal = []
            else:
                vall_arrs.append(_val)
                nvall_arrs.append(len(_val))
                _val = []
            base_val = v
    if full_data:
        return peak_arrs, vall_arrs, npeak_arrs, nvall_arrs
    else:
        if count:
            return npeak_arrs, nvall_arrs
        else:
            return peak_arrs, vall_arrs