import numpy as np
from gimnREC.image.rotate import rotate


def radon_m(image,angles,interpolator,center=None):
    #cria o sinograma de saida
    sino = np.zeros([image.shape[0],angles.size])
    for i,angulo in enumerate(angles):
        #adiciona a cada coluna do sinograma a soma da imagem rotacionada em um certo angulo
        test = rotate(image,angulo,interpolator,center=center)
        sino[:,i]= test.sum(axis=1)
    #retorna o sinograma
    return sino


def projector(image,angles,interpolator,center=None):
    #cria o sinograma de saida
    ang = angles

    sino = np.zeros([image.shape[0],len(angles)])

    for i,angulo in enumerate(ang):
        #adiciona a cada coluna do sinograma a soma da imagem rotacionada em um certo angulo
        test = rotate(image,angulo,interpolator,center=center)
        sino[:,i]= test.sum(axis=1)
    #retorna o sinograma
    return sino