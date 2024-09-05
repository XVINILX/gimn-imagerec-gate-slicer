import slicer
try:
    import itk
except:
    slicer.util.pip_install('itk')
    import itk
    

import numpy as np
import platform
from gimnREC.reconstruction.normalizer import normalize_histogram

try:
    import matplotlib.pyplot as plt 
except:
    pip_install('matplotlib')
    import matplotlib.pyplot as plt



class image:
    """
    Implements the class that will Read our images
    
    """
    __np_pixels = None
    __is_in_memory = False
    __from_image = False
    __name = None
    __from_hdd = False
    __image_path = None
    __image_extension = None
    __is_in_hdd = False
    __is_empty = True
    __out_path = ""
    __sinogram = None

    def __init__(self,path = None , image = None ):
        if image is not None:
            self.set_image(image)
        if path is not None:
            self.read_image(path)


    def read_image(self,path):
        """
        Opens a given path and then tries to read the image in the given path
        """
        try: 
            self.path = path
            self.__np_pixels = itk.imread(self.path)
            self.__np_pixels = itk.array_from_image(self.__np_pixels)
            if platform.system()=="Linux":
                self.__name = self.path.split(sep="/")[-1].split(sep=".")[0]
            if platform.system()=="Windows":
                self.__name = self.path.split(sep="\\")[-1].split(sep=".")[0]
            self.__from_hdd = True
            self.__from_image = False
            self.__is_empty=False
        except Exception as e:
            print("An error ocourred :\n",str(e))

    def set_image(self,image):
        """
        set image proprety as image
        
        """
        self.__from_hdd = False
        self.__from_image = True
        self.__np_pixels = np.asarray(image)
        self.__is_empty=False


    def set_name(self,name):
        """
        Set Image Name, it is use to save the image on the pc.
        """
        self.__name = name

    def save(self,image,extension,complement=""):
        """
        Save an "image", with a given "complement in the name" and an extension i.e ".dcm" ,".jpg" etc;
        """
        if self.name is not None:
            name_out = self.__out_path+self.name+"_"+complement+extension

            image_cpy = image[:]

            #minimum = image.min()
            #if minimum <0 :
            #    image_cpy += (-1)*(minimum)
            #else :
            #    image_cpy += minimum

            #image_cpy = image_cpy/(image_cpy.sum()+10e-9)
            #image_cpy *= np.iinfo(np.uint16).max

            #
            # TODO: ADJUST the linearity 
            #

            #slope = self.sinogram.sum()/np.iinfo(np.uint16).max
            #intercept = 0
            image_itk = itk.image_view_from_array(np.zeros(image_cpy.shape))
            metadata_dict =image_itk.GetMetaDataDictionary()
            #metadata_dict["0028|1053"] = str(slope)  
            #metadata_dict["0028|1052"] = str(intercept)
            #normalized= normalize_histogram(image_cpy)

            
            for i in range(image_cpy.shape[0]):
                plt.imshow(image_cpy[i,:,:])
                plt.colorbar()
                plt.show()
            
            image_itk2= itk.image_view_from_array(image_cpy.astype(np.uint16))
            image_itk2.SetMetaDataDictionary(metadata_dict)
            
            itk.imwrite(image_itk2,name_out)
            self.__image_extension = extension
            self.__is_in_hdd = True

            print(f"saving file : \n{name_out}")
            return name_out
        else:
            print("Image has no name ...\n Saving with default name : 'saved_image'")
    @property
    def from_image(self):
        return self.__from_image
    
    @property
    def from_hdd(self):
        return self.__from_hdd

    @property
    def pixels(self):
        return self.__np_pixels

    @property
    def is_in_memory(self):
        return self.__is_in_memory
    
    @property
    def is_empty(self):
        return self.__is_empty

    @property
    def is_in_hdd(self):
        return self.__is_in_hdd
    
    @property
    def name(self):
        return self.__name
    
    @property
    def path (self):
        return self.__image_path
    
    def set_out_path(self,out_path):
        self.__out_path = out_path
        end = "/"
        if platform.system()=="Linux":
                end = "/"
        if platform.system()=="Windows":
                end = "\\"
        if self.__out_path[-1] != end:
            self.__out_path = self.out_path + end
    
    @property
    def out_path(self):
        return self.__out_path
    
    @path.setter
    def path (self,value):
        if isinstance(value,str):
            self.__image_path = value
        else:
            print("path is not a string")
