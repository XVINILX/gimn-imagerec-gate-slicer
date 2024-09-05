import numpy as np
from scipy.fft import rfft

def rot_center(thetasum):
    """
    Calculates the center of rotation of a sinogram.

    Parameters
    ----------
    thetasum : array like
        The 2-D thetasum array (z,theta).

    Returns
    -------
    COR : float
        The center of rotation.
    """
    T = rfft(thetasum.ravel())
    # Get components of the AC spatial frequency for axis perpendicular to rotation axis.
    imag = T[thetasum.shape[0]].imag
    real = T[thetasum.shape[0]].real
    # Get phase of thetasum and return center of rotation.
    phase = np.arctan2(imag*np.sign(real), real*np.sign(real)) 
    COR = thetasum.shape[-1]/2-phase*thetasum.shape[-1]/(2*np.pi)

    return COR