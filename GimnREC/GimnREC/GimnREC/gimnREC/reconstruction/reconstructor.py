from gimnREC.image import image
from gimnREC.reconstruction.backprojectors import *
from gimnREC.reconstruction.projectors import *
from gimnREC.reconstruction.normalizer import *
from gimnREC.reconstruction.filters import *
from scipy.ndimage import gaussian_filter
from gimnREC.image.interpolators import *
from gimnREC.reconstruction.rotationCenter import *
from scipy.fft import rfft
from matplotlib import pyplot as plt
from numba import njit

import numpy as np


@njit
def system_matrix(nxd,nrd,nphi,angles,correction_center):
    """
        Implements the system matrix, that correspond to the projection around each pixel for the given angles.\n
        To this project we assume circular geometry\n
        in order to alter the geometry please alter the yp variable.\n
        The input parameter angles will be a angles = np.linspace(0,angle_in_radians,number_of_angles)
    """

    system_matrix = np.zeros((nrd*nphi, nxd*nxd)) # numero de linhas =  numero de bins no sinograma
                                                    # numero de colunas=  numero de pixels na imagem
    if correction_center is None:
        correction_center =nxd*0.5
    else:
        print("Correction center ",correction_center)


    # aqui xv e yv irão percorrrer imagem, enquanto ph será o angulo de rotação de cada pixel para a geração da system matrix
    for xv in range(nxd):
        for yv in range(nxd):
            for ph in range(nphi):
                yp = -(xv-(correction_center))*np.sin(angles[ph])+(yv-(correction_center))*np.cos(angles[ph]) # aqui se assume a geometria circular
                yp_bin =int(yp+(nrd)//2.0)
                if yp_bin+ph*nrd < nrd*nphi:
                    system_matrix[yp_bin+ph*nrd, xv+yv*nxd] = 1
    return system_matrix

class reconstructor (image):
    """
    Creates a Reconstructor class that will inherit image class.\n
    

    The sinogram order inside our program is :\n
    * rows : slice\n
    * columns : distances\n
    * Z : angles;

    The sinogram order list must have the folowing names, but the order can change :\n
    \n("slice","distances","angles")

    """
    __sinogram_order_recon = ("slice","distances","angles")  #Sinogam order inside our program
    __center_of_rotation = None                              #center of rotation
    __sinogram_order = None                                  #Sinogram Order, used for repositioning the dimensions following the order needed to reconstruct
    __sinogram  = None
    __reconstructed_mlem = None
    __reconstructed_osem = None
    __reconstructed_fbp = None
  
    
    def __init__ (self,path=None,sinogram=None,sinogram_order = ("slice","angles","distances"), center_of_rotation = None,transpose=None):
        """
        constructs the reconstructor class, it will initiate the super class of reconstructor, that inherits an image class
        the image class will be responsable for opening the dicom and retrievint it's pixels as a numpy object
        
        """
    
        super(reconstructor,self).__init__(path = path , image = sinogram)

        if path is not None:
            self.__sinogram_order = sinogram_order
            self.__sinogram = self.pixels
            self.__sinogram = self.move_axis(self.check_sinogram_order(sinogram_order))


    def check_sinogram_order(self,sinogram_order):
        """
        This method will be used in order to obtain the dimensions organization order.\n

        i.e:\n
        The sinogram order list must have the folowing names, but the order can change :\n
        \n("slice","distances","angles")
        
        """
        order = []
        if not (tuple(sinogram_order) == tuple(self.__sinogram_order_recon)):
            for i, original in enumerate(self.__sinogram_order_recon):
                counter = 0
                for incoming in sinogram_order:

                    if incoming==original:
                        order.append(counter)
                    counter+=1
        else:
            order = [0,1,2]
        return(order)
    
    def move_axis(self,order):
        """
        Depending on the order given, the program will move the axes in order to obtain the organization\n
        needed for the reconstruction
        
        """
        print("New order ", order)
        return np.moveaxis(self.sinogram,[0,1,2],order)
    
    @property
    def sinogram (self):
        '''
            Returns the sinogram pixels as a numpy object
        '''
        return self.__sinogram
    
    def set_sinogram(self,sinogram):
        self.__sinogram = sinogram

    def set_img(self,img):
        '''
            Sets the image
        '''
        self.__img = img


    def set_center_of_rotation (self, center_of_rotation):
        """ 
        Sets the value for the center of rotation
        """
        self.__center_of_rotation = center_of_rotation

    def mlem(self,iterations,interpolation, angles,verbose=False):
        """

        Reconstructs the sinogram using the Maximum likelihood expectation maximization algorithm for a given number of iterations.\n
        This reconstruction is done using the rotations of the "reconstructed image" in order to obtain the projections.\n
        We must provide as inputs:\n
            * iteratinos = number of iterations\n
            * interpolation = interpolator to be used, it can be : linear_interpolation, beta_spline_interpolation, bilinear_interpolation and beta_spline_interpolation_o5
            * verbose = will print the iteration each iteration 
            * angles = The input parameter angles will be a angles = np.linspace(0,angle_in_radians,number_of_angles)

        """
        if self.sinogram is None:
            print( "No sinogram Loaded")
            return -1
        

        slices = self.sinogram.shape[0]
        pixels = self.sinogram.shape[1]
     
        rec=np.ones((self.sinogram.shape[0],self.sinogram.shape[1],self.sinogram.shape[1]))
        for slice_z in range(slices):
            print("Slice ",slice_z)
            sinogram = self.sinogram[slice_z,:,:]
            imagem_estimada = np.ones([pixels,pixels])
            for it in range (iterations):
                if verbose:
                    print("iteration- ",it)
                imagem_estimada = np.nan_to_num(gaussian_filter(imagem_estimada,0.1),copy=True,nan=1)
                proje_estimada = radon_m(imagem_estimada,angles,interpolation,center = self.__center_of_rotation)
                diff =sinogram/(proje_estimada+10e-9)
                imagem_estimada = iradon_m(diff,interpolation,angles,self.__center_of_rotation)*imagem_estimada
            
            rec[slice_z,:,:] = imagem_estimada

        self.__reconstructed_mlem = rec
        return rec


    def osem(self,iterations,subsets_n,interpolation,angles,verbose=False,show_images=False):
        """

        Reconstructs the sinogram using the Ordered Subset Expectation Maximization algorithm for a given number of iterations.\n
        This reconstruction is done using the rotations of the "reconstructed image" in order to obtain the projections.\n
        We must provide as inputs:\n
            * iteratinos = number of iterations\n
            * subsets_n  = number of subsets\n
            * interpolation = interpolator to be used, it can be : linear_interpolation, beta_spline_interpolation, bilinear_interpolation and beta_spline_interpolation_o5
            * verbose = will print the iteration each iteration 
        """
        
        slices = self.sinogram.shape[0]
        pixels = self.sinogram.shape[1]
        
        
        rec=np.ones((self.sinogram.shape[0],self.sinogram.shape[1],self.sinogram.shape[1]))

        slice_count = self.slice_n()
        for slice_z in range(slices):
            if verbose:
                print ( "slice : ", slice_z)
            sinogram = self.sinogram[slice_z,:,:]
            
            angles_subset = np.array_split(angles,subsets_n)
            subsets =  np.array_split(sinogram, subsets_n,axis=1)
            reconstruction = np.ones([pixels,pixels])
            for it in range (iterations):
                if verbose:
                    print("iteration- ",it)
                for i,subset in enumerate(subsets):
                    rec_sub = projector(reconstruction,angles_subset[i],interpolation,center=self.__center_of_rotation)
                    coef = subset/(rec_sub+(10e-9))
                    #coef = np.nan_to_num(coef,copy=True,nan=0)
                    reconstruction *= np.abs((backprojector(coef,angles_subset[i],interpolation,center=self.__center_of_rotation))) 
                    reconstruction = reconstruction/reconstruction.max()
                    mult = slice_count[slice_z]/(reconstruction.shape[0]*reconstruction.shape[1])
                    reconstruction *= mult
            rec[slice_z,:,:] = reconstruction
            if show_images:
                plt.imshow(reconstruction)
                plt.colorbar()
                plt.show()

        #rec = np.nan_to_num(rec,copy=True,nan=0)
        rec = self.normalize(rec)
        self.__reconstructed_osem = rec
        return rec


    def fbp(self,interpolation,filter_type,angles):

        """

        Reconstructs the sinogram using the Maximum likelihood expectation maximization algorithm for a given number of iterations.\n
        This reconstruction is done using the rotations of the "reconstructed image" in order to obtain the projections.\n
        We must provide as inputs:\n
            * interpolation = interpolator to be used, it can be : linear_interpolation, beta_spline_interpolation, bilinear_interpolation and beta_spline_interpolation_o5
            * filter_type = it is the filter used in filtered backprojection, it can be : cossineFilter , ramLak.
            * verbose = will print the iteration each iteration 
            * angles = The input parameter angles will be a angles = np.linspace(0,angle_in_radians,number_of_angles)

        """
        if self.sinogram == None:
            print( "No sinogram Loaded")
            return -1
        slices = self.sinogram.shape[0]
        rec=np.ones((self.sinogram.shape[0],self.sinogram.shape[1],self.sinogram.shape[1]))
        for slice_z in range(slices):
            sinogram = self.sinogram[slice_z,:,:]
            filtered = apply_filter_to_sinogram(filter_type,sinogram)
            rec[slice_z,:,:] = iradon_m(filtered,interpolation,center=self.__center_of_rotation,angles=angles)
        self.__reconstructed_fbp = rec

        return rec
        

    def slice_n(self):
        """
        counts the total number of counts for each slice
        """
        slice_count = np.zeros(self.sinogram.shape[0])
        for slice_sino in range(self.sinogram.shape[0]):
            slice_count[slice_sino]=self.sinogram[slice_sino,:,:].sum()
        return slice_count
    
    def normalize(self,image):
        """
        Normalize the sinogram

        """
        norm = np.zeros(image.shape)
        slices_n = self.slice_n()
        image = image[:]
        #image = normalize_histogram(image)
        for i, count in enumerate(slices_n):
            norm_img =(image[i,:,:]/image[i,:,:].sum())
            norm[i,:,:]= norm_img*count  
        return norm

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




class reconstructor_system_matrix_cpu (reconstructor):
    """
    
    Implements a image reconstructor using the system matrix. This Processing is made using the CPU
    
    """

    # nxd numero de elementos na dimensão x da imagem
    # nrd numero de elementos na distancia do sinograma ( bins )(quantidade de pixels na aquisicao)
    # nphi numero de angulos ( do sinograma pode ser entendido como quantidade de elementos no vetor de angulos que comppõe o sinograma)

    nxd = 0
    nrd = 0
    nphi = 0
    correction_center = 0
    sens_img = 0

    def __init__(self, path=None, sinogram=None, sinogram_order=("slice", "angles", "distances"), center_of_rotation=None,transpose=None):
        super(reconstructor_system_matrix_cpu,self).__init__(path, sinogram, sinogram_order, center_of_rotation)
        if path is not None:
            self.nxd = self.sinogram.shape[1]
            self.nrd = int(self.nxd)
            self.nphi = self.sinogram.shape[2]
            self.slice = self.sinogram.shape[0]
        self.correction_center = center_of_rotation

    def set_sinogram(self,sinogram):
        self.__sinogram = sinogram
        self.nxd = self.__sinogram.shape[1]
        self.nrd = int(self.nxd)
        self.nphi = self.__sinogram.shape[2]
        self.slice = self.__sinogram.shape[0]


    def system_matrix(self,angles):
        """
            Implements the system matrix, that correspond to the projection around each pixel for the given angles.\n
            To this project we assume circular geometry\n
            in order to alter the geometry please alter the yp variable.\n
            The input parameter angles will be a angles = np.linspace(0,angle_in_radians,number_of_angles)
        """

        system_matrix = np.zeros((self.nrd*self.nphi, self.nxd*self.nxd)) # numero de linhas =  numero de bins no sinograma
                                                      # numero de colunas=  numero de pixels na imagem
        if self.correction_center is None:
          correction_center =self.nxd*0.5
        else:
            correction_center = self.correction_center
            print("Correction center ",correction_center)


        # aqui xv e yv irão percorrrer imagem, enquanto ph será o angulo de rotação de cada pixel para a geração da system matrix
        for xv in range(self.nxd):
            for yv in range(self.nxd):
                for ph in range(self.nphi):
                    yp = -(xv-(correction_center))*np.sin(angles[ph])+(yv-(correction_center))*np.cos(angles[ph]) # aqui se assume a geometria circular
                    yp_bin =int(yp+(self.nrd)//2.0)
                    if yp_bin+ph*self.nrd < self.nrd*self.nphi:
                        system_matrix[yp_bin+ph*self.nrd, xv+yv*self.nxd] = 1
        return system_matrix
    

    # irá fazer a projeção da imagem
    def forward_project(self, image, sys_mat):
        """
        Generates the forward projection of the sinogram using the system matrix
        """
        return np.reshape(np.matmul(sys_mat, np.reshape(image, (self.nxd*self.nxd, 1))), (self.nphi, self.nrd))

    # ira fazr a retroprojeção da imagem.
    def backproject(self, sino, sys_mat):
        """
        Generates tehe backprojection of the sinogram using the system matrix.
        """
        return np.reshape(np.matmul(sys_mat.T, np.reshape(sino, (self.nrd*self.nphi, 1))), (self.nxd, self.nxd))

    @property
    def sinogram (self):
        '''
            Returns the sinogram pixels as a numpy object
        '''
        return self.__sinogram

    def mlem(self, num_its, angles):
        """

        Reconstructs the sinogram using the Maximum likelihood expectation maximization algorithm for a given number of iterations.\n
        
        """
        recon = np.ones((self.slice,self.nxd, self.nxd))
        
        for slice in range(self.sinogram.shape[0]):
            sino_for_reconstruction = self.sinogram[slice,:,:]
            self.correction_center = rot_center(sino_for_reconstruction.T)
            sys_mat = system_matrix(nxd=self.nxd,nrd=self.nrd,nphi=self.nphi,angles=angles,correction_center=self.correction_center)
            sino_ones  =   np.ones_like(sino_for_reconstruction)
            sens_image =   self.backproject(sino_ones,sys_mat)
            print(slice)
            for it in range(num_its):
                print(it)
                fpsino = self.forward_project(recon[slice,:,:], sys_mat)
                ratio = sino_for_reconstruction/(fpsino+1.0e-9)
                correction = self.backproject(ratio, sys_mat)/(sens_image+1.0e-9)
                recon[slice,:,:] = recon[slice,:,:]*correction
        
        return recon

    def osem(self, num_its , num_subsets , angles, sens_image=None,verbose = False):
        """

        Reconstructs the sinogram using the Ordered Subset Expectation Maximization algorithm for a given number of iterations.\n
        This reconstruction is done using the system matrix in order to obtain projections and backprojections\n
        We must provide as inputs:\n
            * num_its = number of iterations\n
            * num_subsets  = number of subsets\n
            * sens_image = sensitivity image
            * angles = The input parameter angles will be a angles = np.linspace(0,angle_in_radians,number_of_angles)
        """
        recon = np.ones((self.slice,self.nxd, self.nxd))
        for slice in range(self.sinogram.shape[0]):
            print(slice)
            sino_for_reconstruction = self.sinogram[slice,:,:]
            self.correction_center =None# rot_center(sino_for_reconstruction)
            #sys_mat = self.system_matrix(angles=angles)
            sys_mat = system_matrix(nxd=self.nxd,nrd=self.nrd,nphi=self.nphi,angles=angles,correction_center=self.correction_center)
            sino_ones  =   np.ones_like(sino_for_reconstruction)
            sens_image =   self.backproject(sino_ones,sys_mat)
            # transforma o sinograma em um sinograma de 1 dimensão
            sino1d = np.reshape(sino_for_reconstruction,(sino_for_reconstruction.shape[0]*sino_for_reconstruction.shape[1],1))
            # separa o sinograma de 1d em n subsets
            sub_set = np.split(sino1d, num_subsets)
            # separa a matriz do sistema em n subsets também sobre o eixo das linhas que equivale aos sinogramas
            subset_matrix = np.split(sys_mat,num_subsets,axis=0)
            #inicializa imagem de reconstrucao como ima matriz de uns
            for it in range(num_its):
                print( "Iteração-",it)
                #percorre pelos subsets
                for ss, subset in enumerate(sub_set):
                    #realiza a projeção, que pode ser entendida como a multiplicação da matriz do sistema pelo vetor da imagem
                    fpsino = np.matmul(subset_matrix[ss],np.reshape(recon[slice,:,:], (self.nxd*self.nxd, 1)))
                    #calcula-se quanto esta fatia projetada da nossa imagem estimada é maior ou menor que nosso subset
                    ratio = subset/(fpsino+1.0e-9)
                    # calcula a retroprojeção da matriz dos fatores de correção
                    correction = np.matmul(subset_matrix[ss].T, np.reshape(ratio, (self.nrd*int(self.nphi/num_subsets), 1)))
                    #transforma a "correction" novamente em uma imagem, e coloca o valor no slice correspondente.
                    recon[slice,:,:]= recon[slice,:,:]*np.reshape(correction,(self.nxd, self.nxd))
            
            if verbose==True:
                plt.imshow(recon[slice,:,:])
                plt.show()
        return recon


    

