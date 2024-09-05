import logging
import os
from typing import Annotated, Optional
import numpy as np
import qt



from gimnREC.reconstruction.reconstructor import reconstructor_system_matrix_cpu as rec
from gimnREC.image import image
from gimnREC.reconstruction import reconstructor
from gimnREC.image.interpolators import linear_interpolation as lin_int
from gimnREC.reconstruction.filters import ramLak
from gimnREC.reconstruction.normalizer import normalize_histogram
from gimnREC.reconstruction.projectors import projector


import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode


#
# GimnREC
#

class GimnREC(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "GimnREC"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["GimnREC"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = ["qt", "slicer", "numpy", "numba", "matplotlib"]  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Michael Raed (Gimn)", "Vinicius Vale (GIMN)"]  # TODO: replace with "Firstname Lastname (Organization)"
        
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a "href="https://github.com/organization/projectname#GimnREC">module documentation</a>.
"""
        
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # GimnREC1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='GimnREC',
        sampleName='GimnREC1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'GimnREC1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='GimnREC1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='GimnREC1'
    )

    # GimnREC2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='GimnREC',
        sampleName='GimnREC2',
        thumbnailFileName=os.path.join(iconsPath, 'GimnREC2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='GimnREC2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='GimnREC2'
    )


#
# GimnRECParameterNode
#

@parameterNodeWrapper
class GimnRECParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """
    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# GimnRECWidget
#

class GimnRECWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None
        self.counter =0
        self.redLogic = None
        self.yellowLogic = None
        
        self.greenLogic = None
        
    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/GimnREC.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = GimnRECLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        layoutManager = slicer.app.layoutManager()
        self.redLogic = layoutManager.sliceWidget("Red").sliceLogic()
        self.greenLogic = layoutManager.sliceWidget("Green").sliceLogic()
        self.yellowLogic = layoutManager.sliceWidget("Yellow").sliceLogic()
        
        #Combo Box
        self.ui.option.currentIndexChanged.connect(self.combo_box_option)

        # Buttons
        # self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
        self.ui.reconstruct_button.connect('clicked(bool)',self.recosntruct_button)
        self.ui.swap_axis_btn.connect("clicked(bool)",self.swap_axis)
        self.ui.axs1_btn.connect("clicked(bool)",self.flip1)
        self.ui.axs2_btn.connect("clicked(bool)",self.flip2)
        self.ui.axs3_btn.connect("clicked(bool)",self.flip3)




        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def combo_box_option(self):
        """
        Enables and disables spin boxes
        
        """
        if self.ui.option.currentText == "OSEM":
            self.ui.subsets.setDisabled(False)
            self.ui.subsets.setValue(8)
            self.ui.iterations.setValue(3)

        if self.ui.option.currentText == "MLEM":
            self.ui.subsets.setDisabled(True)
            self.ui.subsets.setValue(0)
            self.ui.iterations.setValue(10)

    def new_vol(self,name, shape):
        """
        Generates a New volume

        """
        # Set up the parameters for the new volume
        nodeName = name
        imageSize = shape
        voxelType = vtk.VTK_UNSIGNED_SHORT
        imageOrigin = [0.0, 0.0, 0.0]
        imageSpacing = [1.0, 1.0, 1.0]
        imageDirections = [[1,0,0], [0,1,0], [0,0,1]]
        fillVoxelValue = 0

        # Create the direction matrix
        directionMatrix = vtk.vtkMatrix3x3()
        for i in range(3):
            for j in range(3):
                directionMatrix.SetElement(i, j, imageDirections[i][j])

        # Create the new volume
        imageData = vtk.vtkImageData()
        imageData.SetDimensions(imageSize)
        imageData.AllocateScalars(voxelType, 1)
        imageData.SetOrigin(imageOrigin)
        imageData.SetSpacing(imageSpacing)
        imageData.SetDirectionMatrix(directionMatrix)
        imageData.GetPointData().GetScalars().Fill(fillVoxelValue)

        # Add the new volume to the scene
        volumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", nodeName)
        volumeNode.SetAndObserveImageData(imageData)



    def update_visualization(self,node):
        slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveVolumeID(node.GetID())
        slicer.app.applicationLogic().PropagateVolumeSelection(0)
        #ijktoras = vtk.vtkMatrix4x4()
        #node.GetIJKToRASMatrix(ijktoras)
        #pos = [64,64,64,1] #ijk
        #pos_ras = ijktoras.MultiplyPoint(pos) #ras
        #print (" Pos  {} , pos_ras {}".format(pos,pos_ras))
        layoutManager = slicer.app.layoutManager()
        redLogic = layoutManager.sliceWidget("Red").sliceLogic()
        greenLogic = layoutManager.sliceWidget("Green").sliceLogic()
        yellowLogic = layoutManager.sliceWidget("Yellow").sliceLogic()
        
        redLogic.SetSliceOffset(64)
        yellowLogic.SetSliceOffset(64)
        greenLogic.SetSliceOffset(-64)



    def flip1(self):
        """
        Flips the axis 1
        """
        current_node = self.ui.inputSelector.currentNode()
        current_node_name = current_node.GetName()
        axes = slicer.util.array(current_node_name)
        fliped = np.flip(axes,axis=0)
        slicer.util.updateVolumeFromArray(current_node, fliped)

    def flip2(self):
        """
        
        Flips the axis 2
        """
        current_node = self.ui.inputSelector.currentNode()
        current_node_name = current_node.GetName()
        axes = slicer.util.array(current_node_name)
        fliped = np.flip(axes,axis=1)
        slicer.util.updateVolumeFromArray(current_node, fliped)

    def flip3(self):
        """
        Flips the axis 3
        
        """
        current_node = self.ui.inputSelector.currentNode()
        current_node_name = current_node.GetName()
        axes = slicer.util.array(current_node_name)
        fliped = np.flip(axes,axis=2)
        slicer.util.updateVolumeFromArray(current_node, fliped)


    def swap_axis(self):
        """
        Swap selected axis
        """
        ax1 = self.ui.axis1_val.value
        ax2 = self.ui.axis2_val.value
        
        current_node = self.ui.inputSelector.currentNode()
        current_node_name = current_node.GetName()
        axes = slicer.util.array(current_node_name)
        axes = np.swapaxes(axes,ax1,ax2)
        
        slicer.util.updateVolumeFromArray(current_node, axes)
        self.counter = self.counter +1



    def recosntruct_button(self):
    # Get necessary parameters for reconstruction

        if self.ui.option.currentText == "Reconstruction Method":
            msgBox = qt.QMessageBox()
            msgBox.setIcon(qt.QMessageBox.Information)
            msgBox.setText("Please Select the reconstruction method.")
            msgBox.setWindowTitle("Information")
            msgBox.setStandardButtons(qt.QMessageBox.Ok)
            msgBox.exec_()
            return 0


        if (not self.ui.rotated_radio.isChecked()) and (not self.ui.sys_mat_radio.isChecked()):
            msgBox = qt.QMessageBox()
            msgBox.setIcon(qt.QMessageBox.Information)
            msgBox.setText("Please Select the reconstruction algorithm type: rotated or system matrix.")
            msgBox.setWindowTitle("Information")
            msgBox.setStandardButtons(qt.QMessageBox.Ok)
            msgBox.exec_()
            return 0


        """
            There are two options for the algorithm implementation, for both osem and mlem. The first one is implemented using rotations of the image
            and then de summing of each pixel line in order to obtain the sinogram. The seccond one is more time consuming, but more acurate, that 
            computes the sinogram for each pixel of the reconstructed image, obtaining the system matrix.
        
        """
        if (self.counter==0):
            msgBox = qt.QMessageBox()
            msgBox.setIcon(qt.QMessageBox.Warning)
            msgBox.setText("Please Put the Sinogram in the correct order")
            msgBox.setWindowTitle("Warning")
            msgBox.setStandardButtons(qt.QMessageBox.Ok)
            msgBox.exec_()
            return 0
    
        
        inputSinogram = self.ui.inputSelector.currentNode() 

        reconstructionMethod = "rotated" if self.ui.rotated_radio.isChecked() else "system_matrix"
        algorithm = self.ui.option.currentText
        iterations = self.ui.iterations.value
        subsets = self.ui.subsets.value
        current_node = self.ui.inputSelector.currentNode()
        if current_node is None:
            msgBox = qt.QMessageBox()
            msgBox.setIcon(qt.QMessageBox.Information)
            msgBox.setText("Please load a Sinogram to reconstruct")
            msgBox.setWindowTitle("Information")
            msgBox.setStandardButtons(qt.QMessageBox.Ok)
            msgBox.exec_()
            return 0
        else:
            current_node_name = current_node.GetName()
        # Gets data from slicer                 
        data  = slicer.util.array(current_node_name)
        # Prints data shape
        
        angles = np.linspace(0, 2 * np.pi, data.shape[1]) + np.pi / 2


        # Call the process function for reconstruction
        self.logic.process(inputSinogram, reconstructionMethod, algorithm, iterations, subsets, angles)


    def cleanup(self) -> None:
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self) -> None:
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in param'eter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[GimnRECParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """
        
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume:
            self.ui.reconstruct_button.toolTip = "Compute output volume"
            self.ui.reconstruct_button.enabled = True
        else:
            self.ui.reconstruct_button.toolTip = "Select input and output volume nodes"
            self.ui.reconstruct_button.enabled = False



#
# GimnRECLogic
#

class GimnRECLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return GimnRECParameterNode(super().getParameterNode())
    

    def update_visualization(self,node):
        slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveVolumeID(node.GetID())
        slicer.app.applicationLogic().PropagateVolumeSelection(0)
        ijktoras = vtk.vtkMatrix4x4()
        node.GetIJKToRASMatrix(ijktoras)
        pos = [64,64,64,1] #ijk
        pos_ras = ijktoras.MultiplyPoint(pos) #ras
        print (" Pos  {} , pos_ras {}".format(pos,pos_ras))
        layoutManager = slicer.app.layoutManager()
        redLogic = layoutManager.sliceWidget("Red").sliceLogic()
        greenLogic = layoutManager.sliceWidget("Green").sliceLogic()
        yellowLogic = layoutManager.sliceWidget("Yellow").sliceLogic()
        
        redLogic.SetSliceOffset(64)
        yellowLogic.SetSliceOffset(64)
        greenLogic.SetSliceOffset(-64)


    def new_vol(self,name, shape):
        """
        Generates a New volume

        """
        # Set up the parameters for the new volume
        nodeName = name
        imageSize = shape
        voxelType = vtk.VTK_UNSIGNED_SHORT
        imageOrigin = [0.0, 0.0, 0.0]
        imageSpacing = [1.0, 1.0, 1.0]
        imageDirections = [[1,0,0], [0,1,0], [0,0,1]]
        fillVoxelValue = 0

        # Create the direction matrix
        directionMatrix = vtk.vtkMatrix3x3()
        for i in range(3):
            for j in range(3):
                directionMatrix.SetElement(i, j, imageDirections[i][j])

        # Create the new volume
        imageData = vtk.vtkImageData()
        imageData.SetDimensions(imageSize)
        imageData.AllocateScalars(voxelType, 1)
        imageData.SetOrigin(imageOrigin)
        imageData.SetSpacing(imageSpacing)
        imageData.SetDirectionMatrix(directionMatrix)
        imageData.GetPointData().GetScalars().Fill(fillVoxelValue)

        # Add the new volume to the scene
        volumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", nodeName)
        volumeNode.SetAndObserveImageData(imageData)

    

    def process(self, inputSinogram: vtkMRMLScalarVolumeNode, 
        reconstructionMethod: str, algorithm: str, iterations: int, subsets: int = 0, 
        angles: Optional[np.ndarray] = None, showResult: bool = True) -> None:
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: node - volume to be reconstructed
        :param reconstructionMethod: string - "rotated" or "system_matrix" options
        :param algorithm: string - OSEM or MLEM method of reconstruction
        :param iterations: int - quantity of interations
        :param subsets: int - quantity of subsets
        :param angles: float[] - angles for reconstruction
        :param showResult: boolean - wheter to show reults
        """
    

        current_node_name = inputSinogram.GetName()
        if not inputSinogram:
            raise ValueError("Input or output volume is invalid")
        
        data  = slicer.util.array(current_node_name)
        # Prints data shape
        print(data.shape, "data shape")
        import time
        startTime = time.time()
        logging.info('Processing started')

        if reconstructionMethod == 'rotated':
            """
            Reconstructs usong Rotation Method
            """
            # instantiates the reconstructor
            rec_rot = reconstructor(path = None)
            # set the sinogram
            rec_rot.set_sinogram(data)

            print("Setting sinogram into reconstructor")

            if algorithm == "OSEM":
                reconstructed = rec_rot.osem(iterations,subsets,lin_int,angles,verbose=True)
            elif algorithm == "MLEM":
                print(angles)
                reconstructed = rec_rot.mlem(iterations,lin_int,angles,verbose=True)

        elif reconstructionMethod == 'system_matrix':
            recon  = rec(path = None)
            recon.set_sinogram(data)
            print("Setting sinogram into reconstructor")
            if algorithm == "OSEM":
                reconstructed = recon.osem(iterations,subsets,angles,verbose=False)
            elif algorithm == "MLEM":
                reconstructed = recon.mlem(iterations,angles,verbose=False)


        nodeList = slicer.mrmlScene.GetNodes()
        found = False
        for node in nodeList:
            if node.GetName() =="reconstruction":
                found = True
                print("Reconstruction already exists")

            

        print(reconstructed.shape, 'reconstructed shape')
        
        if not found:
            self.new_vol("reconstruction",reconstructed.shape)


        print(reconstructed, 'reconstructed')
        for node in nodeList:
            if node.GetName() =="reconstruction":
                if reconstructed is not None:
                    
                    slicer.util.updateVolumeFromArray(node, reconstructed)
                    self.update_visualization(node)
            

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# GimnRECTest
#

class GimnRECTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_I00001()

    def swap_axis(self, inputVolume, ax1Input, ax2Input):
        """
        Swap selected axis
        """
        ax1 = ax1Input
        ax2 = ax2Input
        
        current_node_name = inputVolume.GetName()
        axes = slicer.util.array(current_node_name)
        axes = np.swapaxes(axes,ax1,ax2)
        
        slicer.util.updateVolumeFromArray(inputVolume, axes)
        


    def test_I00001(self):
        """
        Test the GimnREC module with the I00001.dcm file.
        """
        self.delayDisplay("Starting the I00001 test")

        # Get/create input data
        import os
        dataDir = os.path.join(os.path.dirname(__file__), 'Testing', 'Python')
        inputVolume = slicer.util.loadVolume(os.path.join(dataDir, 'I00001.dcm'))
        current_node_name = inputVolume.GetName()


        self.swap_axis(inputVolume,2,0)
        self.swap_axis(inputVolume,1,0)
        self.assertIsNotNone(inputVolume)
        self.delayDisplay('Loaded test data set')
        nodeList = slicer.mrmlScene.GetNodes()
        for node in nodeList:
            if node.GetName() ==current_node_name:
                inputVolume = node
                
                    
                
        inputImageData = inputVolume.GetImageData()

        self.assertIsNotNone(inputImageData)

        # Get the shape of the image data
        inputShape = inputImageData.GetDimensions()
        print(f"Input data shape: {inputShape}")

        # Compute the angles
        angles = np.linspace(0, 2 * np.pi, inputShape[1]) + np.pi / 2

        # Check input volume properties
        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertGreater(inputScalarRange[1], inputScalarRange[0])
            
        logic = GimnRECLogic()
    
        logic.process(inputVolume, "rotated", "OSEM", 3, 8, angles)

        self.delayDisplay('Test passed')
