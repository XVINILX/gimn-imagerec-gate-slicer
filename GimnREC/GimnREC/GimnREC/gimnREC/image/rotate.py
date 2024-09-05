import numpy as np
from scipy.ndimage import rotate as rt_scipy
from numba import njit
import matplotlib.pyplot as plt
import scipy.fft as fft
import itk
from itk import BSplineInterpolateImageFunction


def rotate_itk(imagenp,angle):
    """
    
    uses itk to rotate an image
    
    """
    # ler a imagem de entrada
    input_image = itk.image_view_from_array(imagenp)


    # definir o centro da rotação
    center = (input_image.shape[0] // 2, input_image.shape[1] // 2)

    # definir o ângulo de rotação (em graus)


    # criar o transformador de rotação
    rotation_transform = itk.Euler2DTransform.New()
    rotation_transform.SetCenter(center)
    rotation_transform.SetRotation(angle * np.pi / 180)

    # criar o interpolador de imagem
    interpolator = itk.LinearInterpolateImageFunction.New(input_image)


    #interpolator = BSplineInterpolateImageFunction.New(input_image)
    #interpolator.SetSplineOrder(1) # Define a ordem do spline
    #interpolator.

    
    # criar o filtro de rotação
    rotation_filter = itk.ResampleImageFilter.New(input_image)
    rotation_filter.SetTransform(rotation_transform)
    rotation_filter.SetInterpolator(interpolator)
    rotation_filter.SetOutputSpacing(input_image.GetSpacing())
    rotation_filter.SetOutputOrigin(input_image.GetOrigin())
    rotation_filter.SetOutputDirection(input_image.GetDirection())
    rotation_filter.SetSize(input_image.GetLargestPossibleRegion().GetSize())
    rotation_filter.Update()
    
    # obter a imagem de saída
    output_image = rotation_filter.GetOutput()
    
    return itk.array_from_image(output_image)



def rotate_scipy(image,angle):
    """
    uses scipy to rotate an image for a given angle
    """
    return rt_scipy(image,angle)


def rotate(image, angle, interpolation_func,center=None,channels=False):
    """
    rotate an image for a given angle, using a certain interpolation function;
    the center is at Center, and channels stand for RGB
    """
    # Converts the rotation angle into radiCalcular o centro da imagemans
    theta = angle

    # Obtains the image shape
    height, width = image.shape[:2]

    if center is None:
        # Calculates the image_center 
        center_x = (width // 2)-1
        center_y = (height// 2)-1
    else:
        center_x = center[0]
        center_y = center[1]

    # Calcular a matriz de transformação de rotação
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    rotation_matrix = np.array([[cos_theta, -sin_theta],
                                [sin_theta, cos_theta]])

    # Criar uma grade de coordenadas para a nova imagem rotacionada
    x_coords = np.arange(width)
    y_coords = np.arange(height)
    x_mesh, y_mesh = np.meshgrid(x_coords, y_coords, indexing='xy')
    coords = np.stack([x_mesh, y_mesh], axis=-1)
    transformed_coords = np.dot(coords - np.array([center_x, center_y]), rotation_matrix.T) + np.array([center_x, center_y])
    
    if channels:
        rotated = interpolate_channels(image,transformed_coords,interpolation_func)
    else:
        rotated = interpolate(image,transformed_coords,interpolation_func)
    return rotated


@njit
def interpolate(image,transformed_coords,interpolation_func):
    """
    Interpolate the values using a given function
    """
    height, width = image.shape[:2]
    # Extrae as coordenadas x e y transformadas
    transformed_x = transformed_coords[..., 0]
    transformed_y = transformed_coords[..., 1]
    

    # Aplica a função de interpolação para obter os valores dos pixels na imagem rotacionada
    rotated_image = np.zeros_like(image)
    for y in range(height):
        for x in range(width):
            src_x = transformed_x[y, x]
            src_y = transformed_y[y, x]

            x0 = int(src_x)
            y0 = int(src_y)

            # Calcula as coordenadas dos pixels vizinhos
            x1 = x0 + 1
            y1 = y0 + 1

            # Calcula as diferenças entre as coordenadas
            dx = src_x - x0
            dy = src_y - y0

            # Obtem os valores dos pixels vizinhos
            pixel00 = image[max(0, min(height - 1, y0)), max(0, min(width - 1, x0))]
            pixel01 = image[max(0, min(height - 1, y0)), max(0, min(width - 1, x1))]
            pixel10 = image[max(0, min(height - 1, y1)), max(0, min(width - 1, x0))]
            pixel11 = image[max(0, min(height - 1, y1)), max(0, min(width - 1, x1))]

            # Calcula o valor interpolado
            interpolated_value = interpolation_func(pixel00, pixel01, pixel10, pixel11, dx, dy)

            rotated_image[y, x] = interpolated_value

    return rotated_image


def interpolate_channels(image,transformed_coords,interpolation_func):
    """
    execute the interpolation but using RGB channels
    
    """
    height, width = image.shape[:2]
    # Extrair as coordenadas x e y transformadas
    transformed_x = transformed_coords[..., 0]
    transformed_y = transformed_coords[..., 1]
    
    if (len(image.shape)>2):
        count = image.shape[2]
    else:
        count =1
    # Aplica a função de interpolação para obter os valores dos pixels na imagem rotacionada
    rotated_image = np.zeros_like(image)
    for channel in range(count):
        for y in range(height):
            for x in range(width):
                src_x = transformed_x[y, x]
                src_y = transformed_y[y, x]

                x0 = int(src_x)
                y0 = int(src_y)

                # Calcula as coordenadas dos pixels vizinhos
                x1 = x0 + 1
                y1 = y0 + 1

                # Calcula as diferenças entre as coordenadas
                dx = src_x - x0
                dy = src_y - y0

                # Obtem os valores dos pixels vizinhos
                pixel00 = image[max(0, min(height - 1, y0)), max(0, min(width - 1, x0)), channel]
                pixel01 = image[max(0, min(height - 1, y0)), max(0, min(width - 1, x1)), channel]
                pixel10 = image[max(0, min(height - 1, y1)), max(0, min(width - 1, x0)), channel]
                pixel11 = image[max(0, min(height - 1, y1)), max(0, min(width - 1, x1)), channel]

                # Calcula o valor interpolado
                interpolated_value = interpolation_func(pixel00, pixel01, pixel10, pixel11, dx, dy)

                rotated_image[y, x, channel] = interpolated_value

    return rotated_image