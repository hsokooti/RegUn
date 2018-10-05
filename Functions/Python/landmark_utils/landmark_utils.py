import copy
import logging
import numpy as np
import os
import pickle
import Functions.Python.setting_utils as su
import SimpleITK as sitk


def load_features(setting, landmarks=None, feature_list=None, cn_list=None,
                  pooled_feature_list_ref=None, image_feature_list_ref=None):
    """
    This function load all the features available in feature_list:
    First, it loads the landmarks file if available. By default, it does not overwrite features in this dictionary.
    Some feature are in image-based format: 'stdT', 'E_T', 'stdT_final', 'E_T_final', 'Jac', 'MIND', 'CV'. These features can be used directly for no-pool experiment.
    Some other features are only available within the landmark regions:  'NCMI', 'MI', 'NC'. In no-pool experiment, PMIS with the box size of 15mm is used. This is the 10th element in MI vector
    Finally, it writes the landmark dictionary to the disk
    :param setting:
    :param landmarks:
    :param feature_list:
    :param cn_list:
    :param pooled_feature_list_ref:
    :param image_feature_list_ref:
    :return:
    """
    if pooled_feature_list_ref is None:
        pooled_feature_list_ref = ['stdT', 'E_T', 'stdT_final', 'E_T_final', 'Jac', 'MIND', 'CV', 'NCMI', 'MI', 'NC']
    if image_feature_list_ref is None:
        image_feature_list_ref = ['stdT', 'E_T', 'stdT_final', 'E_T_final', 'Jac', 'MIND', 'CV']

    landmark_address = su.address_generator(setting, 'landmark_file')
    if landmarks is None:
        if os.path.isfile(landmark_address):
            with open(landmark_address, 'rb') as f:
                landmarks = pickle.load(f)
        else:
            landmarks = dict()
    for cn in cn_list:
        if 'cn'+str(cn) not in landmarks.keys():
            landmarks['cn' + str(cn)] = {}
        if len(list(set(['landmarkIndices', 'TRE_nonrigid', 'TRE_affine']) & set(landmarks['cn'+str(cn)].keys()))) < 3:
            error_mask = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'errorImageMask', cn=cn)))
            error_image_nonrigid = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'errorImage', cn=cn)))
            error_image_affine = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, 'errorImageAffine', cn=cn)))
            landmarks_indices = np.where(error_mask>0)
            landmarks['cn'+str(cn)]['landmarkIndices'] = landmarks_indices
            landmarks['cn'+str(cn)]['TRE_nonrigid'] = error_image_nonrigid[landmarks_indices]
            landmarks['cn' + str(cn)]['TRE_affine'] = error_image_affine[landmarks_indices]

        for feature in feature_list:
            if feature in image_feature_list_ref:
                if feature not in landmarks['cn'+str(cn)].keys():
                    feature_image = sitk.GetArrayFromImage(sitk.ReadImage(su.address_generator(setting, feature, cn=cn)))
                    landmarks['cn' + str(cn)][feature] = feature_image[landmarks['cn'+str(cn)]['landmarkIndices']]
                    logging.debug('cn={}'.format(cn) + ', feature= ' + feature + ' is loaded')
                else:
                    logging.debug('cn'+str(cn)+', feature '+feature+' is already existed in the landmarks dictionary')
            if feature in pooled_feature_list_ref:
                feature_pooled = feature + '_pooled'
                if feature_pooled not in landmarks['cn' + str(cn)].keys():
                    landmarks['cn' + str(cn)][feature_pooled] = read_binary_feature(setting, cn=cn, feature=feature)
                    if feature in ['MI', 'NC']:
                        if feature not in landmarks['cn' + str(cn)].keys():
                            if feature == 'MI':
                                landmarks['cn' + str(cn)][feature] = landmarks['cn' + str(cn)][feature_pooled][:, 10]
                                # In no-pool experiment, PMIS with the box size of 15mm is used. This is the 10th element in MI vector
                            if feature == 'NC':
                                landmarks['cn' + str(cn)][feature] = landmarks['cn' + str(cn)][feature_pooled][:, 0]
                    logging.debug('cn={}'.format(cn) + ', feature= ' + feature_pooled + ' is loaded')
                else:
                    logging.debug('cn' + str(cn) + ', feature ' + feature_pooled + ' is already existed in the landmarks dictionary')
    if not os.path.exists(su.address_generator(setting, 'reportFolder')):
        os.makedirs(su.address_generator(setting, 'reportFolder'))
    with open(landmark_address, 'wb') as f:
        pickle.dump(landmarks, f)
    return landmarks


def merge_landmarks(landmarks, cn_list=None):
    landmarks_merged = dict()
    cn_i = 0
    for cn in cn_list:
        if 'cn'+str(cn) in landmarks.keys():
            for key in landmarks['cn'+str(cn)].keys():
                if cn_i == 0:
                    landmarks_merged[key] = landmarks['cn' + str(cn)][key]
                elif cn_i > 0:
                        landmarks_merged[key] = np.concatenate((landmarks_merged[key], landmarks['cn' + str(cn)][key]), axis=0)
            cn_i = cn_i + 1
    return landmarks_merged


def read_landmarks_pkl(setting, cn_list=None, exp_tre_list=None, exp_list=None):
    all_landmarks = dict()
    all_landmarks_merged = dict()
    legend_list = []
    extra_exp_info = su.exp_info()
    if exp_tre_list is not None:
        exp_list = exp_tre_list
    for exp_full_name in exp_list:
        if exp_tre_list is None:
            exp = exp_full_name
            legend_text = exp_full_name
        else:
            exp = exp_full_name.rsplit('-', maxsplit=1)[0]
            legend_text = exp_full_name.rsplit('-', maxsplit=1)[1].rsplit('_')[1]
            legend_text = exp_full_name
        with open(su.address_generator(setting, 'landmark_file', current_experiment=exp), 'rb') as f:
            landmark_exp = pickle.load(f)
            all_landmarks[exp_full_name] = copy.deepcopy(landmark_exp)
            all_landmarks_merged[exp_full_name] = copy.deepcopy(merge_landmarks(landmark_exp, cn_list=cn_list))
        if exp_full_name in extra_exp_info.keys():
            legend_text = legend_text + ': ' + extra_exp_info[exp_full_name]
        # legend_text = '$' + legend_text + '_{' + exp.replace('_', '\_') + '}$'
        legend_text = legend_text
        legend_list.append(legend_text)
    return all_landmarks, all_landmarks_merged, legend_list


def read_binary_feature(setting, cn=None, feature=None):
    if feature in ['NCMI', 'NC', 'MI']:
        number_of_elements = 56
        feature_binary = 'NCMI'
        # 16:48 MI
        # 48:56 NC
        # Number of features in NCMI,
        #    outMI[0]: NMI
        #    outMI[1]: NMIS
        #    outMI[2]: PMI
        #    outMI[3]: PMIS
        #    outMI[4]: NMI->ITK
        #    outMI[5]: NMIS->ITK
        #    outMI[6]: NCR
    else:
        number_of_elements = 18
        feature_binary = feature
    fid = open(su.address_generator(setting, 'PooledFeature', feature=feature_binary, cn=cn), 'rb')
    data = np.fromfile(fid, np.float32)
    binary_feature = data.reshape(-1, number_of_elements, order='F')
    # order 'F' is double checked!
    if feature == 'MI':
        binary_feature = binary_feature[:, 16:48]
    if feature == 'NC':
        binary_feature = binary_feature[:, 48:56]
    return binary_feature


def prepare_feature_for_regression(setting, exp_dict=None, feature_set=None, cn_list=None):
    feature_array = None
    tre_array = None
    if exp_dict['data'] == 'DIR-Lab_COPD':
        setting_exp = su.initialize_setting(exp_dict['experiment'], data=exp_dict['data'])
        if cn_list is None:
            cn_list = setting_exp['cn_range']
        setting_exp['neighborhood_radius'] = int(exp_dict['neighborhood_radius'])
        landmarks, landmarks_merged, _ = read_landmarks_pkl(setting_exp, cn_list=cn_list, exp_list=[exp_dict['experiment']])
        feature_list = su.get_feature_set(feature_set)
        for i_feature, feature in enumerate(feature_list):
            if i_feature == 0:
                feature_array = landmarks_merged[exp_dict['experiment']][feature]
                tre_array = landmarks_merged[exp_dict['experiment']]['TRE_nonrigid']
            else:
                feature_array = np.concatenate((feature_array, landmarks_merged[exp_dict['experiment']][feature]), axis=1)

    else:
        raise ValueError('data: ' + exp_dict['data'] + ' is not valid')

    exp_dict_name = exp_dict['data'] + '_' + exp_dict['experiment'] + '_' + exp_dict['neighborhood_radius']
    if exp_dict['iteration'] is not None:
        exp_dict_name = exp_dict_name + '_itr'
        for itr in exp_dict['iteration']:
            exp_dict_name = exp_dict_name + '_' + str(itr)
    exp_dict_name = exp_dict_name + '_' + feature_set

    return feature_array, tre_array, exp_dict_name
