import os, sys
import Functions.Python.setting_utils as su
import Functions.Python.ANTs.ants_parameters as ANTsP
import Functions.Python.image_processing as IP
import SimpleITK as sitk
import numpy as np
import logging
import Functions.Python.sungrid_utils as sungrid


# import importlib
# importlib.reload(su)

def affine_ANTs(setting, cn=None):
    fixedIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=0)
    movingIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=1)
    affineFolder = su.address_generator(setting, 'affineFolder', cn=cn)
    if not os.path.exists(affineFolder):
        os.makedirs(affineFolder)

    output_name = su.address_generator(setting, 'affineOut', cn=cn)
    number_of_threads = setting['numberOfThreads']
    affine_script = su.address_generator(setting, 'affineScript', cn=cn)
    with open(affine_script, "w") as textScr:
        textScr.write(ANTsP.header_registration())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_fixed_image(fixedIm_address))
        textScr.write(ANTsP.write_moving_image(movingIm_address))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(output_name))
        if setting['useMask']:
            textScr.write(ANTsP.write_fixed_mask(su.address_generator(setting, setting['MaskName_Affine'][0], cn=cn, type_im=0)))
            textScr.write(ANTsP.write_moving_mask(su.address_generator(setting, setting['MaskName_Affine'][0], cn=cn, type_im=1)))
        textScr.write(ANTsP.affine_EMPIRE10(use_mask=setting['useMask']))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(affine_script, 0o774)
    os.system(affine_script)


def BSpline_SyN_ANTs(setting, cn=None, out=None):
    if 'ImageType_Registration' in setting.keys():
        image_type_registration = setting['ImageType_Registration']
    else:
        image_type_registration = 'Im'
    fixed_im_address = su.address_generator(setting, image_type_registration, cn=cn, type_im=0)
    moving_im_address = su.address_generator(setting, image_type_registration, cn=cn, type_im=1)
    output_name = su.address_generator(setting, 'DVF_nonRigid', cn=cn, out=out)
    initial_transform = su.address_generator(setting, 'DVF_perturb', cn=cn, out=out)
    number_of_threads = setting['numberOfThreads']
    nonrigid_script = su.address_generator(setting, 'nonRigidScript', cn=cn, out=out)
    folder_address = su.address_generator(setting, 'nonRigidFolder', cn=cn, out=out)
    if not os.path.exists(folder_address):
        os.makedirs(folder_address)
    with open(nonrigid_script, "w") as textScr:
        textScr.write(ANTsP.header_registration())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_fixed_image(fixed_im_address))
        textScr.write(ANTsP.write_moving_image(moving_im_address))
        textScr.write(ANTsP.write_initial_transform(initial_transform))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(output_name))
        if setting['useMask']:
            textScr.write(ANTsP.write_fixed_mask(su.address_generator(setting, setting['MaskName_BSpline'], cn=cn, type_im=0)))
            textScr.write(ANTsP.write_moving_mask(su.address_generator(setting, setting['MaskName_BSpline'], cn=cn, type_im=1)))
        if os.path.isfile(su.address_generator(setting, 'ParameterFolder') + setting['NonRigidParameter']):
            with open(su.address_generator(setting, 'ParameterFolder') + setting['NonRigidParameter'], 'r') as f_parameter:
                parameter_str = f_parameter.read()
            textScr.write('command="antsRegistration ' + parameter_str + '"')
        else:
            textScr.write(ANTsP.BSpline_SyN_EMPIRE10(setting))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(nonrigid_script, 0o774)
    os.system(nonrigid_script)


def bspline_syn_ants_final(setting, cn=None, outfinal=None):
    if 'ImageType_Registration' in setting.keys():
        image_type_registration = setting['ImageType_Registration']
    else:
        image_type_registration = 'Im'
    fixed_im_address = su.address_generator(setting, image_type_registration, cn=cn, type_im=0)
    moving_im_address = su.address_generator(setting, image_type_registration, cn=cn, type_im=1)
    output_name = su.address_generator(setting, 'DVF_nonRigid_final', cn=cn, outfinal=outfinal)
    initial_transform = su.address_generator(setting, 'DVF_perturb_final', cn=cn, outfinal=outfinal)
    number_of_threads = setting['numberOfThreads']
    nonrigid_script_final = su.address_generator(setting, 'nonRigidScript_final', cn=cn, outfinal=outfinal)
    with open(nonrigid_script_final, "w") as textScr:
        textScr.write(ANTsP.header_registration())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_fixed_image(fixed_im_address))
        textScr.write(ANTsP.write_moving_image(moving_im_address))
        textScr.write(ANTsP.write_initial_transform(initial_transform))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(output_name))
        if setting['useMask']:
            textScr.write(ANTsP.write_fixed_mask(su.address_generator(setting, setting['MaskName_BSpline_Final'], cn=cn, type_im=0)))
            textScr.write(ANTsP.write_moving_mask(su.address_generator(setting, setting['MaskName_BSpline_Final'], cn=cn, type_im=1)))
        if os.path.isfile(su.address_generator(setting, 'ParameterFolder') + setting['NonRigidParameter_final']):
            with open(su.address_generator(setting, 'ParameterFolder') + setting['NonRigidParameter_final'], 'r') as f_parameter:
                parameter_str = f_parameter.read()
            textScr.write('command="antsRegistration ' + parameter_str + '"')
        else:
            textScr.write(ANTsP.bspline_syn_empire10_final(setting))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(nonrigid_script_final, 0o774)
    os.system(nonrigid_script_final)


def affine_ANTs_transform(setting, cn=None):
    fixedIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=0)
    movingIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=1)
    affineOutMat = su.address_generator(setting, 'affineOutMat', cn=cn)
    affineDVF_address = su.address_generator(setting, 'affineDVF', cn=cn)
    number_of_threads = setting['numberOfThreads']
    affine_transform_script = su.address_generator(setting, 'affineTransformScript', cn=cn)
    with open(affine_transform_script, "w") as textScr:
        textScr.write(ANTsP.header_transform())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_input_image(movingIm_address))
        textScr.write(ANTsP.write_reference_image(fixedIm_address))
        textScr.write(ANTsP.write_transform_parameters(affineOutMat))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(affineDVF_address))
        textScr.write(ANTsP.write_default_pixel_value(setting['defaultPixelValue']))
        textScr.write(ANTsP.transform(number_of_transforms=1))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(affine_transform_script, 0o774)
    os.system(affine_transform_script)


def affine_ANTs_transform_image(setting, cn=None):
    fixedIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=0)
    movingIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=1)
    affineOutMat = su.address_generator(setting, 'affineOutMat', cn=cn)
    affine_MovedImage_address = su.address_generator(setting, 'affine_MovedImage', cn=cn)
    number_of_threads = setting['numberOfThreads']
    script = su.address_generator(setting, 'affineTransformMovedImageScript', cn=cn)

    with open(script, "w") as textScr:
        # please note that the last registration that you did, should be the first transform parameters
        textScr.write(ANTsP.header_transform())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_input_image(movingIm_address))
        textScr.write(ANTsP.write_reference_image(fixedIm_address))
        textScr.write(ANTsP.write_transform_parameters(affineOutMat))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(affine_MovedImage_address))
        textScr.write(ANTsP.write_default_pixel_value(setting['defaultPixelValue']))
        textScr.write(ANTsP.transform_image(number_of_transforms=1))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(script, 0o774)
    os.system(script)


def BSpline_SyN_ANTs_transform(setting, cn=None, out=None, number_of_transforms=2):
    if 'nonrigid_number_of_transform' in setting.keys():
        number_of_transforms = setting['nonrigid_number_of_transform']  # remove later
    fixedIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=0)
    movingIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=1)
    if number_of_transforms == 1:
        transform0 = su.address_generator(setting, 'DVF_nonRigid0', cn=cn, out=out)
    if number_of_transforms == 2:
        transform0 = su.address_generator(setting, 'DVF_nonRigid1', cn=cn, out=out)
        transform1 = su.address_generator(setting, 'DVF_nonRigid0', cn=cn, out=out)
    DVF_nonRigid_composed = su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=out)
    number_of_threads = setting['numberOfThreads']
    nonrigid_transform_script = su.address_generator(setting, 'nonRigidTransformScript', cn=cn, out=out)

    with open(nonrigid_transform_script, "w") as textScr:
        # please note that the last registration that you did, should be the first transform parameters
        textScr.write(ANTsP.header_transform())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_input_image(movingIm_address))
        textScr.write(ANTsP.write_reference_image(fixedIm_address))
        textScr.write(ANTsP.write_transform_parameters(transform0, transform_number=0))
        if number_of_transforms > 1:
            textScr.write(ANTsP.write_transform_parameters(transform1, transform_number=1))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(DVF_nonRigid_composed))
        textScr.write(ANTsP.write_default_pixel_value(setting['defaultPixelValue']))
        textScr.write(ANTsP.transform(number_of_transforms=number_of_transforms))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(nonrigid_transform_script, 0o774)
    os.system(nonrigid_transform_script)


def BSpline_SyN_ANTs_transform_image(setting, IN=None, out=None):
    fixedIm_address = su.address_generator(setting, 'Im', cn=IN, type_im=0)
    movingIm_address = su.address_generator(setting, 'Im', cn=IN, type_im=1)
    transform0 = su.address_generator(setting, 'DVF_nonRigid_composed', cn=IN, out=out)
    nonRigid_MovedImage_address = su.address_generator(setting, 'nonRigid_MovedImage', cn=IN, out=out)
    number_of_threads = setting['numberOfThreads']
    script = su.address_generator(setting, 'nonRigidTransformMovedImageScript', cn=IN, out=out)
    log = script + '_log'
    setLogFile(log)

    with open(script, "w") as textScr:
        # please note that the last registration that you did, should be the first transform parameters
        textScr.write(ANTsP.header_transform())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_input_image(movingIm_address))
        textScr.write(ANTsP.write_reference_image(fixedIm_address))
        textScr.write(ANTsP.write_transform_parameters(transform0))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(nonRigid_MovedImage_address))
        textScr.write(ANTsP.write_default_pixel_value(setting['defaultPixelValue']))
        textScr.write(ANTsP.transform_image(number_of_transforms=1))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(script, 0o774)
    os.system(script)


def convert_nii2mha(setting, cn=None, out_list=None):
    if out_list is None:
        out_list = np.arange(0,21)
    if setting['registration_method'] == 'ANTs':
        for out in out_list:
            moved_nii_address = su.address_generator(setting, 'nonRigid_MovedImage', cn=cn, out=out)
            moved_mha_address = su.address_generator(setting, 'nonRigid_MovedImage_mha', cn=cn, out=out)
            if os.path.isfile(moved_nii_address):
                if not os.path.isfile(moved_mha_address):
                    moved_nii_sitk = sitk.ReadImage(moved_nii_address)
                    sitk.WriteImage(moved_nii_sitk, moved_mha_address)
                    logging.debug('convert_nii2mha is done cn={}, out={}'.format(cn, out))
                else:
                    logging.debug('convert_nii2mha, nii exists: cn={}, out={}'.format(cn, out))


def BSpline_SyN_ANTs_final_transform(setting, cn=None, outfinal=None):
    fixedIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=0)
    movingIm_address = su.address_generator(setting, 'Im', cn=cn, type_im=1)
    transform1 = su.address_generator(setting, 'DVF_nonRigid0_final', cn=cn, outfinal=outfinal)
    transform0 = su.address_generator(setting, 'DVF_nonRigid1_final', cn=cn, outfinal=outfinal)
    DVF_nonRigid_composed = su.address_generator(setting, 'DVF_nonRigid_composed_final', cn=cn, outfinal=outfinal)
    number_of_threads = setting['numberOfThreads']
    script = su.address_generator(setting, 'nonRigidTransformScript_final', cn=cn, outfinal=outfinal)

    with open(script, "w") as textScr:
        # please note that the last registration that you did, should be the first transform parameters
        textScr.write(ANTsP.header_transform())
        textScr.write(ANTsP.write_number_of_threads(number_of_threads))
        textScr.write(ANTsP.write_input_image(movingIm_address))
        textScr.write(ANTsP.write_reference_image(fixedIm_address))
        textScr.write(ANTsP.write_transform_parameters(transform0, transform_number=0))
        textScr.write(ANTsP.write_transform_parameters(transform1, transform_number=1))
        textScr.write(ANTsP.write_dimension(setting['dimension']))
        textScr.write(ANTsP.write_output(DVF_nonRigid_composed))
        textScr.write(ANTsP.write_default_pixel_value(setting['defaultPixelValue']))
        textScr.write(ANTsP.transform(number_of_transforms=2))
        textScr.write(ANTsP.footer())
        textScr.close()
    os.chmod(script, 0o774)
    os.system(script)


def BSpline_SyN_ANTs_cleanup(setting, IN=None, out=None):
    if os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed', cn=IN, out=out)):
        os.remove(su.address_generator(setting, 'DVF_nonRigid0', cn=IN, out=out))
        os.remove(su.address_generator(setting, 'DVF_nonRigid1', cn=IN, out=out))
        if out > 0:
            os.remove(su.address_generator(setting, 'DVF_perturb_without_affine', cn=IN, out=out))


def BSpline_SyN_ANTs_cleanup_final(setting, cn=None, outfinal=None):
    if os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed_final', cn=cn, outfinal=outfinal)):
        os.remove(su.address_generator(setting, 'DVF_nonRigid0_final', cn=cn, outfinal=outfinal))
        os.remove(su.address_generator(setting, 'DVF_nonRigid1_final', cn=cn, outfinal=outfinal))
        os.remove(su.address_generator(setting, 'DVF_perturb_pure_final', cn=cn, outfinal=outfinal))


def perturbation(setting, cn=None, out=None, outfinal=None):
    affine_experiment = setting['affine_experiment']
    if out is None and outfinal is not None:
        mode = 'final_perturbation'
        out = 0
        folder_address = su.address_generator(setting, 'nonRigidFolder_final', cn=cn, outfinal=outfinal)
        ref_dvf_address = su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=0)
        DVF_perturb_address = su.address_generator(setting, 'DVF_perturb_final', cn=cn, outfinal=outfinal)
        DVF_perturb_pure_address = su.address_generator(setting, 'DVF_perturb_pure_final', cn=cn, outfinal=outfinal)
    elif outfinal is None and out is not None:
        mode = 'initial_perturbation'
        outfinal = 0
        folder_address = su.address_generator(setting, 'nonRigidFolder', cn=cn, out=out)
        ref_dvf_address = su.address_generator(setting, 'affineDVF', cn=cn, current_experiment=affine_experiment)
        # if affine_experiment is given, it loads the DVF from that experiment.
        DVF_perturb_address = su.address_generator(setting, 'DVF_perturb', cn=cn, out=out)
        DVF_perturb_pure_address = su.address_generator(setting, 'DVF_perturb_without_affine', cn=cn, out=out)
    else:
        raise ValueError('out and outfinal cannot be None at the same time')

    seedNumber = 10000 + 1000 * cn + out * 101 + outfinal * 4
    np.random.seed(seedNumber)
    if not os.path.exists(folder_address):
        os.makedirs(folder_address)
    ref_dvf_sitk = sitk.ReadImage(ref_dvf_address)
    if mode == 'initial_perturbation' and out == 0:
        # when out=0, there is no perturbation, so the initial DVF is equal to the affine dvf.
        sitk.WriteImage(sitk.Cast(ref_dvf_sitk, sitk.sitkVectorFloat32), su.address_generator(setting, 'DVF_perturb', cn=cn, out=out))
    else:
        GridSpacing = setting['GridSpacing']
        gridBorderToZero = setting['GridBorderToZero']
        maxDeform = setting['perturbationOffset']
        numberOfGrids = list(np.round(np.array(ref_dvf_sitk.GetSize()) * np.array(ref_dvf_sitk.GetSpacing()) / GridSpacing))
        numberOfGrids = [int(i) for i in numberOfGrids]  # This is a bit funny, it has to be int (and not even np.int)
        BCoeff = sitk.BSplineTransformInitializer(ref_dvf_sitk, numberOfGrids, order=3)
        grid_side = BCoeff.GetTransformDomainMeshSize()
        BCoeff_parameters = np.random.uniform(-maxDeform, maxDeform, len(BCoeff.GetParameters()))
        BCoeff_processed_dim = [None] * 3
        for dim in range(3):
            BCoeff_dim = np.reshape(np.split(BCoeff_parameters, 3)[dim], [grid_side[2] + 3, grid_side[1] + 3, grid_side[0] + 3])
            # number of coefficients in grid is increased by 3 in simpleITK.
            if np.any(gridBorderToZero):
                nonZeroMask = np.zeros(np.shape(BCoeff_dim))
                nonZeroMask[gridBorderToZero[0]: -gridBorderToZero[0],
                            gridBorderToZero[1]: -gridBorderToZero[1],
                            gridBorderToZero[2]: -gridBorderToZero[2]] = 1
                BCoeff_dim = BCoeff_dim * nonZeroMask
            BCoeff_processed_dim[dim] = np.copy(BCoeff_dim)

        sitk.WriteImage(sitk.GetImageFromArray(np.stack((BCoeff_processed_dim[0], BCoeff_processed_dim[1],
                                               BCoeff_processed_dim[2]), axis=3), isVector=True),
                        su.address_generator(setting, 'BSplineGrid', cn=cn, out=out))

        BCoeff_processed = np.hstack((BCoeff_processed_dim[0].flatten(),
                                      BCoeff_processed_dim[1].flatten(),
                                      BCoeff_processed_dim[2].flatten()))
        BCoeff.SetParameters(BCoeff_processed)
        DVF_filter = sitk.TransformToDisplacementFieldFilter()
        DVF_filter.SetReferenceImage(ref_dvf_sitk)
        DVF_perturb_pure_SITK = DVF_filter.Execute(BCoeff)
        if setting['verboseImage']:
            sitk.WriteImage(sitk.Cast(DVF_perturb_pure_SITK, sitk.sitkVectorFloat32), DVF_perturb_pure_address)
        DVF_perturb_pure = sitk.GetArrayFromImage(DVF_perturb_pure_SITK)
        origDVF = sitk.GetArrayFromImage(ref_dvf_sitk)
        DVF_perturb = origDVF + DVF_perturb_pure
        DVF_perturb_SITK = IP.array_to_sitk(DVF_perturb, im_ref=ref_dvf_sitk, is_vector=True)
        sitk.WriteImage(sitk.Cast(DVF_perturb_SITK, sitk.sitkVectorFloat32), DVF_perturb_address)


def write_and_submit_job(setting, job_name=None, phase=None, cn=None, out=None, outfinal=None, script_address=None):
    if phase == 0:
        job_script_folder = su.address_generator(setting, 'affineFolder', cn=cn)
        job_output = su.address_generator(setting, 'affineJobOut', cn=cn)
    elif phase == 1:
        job_script_folder = su.address_generator(setting, 'nonRigidFolder', cn=cn, out=out)
        job_output = su.address_generator(setting, 'nonRigidJobOut', cn=cn, out=out)
    elif phase == 2:
        job_script_folder = su.address_generator(setting, 'nonRigidFolder_final', cn=cn, outfinal=outfinal)
        job_output = su.address_generator(setting, 'nonRigidJobOut_final', cn=cn, outfinal=outfinal)
    else:
        raise ValueError ('phase is {}'.format(phase))
    if not os.path.exists(job_script_folder):
        os.makedirs(job_script_folder)
    job_script = job_script_folder + 'jobscript.sh'
    with open(job_script, "w") as textScr:
        textScr.write(sungrid.job_script(setting, job_name=job_name, phase=phase, cn=cn, out=out, outfinal=outfinal, script_address=script_address, job_output=job_output))
        textScr.close()
    qsub_cmd = 'qsub '
    if setting['cluster_task_dependency']:
        queue_info, job_info = sungrid.qstat()
        all_jobs = queue_info + job_info
        found = False

        if phase == 1:
            for job in all_jobs:
                if not found:
                    if setting['affine_experiment'] is None:
                        affine_experiment = setting['current_experiment']
                    else:
                        affine_experiment = setting['affine_experiment']
                    if affine_experiment + '_' + 'affine_cn_'+str(cn) == job['JB_name']:
                        found = True
                        print(job_name + ' will wait for ' + affine_experiment + '_' + 'affine_cn_' + str(cn))
                        qsub_cmd = qsub_cmd + '-hold_jid ' + job['JB_name'] + ' '
            if not found:
                if setting['affine_experiment'] is not None:
                    affine_step = setting['affine_experiment_step']
                else:
                    affine_step = 0
                if not os.path.isfile(su.address_generator(setting, 'affineDVF', cn=cn, current_experiment=setting['affine_experiment'])):
                    raise ValueError('The job '+job_name+' cannot be submitted, because neither ' +
                                     ' affine output is availalbe nor affine job =  '+'affine_cn_'+str(cn) +
                                     'is in the job list')
        if phase == 2:
            for job in all_jobs:
                if not found:
                    if setting['current_experiment']+'_'+'nonRigid_cn_'+str(cn)+'_out_0' == job['JB_name']:
                        found = True
                        print(job_name + ' will wait for ' + 'nonRigid_cn_'+str(cn)+'_out_0')
                        qsub_cmd = qsub_cmd + '-hold_jid ' + job['JB_name'] + ' '
            if not found:
                if not os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed', cn=cn, out=0)):
                    raise ValueError('The job '+job_name+' cannot be submitted, because neither ' +
                                     ' nonrigid output is availalbe nor nonrigidjob =  '+'nonRigid_cn_'+str(cn)+'_out_0' +
                                     'is in the job list')

    qsub_cmd = qsub_cmd + job_script
    os.system(qsub_cmd)


class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   modified from: https://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
   """
   def __init__(self, logger, log_level=logging.DEBUG):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

   def flush(self):
      pass


def setLogFile(logFileName):
    logging.basicConfig(
        format='[%(threadName)-12.12s] %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(logFileName),
            logging.StreamHandler()
        ])

    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.DEBUG)
    sys.stdout = sl

    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.DEBUG)
    sys.stderr = sl
