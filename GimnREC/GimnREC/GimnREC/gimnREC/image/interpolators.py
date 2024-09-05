from numba import njit
import numpy as np


@njit
def bilinear_interpolation(pixel00, pixel01, pixel10, pixel11, dx, dy):
    """
    implements bilineal interpolation between 4 pixels
    
    """
    top = pixel00 * (1 - dx) + pixel01 * dx
    bottom = pixel10 * (1 - dx) + pixel11 * dx
    interpolated_value = top * (1 - dy) + bottom * dy
    return interpolated_value


@njit
def beta_spline_interpolation(pixel00, pixel01, pixel10, pixel11, dx, dy):
    """
    implements beta spline between 4 pixels
    
    """
    # Coeficientes do beta-spline
    c00 = 1/6 * (-dx**3 + 3*dx**2 - 3*dx + 1)
    c01 = 1/6 * (3*dx**3 - 6*dx**2 + 4)
    c10 = 1/6 * (-3*dx**3 + 3*dx**2 + 3*dx + 1)
    c11 = 1/6 * dx**3

    # Interpolação nas direções x e y
    interp_x_top = pixel00 * c00 + pixel01 * c01
    interp_x_bottom = pixel10 * c10 + pixel11 * c11
    interpolated_value = interp_x_top * (1 - dy) + interp_x_bottom * dy

    return interpolated_value

@njit
def linear_interpolation(pixel00, pixel01, pixel10, pixel11, dx, dy):
    """
    implements LINEAR interpolation between 4 pixels
    
    """
    top = pixel00 * (1 - dx) + pixel01 * dx
    bottom = pixel10 * (1 - dx) + pixel11 * dx
    interpolated_value = top * (1 - dy) + bottom * dy
    return interpolated_value

@njit
def beta_spline_interpolation_o5(pixel00, pixel01, pixel10, pixel11, dx, dy, order=5):
    """
    implements beta spline of order 5 interpolation between 4 pixels
    
    """
    # Coeficientes do Beta-Spline
    if order == 1:
        coeffs = [0.5, 0.5, 0]
    elif order == 2:
        coeffs = [1/6, 4/6, 1/6]
    elif order == 3:
        coeffs = [1/6, 4/6, 1/6]
    elif order == 4:
        coeffs = [1/24, 11/24, 11/24, 1/24]
    elif order == 5:
        coeffs = [1/24, 11/24, 11/24, 1/24]
    else:
        raise ValueError("Ordem do Beta-Spline não suportada.")

    # Interpolação nas direções x e y
    interp_x_top = np.sum(coeffs[i] * np.power(dx, i) for i in range(order + 1))
    interp_x_bottom = np.sum(coeffs[i] * np.power(dx, i) for i in range(order + 1, 2 * order + 1))
    interpolated_value = interp_x_top * (1 - dy) + interp_x_bottom * dy

    return interpolated_value