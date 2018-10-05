import os
import numpy as np
import Functions.Python.setting_utils as su
import SimpleITK as sitk
import Functions.Python.elastix_python as elxpy
import Functions.Python.image_processing as ip
import logging


def compute_error(setting, cn=None, write_error_image=True):
    if (os.path.isfile(su.address_generator(setting, 'errorImage', cn=cn)) &
         os.path.isfile(su.address_generator(setting, 'errorImageAffine', cn=cn)) &
         os.path.isfile(su.address_generator(setting, 'errorImageMask', cn=cn))):
        logging.debug(setting['current_experiment']+' cn:'+str(cn)+' all error images exist')
        return 1

    if not (os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=0))):
        logging.debug(setting['current_experiment']+' cn:'+str(cn)+' deformation field not found')
        return 2

    fixed_indices = np.loadtxt(su.address_generator(setting, 'landmarkIndex_tr', cn=cn, type_im=0), dtype=np.int)
    fixed_points = np.loadtxt(su.address_generator(setting, 'landmarkPoint_tr', cn=cn, type_im=0))
    moving_points = np.loadtxt(su.address_generator(setting, 'landmarkPoint_tr', cn=cn, type_im=1))
    if setting['registration_output'] == 'DVF':
        if 'affine_experiment_step' in setting.keys():
            affine_step = setting['affine_experiment_step']
        elif 'AffineParameter' in setting.keys():
            affine_step = len(setting['AffineParameter']) - 1
        else:
            affine_step = 0
        dvf_nonrigid = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=0)))
        dvf_affine = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'affineDVF', cn=cn,
                                                                                current_experiment=setting['affine_experiment'],
                                                                                reg_step=affine_step)))
        fixed_nonrigid_transformed_points = np.empty(np.shape(fixed_points))
        fixed_affine_transformed_points = np.empty(np.shape(fixed_points))
        for p in range(len(fixed_nonrigid_transformed_points)):
            fixed_nonrigid_transformed_points[p, :] = fixed_points[p, :] + [dvf_nonrigid[fixed_indices[p, 2], fixed_indices[p, 1], fixed_indices[p, 0], 0],
                                                                            dvf_nonrigid[fixed_indices[p, 2], fixed_indices[p, 1], fixed_indices[p, 0], 1],
                                                                            dvf_nonrigid[fixed_indices[p, 2], fixed_indices[p, 1], fixed_indices[p, 0], 2]]
            fixed_affine_transformed_points[p, :] = fixed_points[p, :] + [dvf_affine[fixed_indices[p, 2], fixed_indices[p, 1], fixed_indices[p, 0], 0],
                                                                          dvf_affine[fixed_indices[p, 2], fixed_indices[p, 1], fixed_indices[p, 0], 1],
                                                                          dvf_affine[fixed_indices[p, 2], fixed_indices[p, 1], fixed_indices[p, 0], 2]]
    elif setting['registration_output'] == 'elastix_transform_parameters':
        fixed_points_elx_address = su.address_generator(setting, 'landmarkIndex_elx', cn=cn, type_im=0)
        elxpy.transformix(parameter_file=su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=0),
                          output_directory=su.address_generator(setting, 'nonRigidFolder', cn=cn, out=0),
                          points=fixed_points_elx_address,
                          transformixPath='transformix')
        raise ValueError('not implemented yet')

    TRE_before_registration = (np.sum((fixed_affine_transformed_points - moving_points) ** 2, axis=1)) ** 0.5
    TRE = (np.sum((fixed_nonrigid_transformed_points - moving_points) ** 2, axis=1)) ** 0.5

    if write_error_image:
        logging.debug('compute_error: writing: ' + su.address_generator(setting, 'errorImage', cn=cn, print_mode=True))
        fixed_image_sitk = sitk.ReadImage(su.address_generator(setting, 'Im', cn=cn, type_im=0))
        error_image_nonrigid = np.zeros(fixed_image_sitk.GetSize()[::-1])
        error_image_affine = np.zeros(fixed_image_sitk.GetSize()[::-1])
        error_mask = np.zeros(fixed_image_sitk.GetSize()[::-1], dtype=np.int8)
        r = setting['neighborhood_radius']
        for p in range(len(fixed_indices)):
            error_image_affine[fixed_indices[p, 2] - r: fixed_indices[p, 2] + r + 1,
                               fixed_indices[p, 1] - r: fixed_indices[p, 1] + r + 1,
                               fixed_indices[p, 0] - r: fixed_indices[p, 0] + r + 1] = TRE_before_registration[p]
            error_image_nonrigid[fixed_indices[p, 2] - r: fixed_indices[p, 2] + r + 1,
                                 fixed_indices[p, 1] - r: fixed_indices[p, 1] + r + 1,
                                 fixed_indices[p, 0] - r: fixed_indices[p, 0] + r + 1] = TRE[p]
            error_mask[fixed_indices[p, 2] - r: fixed_indices[p, 2] + r + 1,
                       fixed_indices[p, 1] - r: fixed_indices[p, 1] + r + 1,
                       fixed_indices[p, 0] - r: fixed_indices[p, 0] + r + 1] = 1
        sitk.WriteImage(sitk.Cast(ip.array_to_sitk(error_image_nonrigid, im_ref=fixed_image_sitk), sitk.sitkFloat32), su.address_generator(setting, 'errorImage', cn=cn))
        sitk.WriteImage(sitk.Cast(ip.array_to_sitk(error_image_affine, im_ref=fixed_image_sitk), sitk.sitkFloat32), su.address_generator(setting, 'errorImageAffine', cn=cn))
        sitk.WriteImage(sitk.Cast(ip.array_to_sitk(error_mask, im_ref=fixed_image_sitk), sitk.sitkInt8), su.address_generator(setting, 'errorImageMask', cn=cn))
    return 0


