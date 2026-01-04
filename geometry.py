from rocketisp.geometry import Geometry
import numpy as np


def get_A(G):
    """Extract area function from rocketisp Geometry object."""
    noz = G.getNozObj()
    zL = [-G.Lcham] + noz.abs_zContour
    rL = [G.Dinj/2.0] + noz.abs_rContour
    
    # Use numpy's interp function for linear interpolation
    # Note: zL must be sorted for numpy.interp
    z_array = np.array(zL)
    r_array = np.abs(rL)  # Take absolute value for radius
    
    # Ensure arrays are sorted by z (they should already be, but just in case)
    sort_idx = np.argsort(z_array)
    z_sorted = z_array[sort_idx]
    r_sorted = r_array[sort_idx]
    
    # Create area function using numpy.interp
    A = lambda x: np.pi * (np.interp(x, z_sorted, r_sorted))**2
    
    xmin = zL[0]
    xmax = zL[-1]
    return A, xmin, xmax


def get_parabolic_A(a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0):
    """
    Create a simple parabolic area profile: A(x) = a*(x-b)^2 + c
    
    Parameters:
    -----------
    a : float
        Coefficient for the quadratic term
    b : float
        Horizontal shift (throat location)
    c : float
        Minimum area (throat area)
    xmin : float
        Minimum x coordinate
    xmax : float
        Maximum x coordinate
    
    Returns:
    --------
    A : function
        Area function A(x)
    xmin : float
        Minimum x coordinate
    xmax : float
        Maximum x coordinate
    """
    A = lambda x: a * (x - b)**2 + c
    return A, xmin, xmax
