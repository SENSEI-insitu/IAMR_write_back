import sys
import numpy as np
import vtk.util.numpy_support as vtknp
from vtk import vtkDataObject, vtkCompositeDataSet, vtkMultiBlockDataSet

# set default values of control parameters
# these can be modified by the XML
meshName = 'mesh'
arrayName = 'density'
arrayCen = vtkDataObject.CELL
threshold = 1.5
multiplier = 0.5
verbose = True

def Initialize():
    # print some info indicating that we are alive and the values
    # about to be used
    r = comm.Get_rank()
    if r == 0:
        if verbose:
            sys.stderr.write('meshName=%s, arrayName=%s, threshold=%g, multiplier=%g\n'%( \
                meshName, arrayName, threshold, multiplier))

def Execute(adaptor):
    r = comm.Get_rank()
    if r == 0 and verbose:
        sys.stderr.write('Execute\n')

    # use SENSEI API to
    # get the mesh and array we's like to modify.
    mesh = adaptor.GetMesh(meshName, True)
    adaptor.AddArray(mesh, meshName, arrayCen, arrayName)

    # visit each block in the AMR hierarchy. we are treating it like
    # a collection of blocks, but one could also iterate by level if needed
    it = mesh.NewIterator()
    it.InitTraversal()
    while not it.IsDoneWithTraversal():
        do = it.GetCurrentDataObject()

        atts = do.GetPointData() if arrayCen == vtkDataObject.POINT \
             else do.GetCellData()

        # get the data array from VTK
        vda = atts.GetArray(arrayName)

        # convert into a numpy representation.
        # TODO -- when if ever is this directly modifiable??
        da = vtknp.vtk_to_numpy(vda)

        # scale values below the threshold
        ii = np.where(da <= threshold)[0]
        da[ii] *= multiplier

        # use the VTK API to modify the AMReX data directly
        #nt = vda.GetNumberOfTuples()
        #i = 0
        #while i < nt:
        #    vda.SetValue(i, da[i])
        #    i += 1

        it.GoToNextItem()

def Finalize():
    # print that we are done
    r = comm.Get_rank()
    if r == 0 and verbose:
        sys.stderr.write('Finalize\n')
    return 0
