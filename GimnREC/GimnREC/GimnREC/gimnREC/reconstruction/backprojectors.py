import numpy as np
from gimnREC.image.rotate import rotate

def iradon_m(sinogram,interpolator,angles,center=None):
    #retira os parametros como tamanho e numero de angulos
    size = sinogram.shape[0]
    angle_n = angles
    
    #instancia as saidas
    out = np.zeros([size,size])
    aux = np.zeros([size,size])
    
    #realiza a soma de cada coluna do sinograma  para todas as linhas da imagem
    #para um determinado angulo
    for i,angulo in enumerate (angle_n):
        col = sinogram[:,i]
        aux[:,0:size]=col
        out+=rotate(aux,angulo-(np.pi/2.0),interpolator,center=center)
    out = out/size
    return np.flip(out,axis=1)

def backprojector(sinogram,angles,interpolator,center=None):
    #retira os parametros como tamanho e numero de angulos
    size = sinogram.shape[0]
    #instancia as saidas
    out = np.zeros([size,size])
    aux = np.zeros([size,size])
    
    #realiza a soma de cada coluna do sinograma  para todas as linhas da imagem
    #para um determinado angulo
    for i,angulo in enumerate (angles):
        col = sinogram[:,i]
        aux[:,0:size]=col
        out+=rotate(aux,angulo-(np.pi/2.0),interpolator,center=center)
    out = out/size
    return np.flip(out,axis=1)
