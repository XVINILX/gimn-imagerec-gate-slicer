from gimnREC.reconstruction.backprojectors import *
from gimnREC.reconstruction.projectors import *
from gimnREC.reconstruction.normalizer import *
from gimnREC.reconstruction.filters import *
from scipy.ndimage import gaussian_filter

"""

    Here we have the mlem, osem and fbp reconstructor written as functions for fast delivery

"""



def mlem(sinogram,iterations,interpolador,angles):
    """

        Reconstructs the sinogram using the Maximum likelihood expectation maximization algorithm for a given number of iterations.\n
        This reconstruction is done using the rotations of the "reconstructed image" in order to obtain the projections.\n
        We must provide as inputs:\n
            * iterations = number of iterations\n
            * interpolation = interpolator to be used, it can be : linear_interpolation, beta_spline_interpolation, bilinear_interpolation and beta_spline_interpolation_o5
            * angles = The input parameter angles will be a angles = np.linspace(0,angle_in_radians,number_of_angles)
    """
    pixels = sinogram.shape[0]
    total = sinogram.sum()
    sinogram = (sinogram/sinogram.max())*total
    imagem_estimada = np.ones([pixels,pixels])
    for it in range (iterations):
        imagem_estimada = np.nan_to_num(gaussian_filter(imagem_estimada,0.1),copy=True,nan=1)
        proje_estimada = radon_m(imagem_estimada,angles,interpolador)
        diff =sinogram/proje_estimada
        imagem_estimada = iradon_m(diff,interpolador)*imagem_estimada
        
    imagem_estimada = (imagem_estimada/imagem_estimada.max())*total
    
    return imagem_estimada


def osem(sinogram,iterations,subsets_n,interpolador,angles):
    """

        Reconstructs the sinogram using the Ordered Subset Expectation Maximization algorithm for a given number of iterations.\n
        This reconstruction is done using the rotations of the "reconstructed image" in order to obtain the projections.\n
        We must provide as inputs:\n
            * iteratinos = number of iterations\n
            * subsets_n  = number of subsets\n
            * interpolation = interpolator to be used, it can be : linear_interpolation, beta_spline_interpolation, bilinear_interpolation and beta_spline_interpolation_o5
            * angles = The input parameter angles will be a angles = np.linspace(0,angle_in_radians,number_of_angles)
    
    """


    pixels = sinogram.shape[0]
    
    total = sinogram.sum()
    pixel_maximum = sinogram.max()
    pixel_minimum = sinogram.min()
    number_of_pixels =1 
    for dim in sinogram.shape:
        number_of_pixels*=dim
        
    pixel_mean = total/number_of_pixels
    

    angles_subset = np.array_split(angles,subsets_n)
    subsets =  np.array_split(sinogram, subsets_n,axis=1)
    reconstruction = np.ones([pixels,pixels])
    
    for it in range (iterations):
        reconstruction = (reconstruction/reconstruction.max())*pixel_mean
        for i,subset in enumerate(subsets):
            rec_sub = projector(reconstruction,angles_subset[i],interpolador)
            coef = subset/rec_sub
            coef = np.nan_to_num(coef,copy=True,nan=0)
            reconstruction *= np.nan_to_num((backprojector(coef,angles_subset[i],interpolador)),copy=True,nan=1)
            #reconstruction = gaussian_filter(reconstruction,0.01)
            
    return reconstruction


def fbp(sinogram,interpolador,filter_type):
    filtered = apply_filter_to_sinogram(filter_type,sinogram)
    return iradon_m(filtered,interpolador)
    

def slice_n(sinograma):
    slice_count = np.zeros(sinograma.shape[0])
    for slice_sino in range(sinograma.shape[0]):
        slice_count[slice_sino]=sinograma[slice_sino].sum()
    return slice_count