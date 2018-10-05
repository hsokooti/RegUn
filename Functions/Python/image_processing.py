import numpy as np
import SimpleITK as sitk


def calculate_jac(dvf, voxel_size=[1, 1]):
    """
    :param dvf: a numpy array with shape of (sizeY, sizeX, 2) or (sizeZ, sizeY, sizeX, 3). You might use np.transpose before this function to correct the order of DVF shape.
    :param voxel_size: physical voxel spacing in mm
    :return: Jac
    """
    if voxel_size is None:
        voxel_size = [1, 1, 1]

    if (len(np.shape(dvf)) - 1) != len(voxel_size):
        raise ValueError ('dimension of DVF is {} but dimension of voxelSize is {}'.format(
            len(np.shape(dvf)) - 1, len(voxel_size)))
    T = np.zeros(np.shape(dvf), dtype=np.float32) # derivative should be calculated on T which is DVF + indices (world coordinate)
    indices = [None] * (len(np.shape(dvf)) - 1)
    DVF_grad = []

    if len(voxel_size) == 2:
        indices[0], indices[1] = np.meshgrid(np.arange(0, np.shape(dvf)[0]), np.arange(0, np.shape(dvf)[1]), indexing='ij')
    if len(voxel_size) == 3:
        indices[0], indices[1], indices[2] = np.meshgrid(np.arange(0, np.shape(dvf)[0]),
                                                         np.arange(0, np.shape(dvf)[1]),
                                                         np.arange(0, np.shape(dvf)[2]), indexing='ij')

    for d in range(len(voxel_size)):
        indices[d] = indices[d] * voxel_size[d]
        T[:, :, :, d] = dvf[:, :, :, d] + indices[d]
        DVF_grad.append(np.gradient(T[:, :, :, d]))  # DVF.grad can be calculated in one shot without for loop.
    if len(voxel_size) == 2:
        Jac = DVF_grad[0][0] * DVF_grad[1][1] - DVF_grad[0][1] * DVF_grad[1][0]
        #       f0/dir0      *   f1/dir1      -    f0/dir1     *   f1/dir0

    if len(voxel_size) == 3:
        Jac = (DVF_grad[0][0] * DVF_grad[1][1] * DVF_grad[2][2] +  # f0/dir0 + f1/dir1 + f2/dir2
               DVF_grad[0][1] * DVF_grad[1][2] * DVF_grad[2][0] +  # f0/dir1 + f1/dir2 + f2/dir0
               DVF_grad[0][2] * DVF_grad[1][0] * DVF_grad[2][1] -
               DVF_grad[0][2] * DVF_grad[1][1] * DVF_grad[2][0] -
               DVF_grad[0][1] * DVF_grad[1][0] * DVF_grad[2][2] -
               DVF_grad[0][0] * DVF_grad[1][2] * DVF_grad[2][1]
               )

    return Jac


def resampler_by_dvf(im_sitk, dvf_t, im_ref=None, default_pixel_value=0, interpolator=sitk.sitkBSpline):
    if im_ref is None:
        im_ref = sitk.Image(dvf_t.GetDisplacementField().GetSize(), sitk.sitkInt8)
        im_ref.SetOrigin(dvf_t.GetDisplacementField().GetOrigin())
        im_ref.SetSpacing(dvf_t.GetDisplacementField().GetSpacing())
        im_ref.SetDirection(dvf_t.GetDisplacementField().GetDirection())

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(im_ref)
    resampler.SetInterpolator(interpolator)
    resampler.SetDefaultPixelValue(default_pixel_value)
    resampler.SetTransform(dvf_t)
    out_im = resampler.Execute(im_sitk)
    return out_im


def array_to_sitk(array_input, origin=None, spacing=None, direction=None, is_vector=False, im_ref=None):
    if origin is None:
        origin = [0, 0, 0]
    if spacing is None:
        spacing = [1, 1, 1]
    if direction is None:
        direction = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    sitk_output = sitk.GetImageFromArray(array_input, isVector=is_vector)
    if im_ref is None:
        sitk_output.SetOrigin(origin)
        sitk_output.SetSpacing(spacing)
        sitk_output.SetDirection(direction)
    else:
        sitk_output.SetOrigin(im_ref.GetOrigin())
        sitk_output.SetSpacing(im_ref.GetSpacing())
        sitk_output.SetDirection(im_ref.GetDirection())
    return sitk_output


def index_to_world(landmark_index, spacing=None, origin=None, direction=None, im_ref=None):
    if im_ref is None:
        if spacing is None:
            spacing = [1, 1, 1]
        if origin is None:
            origin = [0, 0, 0]
        if direction is None:
            direction = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    else:
        spacing = im_ref.GetSpacing()
        origin = im_ref.GetOrigin()
        direction = im_ref.GetDirection()
    landmarks_point = [None] * len(landmark_index)
    for p in range(len(landmark_index)):
        landmarks_point[p] = [index * spacing[i] + origin[i] for i, index in enumerate(landmark_index[p])]
    return landmarks_point
