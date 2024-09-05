import scipy.fft as fft
import numpy as np

def ramLak(size):
    #implementa o filtro RamLak
    ramlak=np.zeros(size)
    value=0.0
    ang = 0.5/(size/2)
    for i in range(size):
        if i<=int(size/2):
            value=value+ang
        if i>int(size/2):
            value=value-ang
        ramlak[i]=value

    return ramlak

def cossineFilter(size):
    #implementa o filtro de cossenos
    ram = ramLak(size)
    out = np.zeros (ram.shape[0])
    for i in range(ram.shape[0]):
        out[i] = ram[i]*np.cos(np.pi*ram[i])
    return out



def apply_filter_to_sinogram(filterType,sinogram):
    #aplica os filtros no sinograma

    #instancia o objeto de saida
    out = np.zeros(sinogram.shape)
    
    #instancia o filtro;
    filt = filterType(sinogram.shape[0])
    
    #cada coluna do sinograma sera passada para o domino das frequencias
    #e logo será aplicado o filtro selecionado
    for angle in range(sinogram.shape[1]):
        fftd = fft.fft(sinogram[:,angle])
        for i in range(fftd.shape[0]):
            fftd[i] = fftd[i]*filt[i]
        fftd = fft.ifft(fftd)
        out[:,angle]=fftd
    return np.real(out)

    
    