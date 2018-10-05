import sys, platform
import os
import copy
import json


def initialize_setting(current_experiment, data='DIR-Lab_COPD', where_to_run='local', registration_method=''):
    setting = dict()
    setting['current_experiment'] = current_experiment
    setting['data'] = data
    setting['whereToRun'] = where_to_run  # 'local' , 'sharkCluster' , 'shark'
    setting['homeFolder'], setting['dataFolder'] = root_address_generator(setting)
    setting['ExpName'] = 'case'
    setting = load_setting_from_data(setting)
    setting = load_setting_from_registration_method(setting, registration_method=registration_method)
    setting['PoolingExeAddress'] = 'E:/PHD/Software/RF/Build/bg-oak2/apps/regression/Pooling/bin/Release/Pooling.exe'
    setting['NCMIExeAddress'] = 'E:/PHD/Software/RF/Build/bg-oak2/apps/regression/NCMI/bin/Release/NCMI.exe'
    setting['Pooling_MaxBoxSize'] = 60
    setting['Pooling_MinBoxSize'] = 2
    setting['MIND_name'] = 'DiffMindSparseSAD'
    setting['CV_name'] = 'CV6_64Smooth11_E5'
    setting['NCMI_MaxBoxSize'] = 40
    setting['NCMI_MinBoxSize'] = 5
    setting['neighborhood_radius'] = 0

    return setting


def load_setting_from_data(setting):
    if setting['data'] == 'DIR-Lab_COPD':
        # general
        setting['numberOfThreads'] = 1
        setting['verboseImage'] = True

        # naming
        setting['types'] = ['i', 'e']
        setting['ExpName'] = 'copd'
        setting['originalImageFolder'] = 'mha'
        setting['pointsFolder'] = 'points'

        # image properties
        setting['dimension'] = 3
        setting['defaultPixelValue'] = -2048
        setting['imageByte'] = 2    # sitk.sitkInt16 , we prefer not to import sitk in SettingUtils
        setting['cn_range'] = [i for i in range(1, 11)]  # list of image pairs in this database

        # general registration
        setting['useMask'] = True

        # inital perturbation
        setting['GridSpacing'] = [10, 10, 10]
        setting['GridBorderToZero'] = [3, 3, 3]
        setting['perturbationOffset'] = 2
        setting['out_max'] = 20     # number of registrations

        # final perturbation
        setting['GridSpacing_final'] = [10, 10, 10]
        setting['GridBorderToZero_final'] = [3, 3, 3]
        setting['perturbationOffset_final'] = 2
        setting['out_max_final'] = 20  # number of registrations

        # cluster SGE config
        setting['cluster_queue'] = 'all.q'
        setting['cluster_memory'] = '25G'
        setting['cluster_task_dependency'] = True
        setting['cluster_phase'] = None  # 0: affine, 1: initial perturb + BSpline_SyN, 2:final perturb + BSpline_Syn
    return setting


def load_setting_from_registration_method(setting, registration_method=''):
    setting['registration_method'] = registration_method
    if registration_method == 'ANTs':
        setting['ext'] = '.nii'
        setting['registration_output'] = 'DVF'
    elif registration_method == 'elastix':
        setting['registration_output'] = 'DVF'
        setting['ext'] = '.mha'
    else:
        setting['ext'] = '.mha'
        setting['registration_output'] = 'DVF'
    return setting


def root_address_generator(setting, force_to=None):
    # force_to : 'PC', 'linux', 'shark'
    if (sys.platform == 'win32' and force_to is None) or force_to == 'PC':
        home_folder = 'E:/PHD/Software/Project/Uncertainty_Reg/'
        data_folder = 'E:/PHD/Database/'

    elif (sys.platform == 'cygwin' and force_to is None) or force_to == 'PC_cygwin':
        home_folder = '/cygdrive/e/PHD/Software/Project/Uncertainty_Reg/'
        data_folder = '/cygdrive/e/PHD/Database/'

    elif ((setting['whereToRun'] == 'sharkCluster' or setting['whereToRun'] == 'shark') and force_to is None) or force_to == 'shark':
        home_folder = '/exports/lkeb-hpc/hsokootioskooyi/Uncertainty_Reg/'
        data_folder = '/exports/lkeb-hpc/hsokootioskooyi/Data/'

    elif (sys.platform == 'linux' and force_to is None) or force_to == 'linux':
        home_folder = '/srv/' + platform.node() + '/hsokooti/Uncertainty_Reg/'
        data_folder = '/srv/' + platform.node() + '/hsokooti/Data/'

    else:
        raise ValueError('platform='+sys.platform+' not recognizable. should be in ["win32", "cygwin", "linux", "sharkCluster"]')
    return home_folder, data_folder


def address_generator(s, requested_address, cn=None, out=None, outfinal=None, type_im=None, print_mode=False, force_to=None,
                      neighborhood_radius=None, unzip=False, current_experiment=None, job_extension=None, feature='',
                      regression_name=None, rf_spec=None, reg_step=0, data=None):
    if data is None:
        data = s['data']

    if current_experiment is None:
        current_experiment = s['current_experiment']
    else:
        if s['current_experiment'] != current_experiment:
            # for instance in ANTs registration the extension is 'nii' but in elastix the extenstion is 'mha'
            # when using affine of elastix in ANTs, each of them should have their own extension.
            setting_current_experiment = load_setting(current_experiment, data=data, where_to_run=s['whereToRun'])
            if type(setting_current_experiment) is dict:
                if 'ext' in setting_current_experiment.keys():
                    s = copy.deepcopy(s)
                    s['ext'] = setting_current_experiment['ext']
    if force_to is None:
        home_folder = s['homeFolder']
        data_folder = s['dataFolder']
    else:
        home_folder, data_folder = root_address_generator(s, force_to=force_to)

    address = {}
    name_dic = {}

    if data == 'DIR-Lab_COPD':
        original_folder = data_folder + 'DIR-Lab/COPDgene/'
        if job_extension is None:
            job_extension = '$JOB_ID'
    else:
        raise ValueError('implementation is done only for data"DIR-Lab_COPD". Please add other settings.')

    address['experimentRootFolder'] = home_folder + 'Elastix/' + data + '/' + current_experiment + '/'
    address['ExpFolder'] = address['experimentRootFolder'] + s['ExpName'] + str(cn) + '/'
    if print_mode:
        address['experimentRootFolder'] = data + '/' + current_experiment + '/'
        address['ExpFolder'] = address['experimentRootFolder'] + s['ExpName'] + str(cn) + '/'
        home_folder = ''

    if requested_address in ['originalImageFolder', 'Im', 'Im_Normalized', 'Im_Masked_Normalized', 'Cylinder', 'Torso', 'Lung_Initial', 'Lung_Filled', 'Lung_Filled_Erode', 'Lung_Manual', 'Lung_Atlas']:
        address['originalImageFolder'] = original_folder + s['originalImageFolder'] + '/'
        if requested_address not in ['originalImageFolder']:
            name_dic['Im'] = 'copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Im_Normalized'] = 'Normalized/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Im_Masked_Normalized'] = 'Masked_Normalized/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Cylinder'] = 'Cylinder/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Torso'] = 'Torso/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Lung_Initial'] = 'Lung_Initial/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Lung_Filled'] = 'Lung_Filled/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Lung_Filled_Erode'] = 'Lung_Filled_Erode/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Lung_Manual'] = 'Lung_Manual/copd' + str(cn) + '_' + s['types'][type_im] + 'BHCT'
            name_dic['Lung_Atlas'] = 'Lung_Atlas/copd' + str(cn).zfill(2) + '_' + s['types'][type_im] + 'BHCT' + '_Both_Lung_Mask'
            address[requested_address] = address['originalImageFolder'] + name_dic[requested_address] + '.mha'

    elif requested_address in ['originalPointFolder', 'landmarkIndex_tr', 'landmarkIndex_elx', 'landmarkPoint_tr', 'landmarkPoint_elx']:
        address['originalPointFolder'] = original_folder + s['pointsFolder'] + '/'
        name_dic['landmarkIndex_tr'] = 'copd' + str(cn) + '_300_' + s['types'][type_im] + 'BH_xyz_r1_tr.txt'
        name_dic['landmarkPoint_tr'] = 'copd' + str(cn) + '_300_' + s['types'][type_im] + 'BH_world_r1_tr.txt'
        name_dic['landmarkIndex_elx'] = 'copd' + str(cn) + '_300_' + s['types'][type_im] + 'BH_xyz_r1_elx.txt'
        name_dic['landmarkPoint_elx'] = 'copd' + str(cn) + '_300_' + s['types'][type_im] + 'BH_world_r1_elx.txt'
        if requested_address not in ['originalPointFolder']:
            address[requested_address] = address['originalPointFolder'] + name_dic[requested_address]

    elif requested_address in ['BSplineGridFolder', 'BSplineGridTransform']:
        address['BSplineGridFolder'] = address['ExpFolder'] + 'BSplineGrid/'
        address['BSplineGridTransform'] = address['BSplineGridFolder'] + 'TransformParameters.0.txt'

    elif requested_address in ['affineFolder', 'affineFolderOld', 'affineScript', 'affineOut', 'affineTransformScript', 'affineOutMat',
                               'affineDVF', 'affineJobOut', 'affine_MovedImage', 'affineTransformMovedImageScript',
                               'affineTransformParameter']:
        address['affineFolder'] = address['ExpFolder'] + 'Affine' + str(reg_step) + '/'
        address['affineFolderOld'] = address['ExpFolder'] + 'OAfterS/'
        address['affineScript'] = address['affineFolder'] + 'affineScirpt.sh'
        address['affineOut'] = address['affineFolder'] + 'affineOut'
        address['affineTransformScript'] = address['affineFolder'] + 'affineTransformScript.sh'
        address['affineOutMat'] = address['affineFolder'] + 'affineOut0GenericAffine.mat'
        address['affineDVF'] = address['affineFolder'] + 'deformationField' + s['ext']
        address['affineJobOut'] = address['affineFolder'] + 'jobOut.' + job_extension
        address['affine_MovedImage'] = address['affineFolder'] + 'result.0' + s['ext']
        address['affineTransformMovedImageScript'] = address['affineFolder'] + 'affineTransformMovedImageScript.sh'
        address['affineTransformParameter'] = address['affineFolder'] + 'TransformParameters.0.txt'

    elif requested_address in ['nonRigidFolder', 'DVF_perturb_without_affine', 'DVF_perturb', 'DVF_nonRigid', 'nonRigidScript',
                               'nonRigidJobOut', 'nonRigidTransformScript', 'DVF_nonRigid0', 'DVF_nonRigid1', 'DVF_nonRigid_composed',
                               'nonRigid_MovedImage', 'nonRigid_MovedImage_mha', 'nonRigid_MovedImage2', 'nonRigidTransformMovedImageScript',
                               'BSplineGrid', 'BSplinePerturb', 'BSplineTransformParameter']:
        name_dic['DVF_nonRigid'] = 'DVF_nonRigid'
        address['nonRigidFolder'] = address['ExpFolder'] + 'out' + str(out) + '/'
        address['DVF_nonRigid'] = address['nonRigidFolder'] + name_dic['DVF_nonRigid']
        address['nonRigidScript'] = address['nonRigidFolder'] + 'nonRigidScript.sh'
        address['nonRigidJobOut'] = address['nonRigidFolder'] + 'jobOut.' + job_extension
        address['DVF_perturb_without_affine'] = address['nonRigidFolder'] + 'DVF_perturb_without_affine' + s['ext']
        address['BSplinePerturb'] = address['nonRigidFolder'] + 'BSplinePerturb.txt'
        address['DVF_perturb'] = address['nonRigidFolder'] + 'DVF_perturb' + s['ext']
        address['BSplineGrid'] = address['nonRigidFolder'] + 'BSplineGrid' + s['ext']
        address['nonRigidTransformScript'] = address['nonRigidFolder'] + 'nonRigidTransformScript.sh'
        dvf_ext = '.nii.gz'
        if unzip:
            dvf_ext = '.nii'
        address['DVF_nonRigid0'] = address['nonRigidFolder'] + name_dic['DVF_nonRigid'] + '0Warp' + dvf_ext
        address['DVF_nonRigid1'] = address['nonRigidFolder'] + name_dic['DVF_nonRigid'] + '1Warp' + dvf_ext
        address['DVF_nonRigid_composed'] = address['nonRigidFolder'] + 'deformationField' + s['ext']
        address['nonRigid_MovedImage'] = address['nonRigidFolder'] + 'result.0' + s['ext']
        address['nonRigid_MovedImage_mha'] = address['nonRigidFolder'] + 'result.0' + '.mha'
        address['nonRigidTransformMovedImageScript'] = address['nonRigidFolder'] + 'nonRigidTransformMovedImageScript.sh'
        address['BSplineTransformParameter'] = address['nonRigidFolder'] + 'TransformParameters.0.txt'

    elif requested_address in ['nonRigidFolder_final', 'nonRigidScript_final', 'nonRigidJobOut_final', 'DVF_nonRigid_final', 'DVF_perturb_pure_final', 'DVF_perturb_final',
                               'nonRigidTransformScript_final', 'DVF_nonRigid0_final', 'DVF_nonRigid1_final', 'DVF_nonRigid_composed_final', 'nonRigid_MovedImage_final',
                               'BSplinePerturb_final', 'BSplineTransformParameter_final']:
        name_dic['DVF_nonRigid_final'] = 'DVF_nonRigid_final'
        address['nonRigidFolder_final'] = address['ExpFolder'] + 'outfinal' + str(outfinal) + '/'
        address['nonRigidScript_final'] = address['nonRigidFolder_final'] + 'nonRigidScript_final.sh'
        address['nonRigidJobOut_final'] = address['nonRigidFolder_final'] + 'jobOut.' + job_extension
        address['DVF_nonRigid_final'] = address['nonRigidFolder_final'] + name_dic['DVF_nonRigid_final']
        address['DVF_perturb_pure_final'] = address['nonRigidFolder_final'] + 'DVF_perturb_pure_final' + s['ext']
        address['DVF_perturb_final'] = address['nonRigidFolder_final'] + 'DVF_perturb_final' + s['ext']
        address['BSplinePerturb_final'] = address['nonRigidFolder_final'] + 'BSplinePerturb_final.txt'

        address['nonRigidTransformScript_final'] = address['nonRigidFolder_final'] + 'nonRigidTransformScript_final.sh'
        address['DVF_nonRigid0_final'] = address['nonRigidFolder_final'] + name_dic['DVF_nonRigid_final'] + '0Warp.nii.gz'
        address['DVF_nonRigid1_final'] = address['nonRigidFolder_final'] + name_dic['DVF_nonRigid_final'] + '1Warp.nii.gz'
        address['DVF_nonRigid_composed_final'] = address['nonRigidFolder_final'] + 'deformationField' + s['ext']
        address['nonRigid_MovedImage_final'] = address['nonRigidFolder_final'] + 'result.0' + s['ext']
        address['BSplineTransformParameter_final'] = address['nonRigidFolder_final'] + 'TransformParameters.0.txt'

    elif requested_address in ['ResultFolder', 'PoolFolder', 'errorImage', 'errorImageMask', 'errorImageAffine',
                               'stdT', 'E_T', 'stdT_final', 'E_T_final', 'Jac', 'MIND', 'CV', 'NCMI',
                               'PoolingConfig', 'PooledFeature']:
        if neighborhood_radius is None:
            neighborhood_radius = s['neighborhood_radius']
        address['ResultFolder'] = address['ExpFolder'] + 'Result/'
        address['PoolFolder'] = address['ResultFolder'] + 'Pooled/'
        if not (os.path.exists(address['ResultFolder']) or print_mode):
            os.makedirs(address['ResultFolder'])
        address['errorImage'] = address['ResultFolder'] + 'errorImage_r' + str(neighborhood_radius) + '.mha'
        address['errorImageMask'] = address['ResultFolder'] + 'errorImageMask_r' + str(neighborhood_radius) + '.mha'
        address['errorImageAffine'] = address['ResultFolder'] + 'errorImageAffine_r' + str(neighborhood_radius) + '.mha'
        if requested_address in ['stdT', 'E_T', 'stdT_final', 'E_T_final', 'Jac']:
            name_dic[requested_address] = requested_address
            address[requested_address] = address['ResultFolder'] + name_dic[requested_address] + '.mha'
        address['MIND'] = address['ResultFolder'] + s['MIND_name'] + '.mha'
        address['CV'] = address['ResultFolder'] + s['CV_name'] + '.mha'
        address['PoolingConfig'] = address['PoolFolder']+'config_'+feature+'_r'+str(neighborhood_radius)+'.txt'
        address['PooledFeature'] = address['PoolFolder']+'pooled_'+feature+'_r'+str(neighborhood_radius)+'.bin'

    elif requested_address in ['reportFolder', 'ReportFeatureFolder', 'TRE_BoxPlot_cn', 'TRE_BoxPlot_Merged', 'TRE_Table_Merged', 'TRE_Table_cn',
                               'landmark_file', 'FeatureScatter', 'FeatureScatterSort', 'FeatureBoxPlot', 'setting_file', 'LossPlot', 'LossPlotItr']:
        address['reportFolder'] = address['experimentRootFolder'] + 'Report/'
        address['ReportFeatureFolder'] = address['reportFolder'] + 'Feature/'
        address['TRE_BoxPlot_cn'] = address['reportFolder'] + 'TRE_BoxPlot_cn.png'
        address['TRE_BoxPlot_Merged'] = address['reportFolder'] + 'TRE_BoxPlot_Merged.png'
        address['TRE_Table_Merged'] = address['reportFolder'] + 'TRE_Table_Merged.png'
        address['TRE_Table_cn'] = address['reportFolder'] + 'TRE_Table_cn.png'
        address['FeatureScatter'] = address['ReportFeatureFolder'] + feature + '_Scatter.png'
        address['FeatureScatterSort'] = address['ReportFeatureFolder'] + feature + '_Sort.png'
        address['FeatureBoxPlot'] = address['ReportFeatureFolder'] + feature + '_BoxPlot.png'
        address['LossPlot'] = address['reportFolder'] + 'cn' + str(cn) + '_LossPlot.png'
        address['LossPlotItr'] = address['reportFolder'] + 'cn' + str(cn) + '_LossPlotItr.png'
        address['landmark_file'] = address['reportFolder'] + 'landmark.pkl'
        address['setting_file'] = address['reportFolder'] + 'setting'

    elif requested_address in ['ParameterFolder']:
        address['ParameterFolder'] = address['experimentRootFolder'] + 'parameter/'

    elif requested_address in ['RegressionFolder', 'RegressionModelFolder', 'RegressionResult_MAT', 'RegressionResult_png', 'RegressionResult_name']:
        address['RegressionFolder'] = home_folder + 'Elastix/Regression/' + current_experiment + '/'
        address['RegressionModelFolder'] = home_folder + 'Elastix/Regression/Model/'
        if requested_address in ['RegressionResult_MAT', 'RegressionResult_png', 'RegressionResult_name']:
            address['RegressionResult_name'] = regression_name + '_' + rf_spec
            address['RegressionResult_MAT'] = address['RegressionFolder'] + 'MAT/' + address['RegressionResult_name'] + '.mat'
            address['RegressionResult_png'] = address['RegressionFolder'] + 'MAT/' + address['RegressionResult_name'] + '.png'

    if requested_address in address.keys():
        return address[requested_address]
    else:
        return None


def exp_info():
    exp_dict = {'elastix1-TRE_nonrigid': 'Affine: elastix1(Torso), Lung-Filled, itr2000',
                'ANTs1-TRE_nonrigid': 'Affine:elastix1(Torso), MaskedNormalizedIm, 4R, s:0.1, cth:1-e-6,',
                }
    return exp_dict


def get_feature_set(feature_set_name):
    feature_set = {'combined': ['stdT_pooled', 'stdT_final_pooled', 'CV_pooled', 'MIND_pooled', 'E_T_pooled', 'E_T_final_pooled', 'MI_pooled', 'Jac_pooled'],
                   'intensity': ['MIND_pooled', 'MI_pooled'],
                   'registration': ['stdT_pooled', 'stdT_final_pooled', 'CV_pooled', 'E_T_pooled', 'E_T_final_pooled', 'Jac_pooled']
                   }
    return feature_set[feature_set_name]


def write_setting(setting):
    setting_name = address_generator(setting, 'setting_file').rsplit('/', maxsplit=1)[1]
    setting_folder = address_generator(setting, 'setting_file').rsplit('/', maxsplit=1)[0] + '/'
    if not os.path.isdir(setting_folder):
        os.makedirs(setting_folder)
    setting_number = 0
    setting_address = setting_folder + setting_name + str(setting_number) + '.txt'
    while os.path.isfile(setting_address):
        setting_number = setting_number + 1
        setting_address = setting_folder + setting_name + str(setting_number) + '.txt'
    with open(setting_address, 'w') as file:
        file.write(json.dumps(setting, sort_keys=True, indent=4, separators=(',', ': ')))


def load_setting(current_experiment, data=None, where_to_run=None):
    setting = initialize_setting(current_experiment, data=data, where_to_run=where_to_run)
    setting_folder = address_generator(setting, 'reportFolder')
    if not os.path.isdir(setting_folder):
        os.makedirs(setting_folder)
    setting_file_list = []
    for file in os.listdir(setting_folder):
        if 'setting' in file:
            setting_file_list.append(file)
    if len(setting_file_list) == 0:
        print(current_experiment + ': no setting file found')
        return 0
    else:
        if len(setting_file_list) == 1:
            selected_setting = 0
        elif len(setting_file_list) > 1:
            selected_setting = -1
            print(current_experiment + ': multiple setting files are found, selected_setting: ' + setting_file_list[selected_setting])
        setting_address = setting_folder + setting_file_list[selected_setting]
        with open(setting_address, 'r') as f:
            setting = json.load(f)
        # update the setting path if whereToRun is changed
        setting['whereToRun'] = where_to_run  # 'local' , 'sharkCluster' , 'shark'
        setting['homeFolder'], setting['dataFolder'] = root_address_generator(setting)

        setting = add_ants_parameter_setting(setting)
        return setting


def add_ants_parameter_setting(setting):
    return setting
