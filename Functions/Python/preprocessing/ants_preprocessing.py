import os
import numpy as np
import SimpleITK as sitk
import Functions.Python.setting_utils as su
import Functions.Python.image_processing as ip


def image_normalization(setting, cn=None, mask_name='Lung_Filled_Erode'):
    normalized_folder = su.address_generator(setting, 'originalImageFolder') + 'Normalized/'
    if not os.path.isdir(normalized_folder):
        os.makedirs(normalized_folder)
    normalized_erode_folder = su.address_generator(setting, 'originalImageFolder') + 'Masked_Normalized/'
    if not os.path.isdir(normalized_erode_folder):
        os.makedirs(normalized_erode_folder)
    for type_im in range(len(setting['types'])):
        im_sitk = sitk.ReadImage(su.address_generator(setting, 'Im', type_im=type_im, cn=cn))
        im = sitk.GetArrayFromImage(im_sitk)
        mask = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, mask_name, type_im=type_im, cn=cn)))
        im_masked = im * mask
        min_im = np.min(im_masked)
        max_im = np.max(im_masked)
        slop = 1.0/(max_im-min_im)
        intercept = -min_im/(max_im-min_im)
        im_masked_normalized = 1 - (im_masked-min_im)/(max_im-min_im)
        im_masked_normalized = im_masked_normalized * mask
        im_masked_normalized_sitk = ip.array_to_sitk(im_masked_normalized, im_ref=im_sitk)
        sitk.WriteImage(im_masked_normalized_sitk, su.address_generator(setting, 'Im_Masked_Normalized', type_im=type_im, cn=cn))
        print('writing '+su.address_generator(setting, 'Im_Masked_Normalized', type_im=type_im, cn=cn, print_mode=True))
        print('slop: {:.6f}, intercept: {:.6f}'.format(slop, intercept))
