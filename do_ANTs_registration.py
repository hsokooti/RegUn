import os
import numpy as np
import Functions.Python.setting_utils as su
import Functions.Python.ANTs.registration_ants as regANTs
import argparse
import logging
import shutil


def do_ANTs_registration():
    cn_range = np.arange(1, 11)
    out_range = np.arange(0, 21)
    outfinal_range = np.arange(1,21)
    where_to_run = 'sharkCluster'  # 'local' , 'sharkCluster' , 'shark'
    database = 'DIR-Lab_COPD'
    current_experiment = 'ANTs1'
    if not su.load_setting(current_experiment, data=database, where_to_run=where_to_run):
        registration_method = 'ANTs'
        setting = su.initialize_setting(current_experiment, data=database, where_to_run=where_to_run, registration_method=registration_method)
        # setting['initial_nonrigid_iterations'] = [150, 120, 100, 30]
        setting['NonRigidParameter'] = 'nonrigid.txt'
        setting['NonRigidParameter_final'] = 'nonrigid_final.txt'
        setting['ImageType_Registration'] = 'Im_Masked_Normalized'
        setting['MaskName_Affine'] = ['Torso']
        setting['useMask'] = False
        setting['MaskName_BSpline'] = 'Lung_Filled'    # Lung_Filled
        setting['MaskName_BSpline_Final'] = 'Lung_Filled'
        setting['affine_experiment'] = 'elastix1'   # you can choose to use the affine result of the current experiment or from another experiment.
        # This is useful when you want to tune the nonrigid registration. if it is None, then the affine folder in the current experiment is used
        setting['affine_experiment_step'] = 0
        su.write_setting(setting)
    else:
        setting = su.load_setting(current_experiment, data=database, where_to_run=where_to_run)

    setting['cluster_phase'] = 1  # 0: affine, 1: initial perturb + BSpline_SyN, 2:final perturb + BSpline_Syn
    setting['cluster_task_despendency'] = True
    setting = check_input_arguments(setting)  # if script have some arguments, it goes to 'sharkCluster' mode. Now you can modify the code after submitting the jobs.

    if setting['whereToRun'] == 'local' or setting['whereToRun'] == 'shark':
        backup_script_address = backup_script(setting, os.path.realpath(__file__))
        for cn in [2]:
            # regANTs.affine_ANTs(setting, cn=cn)
            # regANTs.affine_ANTs_transform(setting, cn=cn)
            # regANTs.affine_ANTs_transform_image(setting, cn=cn)
            hi = 1
            for out in range(0, 1):
                # regANTs.perturbation(setting, cn=cn, out=out)
                # regANTs.BSpline_SyN_ANTs(setting, cn=cn, out=out)
                # regANTs.BSpline_SyN_ANTs_transform(setting, cn=cn, out=out)
                # regANTs.BSpline_SyN_ANTs_cleanup(setting, IN=cn, out=out)
                # regANTs.BSpline_SyN_ANTs_transform_image(setting, IN=cn, out=out)
                # regANTs.convert_nii2mha(setting, cn=cn, out=out)
                hi = 1

            for outfinal in range(1, 21):
                # regANTs.perturbation(setting, cn=cn, outfinal=outfinal)
                # regANTs.bspline_syn_ants_final(setting, cn=cn, outfinal=outfinal)
                # regANTs.BSpline_SyN_ANTs_final_transform(setting, cn=cn, outfinal=outfinal)
                # regANTs.BSpline_SyN_ANTs_cleanup_final(setting, cn=cn, outfinal=outfinal)
                hi = 1

    elif setting['whereToRun'] == 'sharkCluster':
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('--cn', metavar='N', type=int, nargs='+',
                            help='an integer for the accumulator')
        parser.add_argument('--out', metavar='N', type=int, nargs='+',
                            help='an integer for the accumulator')
        parser.add_argument('--outfinal', metavar='N', type=int, nargs='+',
                            help='an integer for the accumulator')
        parser.add_argument('--phase', metavar='N', type=int, nargs='+',
                            help='an integer for the accumulator')
        args = parser.parse_args()
        if args.phase is not None:
            # clusterMode is in the run mode
            phase = args.phase[0]
            if args.cn is not None:
                cn = args.cn[0]
            if args.out is not None:
                out = args.out[0]
            if args.outfinal is not None:
                outfinal = args.outfinal[0]

            if phase == 0:
                logging.debug('phase={}, cn={} '.format(phase, cn))
                regANTs.affine_ANTs(setting, cn=cn)
                regANTs.affine_ANTs_transform(setting, cn=cn)
                regANTs.affine_ANTs_transform_image(setting, cn=cn)
            if phase == 1:
                logging.debug('phase={}, cn={}, out={} '.format(phase, cn, out))
                regANTs.perturbation(setting, cn=cn, out=out)
                regANTs.BSpline_SyN_ANTs(setting, cn=cn, out=out)
                regANTs.BSpline_SyN_ANTs_transform(setting, cn=cn, out=out)
                regANTs.BSpline_SyN_ANTs_cleanup(setting, IN=cn, out=out)
                regANTs.BSpline_SyN_ANTs_transform_image(setting, IN=cn, out=out)

            if phase == 2:
                logging.debug('phase={}, cn={}, outfinal={} '.format(phase, cn, outfinal))
                regANTs.perturbation(setting, cn=cn, outfinal=outfinal)
                regANTs.bspline_syn_ants_final(setting, cn=cn, outfinal=outfinal)
                regANTs.BSpline_SyN_ANTs_final_transform(setting, cn=cn, outfinal=outfinal)
                regANTs.BSpline_SyN_ANTs_cleanup_final(setting, cn=cn, outfinal=outfinal)
        else:
            # clusterMode is in the preparing_jobs mode
            backup_script_address = backup_script(setting, os.path.realpath(__file__))
            phase = setting['cluster_phase']
            if phase == 0:
                for cn in cn_range:
                    if not os.path.isfile(su.address_generator(setting, 'affineDVF', cn=cn)):
                        job_name = setting['current_experiment'] + '_' + 'affine_cn_' + str(cn)
                        regANTs.write_and_submit_job(setting, job_name=job_name, phase=phase, cn=cn, script_address=backup_script_address)
            if phase == 1:
                for cn in range(9, 11):
                    for out in range(1, 21):
                        job_name = setting['current_experiment'] + '_' + 'nonRigid_cn_' + str(cn) + '_out_' + str(out)
                        regANTs.write_and_submit_job(setting, job_name=job_name, phase=phase, cn=cn, out=out, script_address=backup_script_address)
            if phase == 2:
                for cn in range(9, 11):
                    for outfinal in range(1, 21):
                        if not os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed_final', cn=cn, outfinal=outfinal)):
                            job_name = setting['current_experiment'] + '_' + 'nonRigid_cn_' + str(cn) + '_outfinal_' + str(outfinal)
                            regANTs.write_and_submit_job(setting, job_name=job_name, phase=phase, cn=cn, outfinal=outfinal, script_address=backup_script_address)


def backup_script(setting, script_address):
    """
    backup the current script
    :param script_address: current script address
    :return: backup_script_address: backup script address
    """
    script_address = script_address.replace('\\', '/')  # windows path correction
    script_name = script_address.rsplit('/', maxsplit=1)[1]
    script_folder = script_address.rsplit('/', maxsplit=1)[0] + '/'
    backup_number = 1
    backup_root_folder = su.address_generator(setting, 'experimentRootFolder') + 'code_backup/'
    backup_folder = backup_root_folder + 'backup-' + str(backup_number) + '/'
    while os.path.isdir(backup_folder):
        backup_number = backup_number + 1
        backup_folder = backup_root_folder + 'backup-' + str(backup_number) + '/'
    os.makedirs(backup_folder)
    shutil.copy(script_address, backup_folder)
    shutil.copytree(script_folder + '/Functions/Python/', backup_folder + '/Functions/Python/')
    backup_script_address = backup_folder + script_name
    return backup_script_address


def check_input_arguments(setting):
    parser = argparse.ArgumentParser(description='inpusts of ANTs registration')
    parser.add_argument('--phase', metavar='N', type=int, nargs='+',
                        help='0: Affine, 1: stdT, 2:stdTL')
    parser.add_argument('--cn', metavar='N', type=int, nargs='+',
                        help='case number of the image')
    parser.add_argument('--out', metavar='N', type=int, nargs='+',
                        help='selected number of the registration to calculated stdT')
    parser.add_argument('--outfinal', metavar='N', type=int, nargs='+',
                        help='selected number of the registration to calculated stdTL')
    args = parser.parse_args()
    if args.phase is not None:
        setting['whereToRun'] = 'sharkCluster'
    return setting


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    do_ANTs_registration()

