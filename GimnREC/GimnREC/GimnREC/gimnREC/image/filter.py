
import slicer
from numpy import dtype
from copy import deepcopy

import numpy as np
from matplotlib import pyplot as plt
import numpy as np

try:
	from numba import njit
except:
  slicer.util.pip_install('numba')
  from numba import njit

# IMPLEMENTADO NA VERSAO NAO SEPARAVEL # para imagens NÃO RGB

@njit #  <--- decorador do NUMBA. Diz ao numba para complilar esta função. P.s. Utilizar bibliotecas do numpy internamente, outras bibliotecas não aceitas pelo numba
def get_neighbors (imagem,u,v,window ):
  """
  From an image it takes at the pixel u,v, all the neighboors in with a window centered in u,v with size(Window)

  """
  #define a matriz onde serao salvos os vizinhos
  tipo = imagem.dtype
  neighbors = np.zeros((window,window),dtype=tipo)
  x_pos = 0
  y_pos = 0 

  # iteração sobre a matriz gerada 
  # atentar para os limites (window//2) <- divisao inteira por 2 
  # como o range nao pega o ultimo valor soma +1
  for i in range(u-window//2,u+window//2+1):
    x_pos=0
    for j in range(v-window//2,v+window//2+1):
      neighbors[y_pos,x_pos] = imagem[i,j] # pega os valores da matriz original e coloca no vizinho
      x_pos +=1
    y_pos+=1
  return neighbors



# filtro generico, se for desejado gerar um filtro de mediana ou mesmo filtros morfologicos, a logica dos vizinhos deve ser 
# alterada no "AQUI"
@njit  #  <--- decorador do NUMBA. Diz ao numba para complilar esta função. P.s. Utilizar bibliotecas do numpy internamente, outras bibliotecas não aceitas pelo numba
def filtro (kernel,imagem):
  """
  implements a convolutional filter, that aplies an kernel, to an image

  """
  tipo = imagem.dtype
  x_len = imagem.shape[1]
  y_len = imagem.shape[0]
  out = np.zeros((y_len,x_len),dtype=tipo)
  window_y , window_x = kernel.shape
  if window_y is window_x: # checa se o kernel possui as mesmas dimenções em x e em y
    window = window_x
    for i in range(window//2,(y_len-(window//2))):
      for j in range(window//2,(x_len-(window//2))):
        vizinhos=get_neighbors(imagem,i,j,window)
        out[i,j] = ((vizinhos*kernel)/(np.abs(kernel).sum())).sum()      # kernel deve ser do mesmo tamanho de vizinhos para a multiplicacao
        # /\  AQUI                                                         # ele está dividido pelo modulo da soma dos valores do kernel
                                                                           # para garantir normalização
         
  else:
      print("dimensões x e y do kernel não são iguais")
  return out

@njit
def covolve_1d(kernel,vector):
  """
  Applies 1d convolution

  """
  out = np.zeros(vector.shape[0])
  tam_kernel = kernel.shape[0]//2
  for i in range(tam_kernel,vector.shape[0]-tam_kernel):
    neighbors = vector[i-tam_kernel:i+tam_kernel+1]
    out[i] = ((neighbors*kernel).sum())/(np.abs(kernel).sum())
  return out

@njit
def filtro_separavel(kernel_a,kernel_b,imagem):
  """
  Implements a filter in a separable way
  """
  tipo = imagem.dtype
  x_len = imagem.shape[1]
  y_len = imagem.shape[0]
  out = np.ones((y_len,x_len),dtype=tipo)

  for j in range(y_len):
    linha = imagem[j,:]
    out[j,:]= covolve_1d(kernel_b, linha)

  for i in range(x_len):
    coluna = out[:,i]
    out[:,i]= covolve_1d(kernel_a, coluna)

  return out

def gaussian_kernel_norm(n, m, sigma):
    """
    generates 2D  gaussian kernel centered at the pixel, n,m , and with standard deviation sigma
    
    """
    # Calcular o centro do kernel
    center_x = n // 2
    center_y = m // 2

    # Criar as coordenadas do kernel
    x = np.arange(n) - center_x
    y = np.arange(m) - center_y

    # Criar a malha de coordenadas
    x_mesh, y_mesh = np.meshgrid(x, y)

    # Calcular o kernel gaussiano
    kernel = np.exp(-(x_mesh**2 + y_mesh**2) / (2 * sigma**2))
    kernel /= (2 * np.pi * sigma**2)
    kernel = kernel/kernel.max()
    return kernel


