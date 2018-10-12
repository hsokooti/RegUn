import os
import time
import Functions.Python.setting_utils as su
import Functions.Python.elastix_python as elxpy
import numpy as np
import Functions.Python.sungrid_utils as sungrid


def affine(setting, cn=None):
    fixed_mask_address = None
    moving_mask_address = None
    for affine_step, affine_parameter in enumerate(setting['AffineParameter']):
        if affine_step == 0:
            initial_transform = None
        else:
            initial_transform = su.address_generator(setting, 'affineTransformParameter', cn=cn, reg_step=affine_step - 1)
        if setting['useMask']:
            fixed_mask_address = su.address_generator(setting, setting['MaskName_Affine'][affine_step], cn=cn, type_im=0)
            moving_mask_address = su.address_generator(setting, setting['MaskName_Affine'][affine_step], cn=cn, type_im=1)
        elx_cmd = elxpy.elastix(parameter_file=su.address_generator(setting, 'ParameterFolder') + affine_parameter,
                                output_directory=su.address_generator(setting, 'affineFolder', cn=cn, reg_step=affine_step),
                                elastix_address='elastix',
                                fixed_image=su.address_generator(setting, 'Im', cn=cn, type_im=0),
                                moving_image=su.address_generator(setting, 'Im', cn=cn, type_im=1),
                                fixed_mask=fixed_mask_address,
                                moving_mask=moving_mask_address,
                                initial_transform=initial_transform,
                                threads=setting['numberOfThreads'])


def affine_transform(setting, cn=None, transform_all_step=True):
    if transform_all_step:
        affine_step_list = np.arange(len(setting['AffineParameter']))
    else:
        affine_step_list = [len(setting['AffineParameter']) - 1]
    for affine_step in affine_step_list:
        affine_folder = su.address_generator(setting, 'affineFolder', cn=cn, reg_step=affine_step)
        elx_cmd = elxpy.transformix(parameter_file=su.address_generator(setting, 'affineTransformParameter', cn=cn, reg_step=affine_step),
                                    input_image=su.address_generator(setting, 'Im', cn=cn, type_im=1),
                                    output_directory=affine_folder,
                                    points='all',
                                    threads=setting['numberOfThreads'])
        os.rename(affine_folder + 'result.mha',
                  su.address_generator(setting, 'affine_MovedImage', cn=cn, reg_step=affine_step))


def bspline(setting, cn=None, out=None):
    fixed_mask_address = None
    moving_mask_address = None
    if setting['useMask']:
        fixed_mask_address = su.address_generator(setting, setting['MaskName_BSpline'], cn=cn, type_im=0)
        moving_mask_address = su.address_generator(setting, setting['MaskName_BSpline'], cn=cn, type_im=1)
    elx_cmd = elxpy.elastix(parameter_file=su.address_generator(setting, 'ParameterFolder') + setting['BSplineParameter'],
                            output_directory=su.address_generator(setting, 'nonRigidFolder', cn=cn, out=out),
                            elastix_address='elastix',
                            fixed_image=su.address_generator(setting, 'Im', cn=cn, type_im=0),
                            moving_image=su.address_generator(setting, 'Im', cn=cn, type_im=1),
                            fixed_mask=fixed_mask_address,
                            moving_mask=moving_mask_address,
                            initial_transform=su.address_generator(setting, 'BSplinePerturb', cn=cn, out=out),
                            threads=setting['numberOfThreads'])


def bspline_final(setting, cn=None, outfinal=None):
    fixed_mask_address = None
    moving_mask_address = None
    if setting['useMask']:
        fixed_mask_address = su.address_generator(setting, setting['MaskName_BSpline'], cn=cn, type_im=0)
        moving_mask_address = su.address_generator(setting, setting['MaskName_BSpline'], cn=cn, type_im=1)
    elx_cmd = elxpy.elastix(parameter_file=su.address_generator(setting, 'ParameterFolder') + setting['BSplineParameter_final'],
                            output_directory=su.address_generator(setting, 'nonRigidFolder_final', cn=cn, outfinal=outfinal),
                            elastix_address='elastix',
                            fixed_image=su.address_generator(setting, 'Im', cn=cn, type_im=0),
                            moving_image=su.address_generator(setting, 'Im', cn=cn, type_im=1),
                            fixed_mask=fixed_mask_address,
                            moving_mask=moving_mask_address,
                            initial_transform=su.address_generator(setting, 'BSplinePerturb_final', cn=cn, outfinal=outfinal),
                            threads=setting['numberOfThreads'])


def bspline_transform(setting, cn=None, out=None, transform_image=True, dvf=True):
    bspline_folder = su.address_generator(setting, 'nonRigidFolder', cn=cn, out=out)
    transformix_log = bspline_folder + 'transformix.log'
    if os.path.isfile(transformix_log):
        backup_number = 1
        transformix_log_rename = bspline_folder + 'transformix' + str(backup_number) + '.log'
        while os.path.isfile(transformix_log_rename):
            backup_number = backup_number + 1
            transformix_log_rename = bspline_folder + 'transformix' + str(backup_number) + '.log'
        os.rename(transformix_log, transformix_log_rename)

    if transform_image:
        input_image = su.address_generator(setting, 'Im', cn=cn, type_im=1)
    else:
        input_image=None
    if dvf:
        points = 'all'
    else:
        points = None
    elx_cmd = elxpy.transformix(parameter_file=su.address_generator(setting, 'BSplineTransformParameter', cn=cn, out=out),
                                input_image=input_image,
                                output_directory=bspline_folder,
                                points=points,
                                threads=setting['numberOfThreads'])
    if transform_image:
        if not os.path.isfile(bspline_folder + 'result.mha'):
            time.sleep(5)
        os.rename(bspline_folder + 'result.mha',
                  su.address_generator(setting, 'nonRigid_MovedImage', cn=cn, out=out))


def bspline_final_transform(setting, cn=None, outfinal=None):
    bspline_folder = su.address_generator(setting, 'nonRigidFolder_final', cn=cn, outfinal=outfinal)
    elx_cmd = elxpy.transformix(parameter_file=su.address_generator(setting, 'BSplineTransformParameter_final', cn=cn, outfinal=outfinal),
                                output_directory=bspline_folder,
                                points='all',
                                threads=setting['numberOfThreads'])


def correct_initial_transform(setting, cn=None, out=None, outfinal=None):
    affine_experiment = setting['affine_experiment']
    parameter_dict = dict()
    if out is None and outfinal is not None:
        mode = 'final_perturbation'
        parameter_dict['BSplinePerturb_final'] = {}
        parameter_dict['BSplinePerturb_final']['address'] = su.address_generator(setting, 'BSplinePerturb_final', cn=cn, outfinal=outfinal)
        parameter_dict['BSplinePerturb_final']['InitialTransform'] = su.address_generator(setting, 'BSplinePerturb', cn=cn, out=0)
        parameter_dict['BSplineTransformParameter_final'] = {}
        parameter_dict['BSplineTransformParameter_final']['address'] = su.address_generator(setting, 'BSplineTransformParameter_final', cn=cn, outfinal=outfinal)
        parameter_dict['BSplineTransformParameter_final']['InitialTransform'] = su.address_generator(setting, 'BSplinePerturb_final', cn=cn, outfinal=outfinal)
    elif outfinal is None and out is not None:
        mode = 'initial_perturbation'
        parameter_dict['BSplinePerturb'] = {}
        parameter_dict['BSplinePerturb']['address'] = su.address_generator(setting, 'BSplinePerturb', cn=cn, out=out)
        parameter_dict['BSplinePerturb']['InitialTransform'] = su.address_generator(setting, 'affineTransformParameter', cn=cn, current_experiment=affine_experiment)
        parameter_dict['BSplineTransformParameter'] = {}
        parameter_dict['BSplineTransformParameter']['address'] = su.address_generator(setting, 'BSplineTransformParameter', cn=cn, out=out)
        parameter_dict['BSplineTransformParameter']['InitialTransform'] = su.address_generator(setting, 'affineTransformParameter', cn=cn, current_experiment=affine_experiment)
    else:
        raise ValueError('out and outfinal cannot be both None or both nonNone')
    for parameter in parameter_dict.keys():
        with open(parameter_dict[parameter]['address'], 'r') as f:
            transform_f = f.read()
        with open(parameter_dict[parameter]['address'], 'w') as transform_str:
            for line in transform_f.splitlines():
                if 'InitialTransformParametersFileName' in line:
                    line = '(InitialTransformParametersFileName ' + '"' + parameter_dict[parameter]['InitialTransform'] + '")'
                transform_str.write(line + '\n')


def perturbation(setting, cn=None, out=None, outfinal=None):
    affine_experiment = setting['affine_experiment']
    baspline_grid_experiment = setting['BSplineGridExperiment']
    if out is None and outfinal is not None:
        mode = 'final_perturbation'
        out = 0
        perturb_folder = su.address_generator(setting, 'nonRigidFolder_final', cn=cn, outfinal=outfinal)
        bspline_perturb_address = su.address_generator(setting, 'BSplinePerturb_final', cn=cn, outfinal=outfinal)
        bspline_ref_address = su.address_generator(setting, 'BSplineTransformParameter', cn=cn, out=0)

    elif outfinal is None and out is not None:
        mode = 'initial_perturbation'
        outfinal = 0
        perturb_folder = su.address_generator(setting, 'nonRigidFolder', cn=cn, out=out)
        bspline_perturb_address = su.address_generator(setting, 'BSplinePerturb', cn=cn, out=out)
        bspline_ref_address = su.address_generator(setting, 'BSplineGridTransform', cn=cn, current_experiment=baspline_grid_experiment)
    else:
        raise ValueError('out and outfinal cannot be both None or both nonNone')
    seedNumber = 10000 + 1000 * cn + out * 101 + outfinal * 4
    np.random.seed(seedNumber)
    if not os.path.exists(perturb_folder):
        os.makedirs(perturb_folder)

    if mode == 'initial_perturbation':
        if not os.path.isfile(bspline_ref_address):
            elx_cmd = elxpy.elastix(parameter_file=su.address_generator(setting, 'ParameterFolder') + setting['BSplineGridParameter'],
                                    output_directory=su.address_generator(setting, 'BSplineGridFolder', cn=cn),
                                    elastix_address='elastix',
                                    fixed_image=su.address_generator(setting, 'Im', cn=cn, type_im=0),
                                    moving_image=su.address_generator(setting, 'Im', cn=cn, type_im=1),
                                    threads=setting['numberOfThreads'])

    with open(bspline_ref_address, 'r') as f:
        bspline_ref_f = f.read()

    for line in bspline_ref_f.splitlines():
        if 'TransformParameters ' in line:
            bspline_grid_str = line.replace('(TransformParameters', '')
            bspline_grid_str = bspline_grid_str.replace(')', '')
        elif '(GridSize' in line:
            grid_size_str = line.replace('(GridSize', '')
            grid_size_str = grid_size_str.replace(')', '')

    bspline_grid_ref = np.array(bspline_grid_str.split()).astype(np.float)
    grid_size = np.array(grid_size_str.split()).astype(np.int)
    if mode == 'initial_perturbation':
        bspline_grid_initial = np.zeros(bspline_grid_ref.shape, dtype=np.float)
    else:
        bspline_grid_initial = bspline_grid_ref.copy()
    if mode == 'initial_perturbation' and out == 0:
        # no perturbation when out=0
        bspline_grid = bspline_grid_initial.copy()
    else:
        perturb_offset = setting['perturbationOffset']
        grid_border_to_zero = setting['GridBorderToZero']
        bspline_grid_random = np.random.uniform(-perturb_offset, perturb_offset, len(bspline_grid_ref))
        bspline_grid_masked_dim = [None] * 3
        for dim in range(3):
            bspline_grid_dim = np.reshape(np.split(bspline_grid_random, 3)[dim], [grid_size[2], grid_size[1], grid_size[0]])
            # to check: you can use: bspline_grid_dim = np.ones([grid_size[2], grid_size[1], grid_size[0]]) * (dim +1)
            if np.any(grid_border_to_zero):
                nonZeroMask = np.zeros(np.shape(bspline_grid_dim))
                nonZeroMask[grid_border_to_zero[0]: -grid_border_to_zero[0],
                            grid_border_to_zero[1]: -grid_border_to_zero[1],
                            grid_border_to_zero[2]: -grid_border_to_zero[2]] = 1
                bspline_grid_dim = bspline_grid_dim * nonZeroMask
            bspline_grid_masked_dim[dim] = np.copy(bspline_grid_dim)
        bspline_grid_masked = np.hstack((bspline_grid_masked_dim[0].flatten(),
                                         bspline_grid_masked_dim[1].flatten(),
                                         bspline_grid_masked_dim[2].flatten()))
        bspline_grid = bspline_grid_initial + bspline_grid_masked

    with open(bspline_perturb_address, 'w') as bspline_perturb_str:
        for line in bspline_ref_f.splitlines():
            if 'TransformParameters ' in line:
                line = '(TransformParameters'
                time_before_loop= time.time()
                for coeff in bspline_grid:
                    line = line + ' {:.6f}'.format(coeff)
                line = line + ')'
                time_after_loop = time.time()
                print('Writing TransformParameters is done in {:.2f}'.format(time_after_loop-time_before_loop))
            if 'InitialTransformParametersFileName' in line:
                affine_step = len(setting['AffineParameter']) - 1
                if mode == 'initial_perturbation':
                    line = '(InitialTransformParametersFileName ' + '"' + \
                           su.address_generator(setting, 'affineTransformParameter', cn=cn,
                                                current_experiment=affine_experiment, reg_step=affine_step) + '")'
            bspline_perturb_str.write(line + '\n')


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
                if not os.path.isfile(su.address_generator(setting,
                                                           'affineTransformParameter',
                                                           cn=cn,
                                                           current_experiment=setting['affine_experiment'],
                                                           reg_step=affine_step)):
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
                if not os.path.isfile(su.address_generator(setting, 'BSplineTransformParameter', cn=cn, out=0)):
                    raise ValueError('The job '+job_name+' cannot be submitted, because neither ' +
                                     ' nonrigid output is availalbe nor nonrigidjob =  '+'nonRigid_cn_'+str(cn)+'_out_0' +
                                     'is in the job list')
    qsub_cmd = qsub_cmd + job_script
    os.system(qsub_cmd)



