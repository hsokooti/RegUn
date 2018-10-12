import os
import numpy as np
import Functions.Python.setting_utils as su
import Functions.Python.registration_elx as reg_elx
import argparse
import logging
import shutil
import json


def do_elastix_registration():
    cn_range = np.arange(1, 11)
    where_to_run = 'sharkCluster'  # 'local' , 'sharkCluster' , 'shark'
    database = 'DIR-Lab_COPD'
    current_experiment = 'elastix1'
    if not su.load_setting(current_experiment, data=database, where_to_run=where_to_run):
        registration_method = 'elastix'
        setting = su.initialize_setting(current_experiment, data=database, where_to_run=where_to_run, registration_method=registration_method)
        setting['affine_experiment'] = 'elastix1'   # you can choose to use the affine result of the current experiment or from another experiment.
        # This is useful when you want to tune the nonrigid registration. if it is None, then the affine folder in the current experiment is used
        setting['affine_experiment_step'] = 0
        setting['BSplineGridExperiment'] = 'elastix1'
        setting['AffineParameter'] = ['par0049.affine.txt']
        setting['MaskName_Affine'] = ['Torso']
        setting['MaskName_BSpline'] = 'Lung_Atlas'
        setting['MaskName_BSpline_Final'] = 'Lung_Atlas'
        setting['BSplineGridParameter'] = 'par0049.bspline.grid.txt'
        setting['BSplineParameter'] = 'par0049_stdT-advanced.txt'
        setting['BSplineParameter_final'] = 'par0049_stdTL-advanced.txt'
        setting['numberOfThreads'] = 7
        su.write_setting(setting)
    else:
        setting = su.load_setting(current_experiment, data=database, where_to_run=where_to_run)

    setting['cluster_phase'] = 1  # 0: affine, 1: initial perturb + BSpline, 2:final perturb + BSpline
    setting = check_input_arguments(setting)  # if script have some arguments, it goes to 'sharkCluster' mode. Now you can modify the code after submitting the jobs.

    if setting['whereToRun'] == 'local' or setting['whereToRun'] == 'shark':
        backup_script_address = backup_script(setting, os.path.realpath(__file__))
        for cn in range(1, 11):
            # reg_elx.affine(setting, cn=cn)
            # reg_elx.affine_transform(setting, cn=cn)
            hi = 1
            for out in range(0, 1):
                # reg_elx.perturbation(setting, cn=cn, out=out)
                # reg_elx.bspline(setting, cn=cn, out=out)
                # reg_elx.correct_initial_transform(setting, cn=cn, out=out)
                # reg_elx.bspline_transform(setting, cn=cn, out=out, dvf=True)
                hi = 1
            for outfinal in range(1, 21):
                # reg_elx.perturbation(setting, cn=cn, outfinal=outfinal)
                # reg_elx.bspline_final(setting, cn=cn, outfinal=outfinal)
                # reg_elx.correct_initial_transform(setting, cn=cn, outfinal=outfinal)
                # reg_elx.bspline_final_transform(setting, cn=cn, outfinal=outfinal)
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
                reg_elx.affine(setting, cn=cn)
            if phase == 1:
                logging.debug('phase={}, cn={}, out={} '.format(phase, cn, out))
                reg_elx.perturbation(setting, cn=cn, out=out)
                reg_elx.bspline(setting, cn=cn, out=out)
                reg_elx.bspline_transform(setting, cn=cn, out=out, dvf=True)

            if phase == 2:
                logging.debug('phase={}, cn={}, outfinal={} '.format(phase, cn, outfinal))
                reg_elx.perturbation(setting, cn=cn, outfinal=outfinal)
                reg_elx.bspline_final(setting, cn=cn, outfinal=outfinal)

        else:
            # clusterMode is in the preparing_jobs mode
            backup_script_address = backup_script(setting, os.path.realpath(__file__))
            phase = setting['cluster_phase']
            if phase == 0:
                for cn in cn_range:
                    if not os.path.isfile(su.address_generator(setting, 'affineTransformParameter', cn=cn)):
                        job_name = setting['current_experiment'] + '_' + 'affine_cn_' + str(cn)
                        reg_elx.write_and_submit_job(setting, job_name=job_name, phase=phase, cn=cn, script_address=backup_script_address)
            if phase == 1:
                for cn in cn_range:
                    for out in range(0, 1):
                        job_name = setting['current_experiment'] + '_' + 'nonRigid_cn_' + str(cn) + '_out_' + str(out)
                        reg_elx.write_and_submit_job(setting, job_name=job_name, phase=phase, cn=cn, out=out, script_address=backup_script_address)
            if phase == 2:
                for cn in cn_range:
                    for outfinal in range(1, 21):
                        # if not os.path.isfile(su.address_generator(setting, 'DVF_nonRigid_composed_final', IN=cn, outfinal=outfinal)):
                        job_name = setting['current_experiment'] + '_' + 'nonRigid_cn_' + str(cn) + '_outfinal_' + str(outfinal)
                        reg_elx.write_and_submit_job(setting, job_name=job_name, phase=phase, cn=cn, outfinal=outfinal, script_address=backup_script_address)


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
    parser = argparse.ArgumentParser(description='inpusts of elastix registration')
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
    do_elastix_registration()

