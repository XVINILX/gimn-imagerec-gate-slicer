import numpy as np

def normalize_histogram(image):

        hist, bins = np.histogram(image.flatten(), bins=256, range=[0, 65535])
        
        # Calcula a função de distribuição acumulada (CDF) do histograma
        cdf = hist.cumsum()
        
        # Normaliza a CDF para o intervalo [0, 65535]
        cdf_normalized = (cdf - cdf.min()) * 65535 / (cdf.max() - cdf.min())
        
        # Interpola os valores do histograma normalizado
        image_normalized = np.interp(image.flatten(), bins[:-1], cdf_normalized)
        
        # Remodela a imagem normalizada para sua forma original
        image_normalized = image_normalized.reshape(image.shape)
        

        return image_normalized.astype(np.uint16)