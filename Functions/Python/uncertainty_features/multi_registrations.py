import os
import numpy as np
import Functions.Python.setting_utils as su
import SimpleITK as sitk
import Functions.Python.image_processing as ip
import logging
import time
import pickle


def std_t(setting, cn=None, max_number_of_registration=None, mode='initial'):
    """
    This function writes stdT, E_T or stdT_final, E_T_final. mode can be chosen between 'initial' and 'final'
    mode = 'initial' ---->>  write stdT, E_T
    mode = 'final' ---->>  write stdT_final, E_T_final

    :param setting: setting dictionary
    :param cn:  number of the case
    :param max_number_of_registration:  maximum number of registration. By default it is supposed to be written in the setting dict.
    :param mode:   'initial' or 'final'
    :return: write stdT, E_T or stdT_final, E_T_final
    """

    time_before = time.time()
    all_dvf_available = True
    if mode == 'initial':
        name_ext = ''  # no extentension in the naming of initial mode, for eg: DVF_nonRigid_composed, stdT
        if max_number_of_registration is None:
            max_number_of_registration = setting['out_max']
        if os.path.isfile(su.address_generator(setting, 'stdT' + name_ext, cn=cn)):
            logging.debug('multi_registration.std_t: already exists: ' + su.address_generator(setting, 'stdT' + name_ext, cn=cn, print_mode=True))
            return 1
        else:
            for out in range(1, max_number_of_registration+1):
                all_dvf_available = all_dvf_available & os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed' + name_ext, cn=cn, out=out))
    elif mode == 'final':
        name_ext = '_final'  # _final extentension in the naming of final mode, , for eg: DVF_nonRigid_composed_final, stdT_final
        if max_number_of_registration is None:
            max_number_of_registration = setting['out_max_final']
        if os.path.isfile(su.address_generator(setting, 'stdT' + name_ext, cn=cn)):
            logging.debug('multi_registration.std_t: already exists: ' + su.address_generator(setting, 'stdT' + name_ext, cn=cn, print_mode=True))
            return 1
        else:
            for outfinal in range(1, max_number_of_registration+1):
                all_dvf_available = all_dvf_available & os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed' + name_ext, cn=cn, outfinal=outfinal))
    else:
        raise ValueError('mode is set to '+mode+' but is should be either "initial" or "final"')

    if all_dvf_available:
        logging.debug('multi_registration.stdT: start calculating stdT' + name_ext + ' IN={}'.format(cn))
        dimension = setting['dimension']

        dvf0 = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=0)))
        dvf_all = [None] * dimension
        dvf_var = [None] * dimension
        dvf_mean = [None] * dimension
        for dim in range(3):
            dvf_all[dim] = np.empty(np.r_[np.shape(dvf0)[:-1], max_number_of_registration], dtype=np.float32)
        for out in range(1, max_number_of_registration+1):
            if mode == 'initial':
                dvf_ = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'DVF_nonRigid_composed' + name_ext, cn=cn, out=out)))
                logging.debug('multi_registration.stdT: reading: ' + su.address_generator(setting, 'DVF_nonRigid_composed' + name_ext, cn=cn, out=out, print_mode=True))
            elif mode == 'final':
                dvf_ = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'DVF_nonRigid_composed' + name_ext, cn=cn, outfinal=out)))
                logging.debug('multi_registration.stdT: reading: ' + su.address_generator(setting, 'DVF_nonRigid_composed' + name_ext, cn=cn, outfinal=out, print_mode=True))
            for dim in range(dimension):
                dvf_all[dim][:, :, :, out-1] = dvf_[:, :, :, dim]

        for dim in range(dimension):
            dvf_var[dim] = (np.var(dvf_all[dim], axis=dimension)).astype(np.float32)
            dvf_mean[dim] = (np.mean(dvf_all[dim], axis=dimension)).astype(np.float32)

        std_t = np.sqrt(sum(dvf_var))
        E_T = (np.sqrt(np.sum(np.square([dvf_mean[dim] - dvf0[:, :, :, dim] for dim in range(dimension)]), axis=0))).astype(np.float32)
        fixed_image_sitk = sitk.ReadImage(su.address_generator(setting, 'Im', cn=cn, type_im=0))
        sitk.WriteImage(ip.array_to_sitk(std_t, im_ref=fixed_image_sitk), su.address_generator(setting, 'stdT' + name_ext, cn=cn))
        sitk.WriteImage(ip.array_to_sitk(E_T, im_ref=fixed_image_sitk), su.address_generator(setting, 'E_T' + name_ext, cn=cn))
        time_after = time.time()
        logging.debug('multi_registration.stdT: calculating stdT' + name_ext + ' IN={} is done in {:.2f}'.format(cn, time_after - time_before))
    else:
        logging.debug('multi_registration.std_t: all dvf are not available: '+su.address_generator(setting, 'stdT' + name_ext, cn=cn, print_mode=True))


def jac(setting, cn=None):
    time_before = time.time()
    dvf_sitk = sitk.ReadImage(su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=0))
    jac = ip.calculate_jac(sitk.GetArrayFromImage(dvf_sitk), dvf_sitk.GetSpacing())
    sitk.WriteImage(sitk.Cast(ip.array_to_sitk(jac, im_ref=dvf_sitk), sitk.sitkVectorFloat32),
                    su.address_generator(setting, 'Jac', cn=cn))
    time_after = time.time()
    logging.debug('multi_registration: calculating Jac cn={} is done in {:.2f}'.format(cn, time_after - time_before))


def feature_pooling(setting, cn=None, feature_list=None, pooling_executable=None, neighborhood_radius=None):
    time_before = time.time()
    if pooling_executable is None:
        pooling_executable = setting['PoolingExeAddress']
    if not os.path.isdir(su.address_generator(setting, 'PoolFolder', cn=cn)):
        os.makedirs(su.address_generator(setting, 'PoolFolder', cn=cn))
    for feature in feature_list:
        config_file = su.address_generator(setting, 'PoolingConfig', cn=cn, feature=feature, neighborhood_radius=neighborhood_radius)
        config_str = 'image=' + su.address_generator(setting, feature, cn=cn) + '\n'
        config_str = config_str +'mask=' + su.address_generator(setting, 'errorImageMask', cn=cn, neighborhood_radius=neighborhood_radius) + '\n'
        config_str = config_str +'output=' + su.address_generator(setting, 'PoolFolder', cn=cn) + '\n'
        config_str = config_str+'max_boxsize='+str(setting['Pooling_MaxBoxSize'])+'\n'
        config_str = config_str+'min_boxsize='+str(setting['Pooling_MinBoxSize'])+'\n'
        config_str = config_str+'abs_intensity_features=1'+'\n'
        with open(config_file, "w") as text_str:
            text_str.write(config_str)
        pooled_feature_address = su.address_generator(setting, 'PooledFeature', feature=feature, cn=cn, neighborhood_radius=neighborhood_radius)
        pooled_feature_pure_address = pooled_feature_address.rsplit('/', maxsplit=1)[1]
        pooling_cmd = pooling_executable+' --config '+config_file+' '+pooled_feature_pure_address
        os.system(pooling_cmd)
    time_after = time.time()
    logging.debug('multi_registration: Pooling cn={} is done in {:.2f}'.format(cn, time_after - time_before))


def ncmi(setting, cn=None, ncmi_executable=None, neighborhood_radius=None):
    time_before = time.time()
    if ncmi_executable is None:
        ncmi_executable = setting['NCMIExeAddress']
    if not os.path.isdir(su.address_generator(setting, 'PoolFolder', cn=cn)):
        os.makedirs(su.address_generator(setting, 'PoolFolder', cn=cn))
    feature = 'NCMI'
    config_file = su.address_generator(setting, 'PoolingConfig', cn=cn, feature=feature, neighborhood_radius=neighborhood_radius)
    config_str = 'images=' + su.address_generator(setting, 'Im', cn=cn, type_im=0) + ' ' + \
                 su.address_generator(setting, 'nonRigid_MovedImage', cn=cn, out=0) + '\n'
    config_str = config_str +'mask=' + su.address_generator(setting, 'errorImageMask', cn=cn, neighborhood_radius=neighborhood_radius) + '\n'
    config_str = config_str +'output=' + su.address_generator(setting, 'PoolFolder', cn=cn) + '\n'
    config_str = config_str+'max_boxsize='+str(setting['NCMI_MaxBoxSize'])+'\n'
    config_str = config_str+'min_boxsize='+str(setting['NCMI_MinBoxSize'])+'\n'
    config_str = config_str+'abs_intensity_features=1'+'\n'
    with open(config_file, "w") as text_str:
        text_str.write(config_str)
    pooled_feature_address = su.address_generator(setting, 'PooledFeature', feature=feature, cn=cn, neighborhood_radius=neighborhood_radius)
    pooled_feature_pure_address = pooled_feature_address.rsplit('/', maxsplit=1)[1]
    pooling_cmd = ncmi_executable+' --config '+config_file+' '+pooled_feature_pure_address
    os.system(pooling_cmd)
    time_after = time.time()
    logging.debug('multi_registration: NCMMI cn={} is done in {:.2f}'.format(cn, time_after - time_before))
