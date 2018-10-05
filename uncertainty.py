import numpy as np
import Functions.Python.setting_utils as su
import logging
import Functions.Python.MIND as pyMIND
import Functions.Python.uncertainty_features as ut
import Functions.Python.preprocessing as pre
import Functions.Python.landmark_utils as lu
import Functions.Python.ANTs.registration_ants as reg_ants
import Functions.Python.ANTs.loss_function as ants_loss
import time


def main(current_experiment=None):
    where_to_run = 'local'  # 'local' , 'sharkCluster' , 'shark'
    database = 'DIR-Lab_COPD'
    current_experiment = 'ANTs18'  # 'elastix1', 'EMPIRE10_crop11'
    if not su.load_setting(current_experiment, data=database, where_to_run=where_to_run):
        registration_method = 'ANTs'   # elastix , ANTs
        setting = su.initialize_setting(current_experiment, data=database, where_to_run=where_to_run, registration_method=registration_method)
        setting['cluster_phase'] = 1  # 0: affine, 1: initial perturb + BSpline_SyN, 2:final perturb + BSpline_Syn
        setting['affine_experiment'] = None
        setting['AffineParameter'] = ['Par0011.affine.txt', 'Par0011.affine.txt', 'Par0011.affine.txt']
        setting['MaskName_Affine'] = ['Cylinder', 'Torso', 'Lung_Manual']
    else:
        setting = su.load_setting(current_experiment, data=database, where_to_run=where_to_run)

    cn_list = setting['cn_range']
    feature_list = ['stdT', 'E_T', 'stdT_final', 'E_T_final', 'Jac', 'MIND', 'CV', 'NC', 'MI']
    feature_pool_list = ['stdT', 'E_T', 'stdT_final', 'E_T_final', 'Jac', 'MIND', 'CV']
    feature_scatter_list = ['stdT_pooled_0', 'stdT_pooled_1', 'stdT_pooled_2', 'stdT_pooled_3', 'MIND_pooled_0', 'MIND_pooled_1', 'MIND_pooled_2'] + ['stdT', 'E_T', 'Jac', 'MIND', 'CV', 'NC', 'MI']

    cn_remove = []
    for cn in cn_list:
        # ------------ pre-processing -------------
        pre.dirlab.dir_lab_copd(cn)
        pre.cylinder_mask(setting, cn=cn)
        pre.chest_segmentation.ptpulmo_segmentation_dirlab(data='DIR-Lab_COPD', cn=cn, segment_organ='Torso')
        pre.chest_segmentation.ptpulmo_segmentation_dirlab(data='DIR-Lab_COPD', cn=cn, segment_organ='Lung')
        pre.chest_segmentation.lung_fill_hole_dirlab(data='DIR-Lab_COPD', cn=cn)
        # pre.chest_segmentation.lung_fill_hole_erode(setting, cn=cn)
        # pre.cylinder_mask(setting, cn=cn, overwrite=False)
        pre.ants_preprocessing.image_normalization(setting, cn=cn)

        #  ------------ registration --------------
        # preferably do the registration by running either do_elastix_registration or do_ANTs_registration
        # do_elastix_registration

        # ------------ post-processing -------------
        reg_ants.convert_nii2mha(setting, cn=cn)

        # ---------- feature extraction -----------
        ut.std_t(setting, cn=cn, mode='initial')
        ut.std_t(setting, cn=cn, mode='final')
        ut.jac(setting, cn=cn)
        output_error = ut.compute_error(setting, cn=cn, write_error_image=True)
        if output_error == 2:
            cn_remove.append(cn)
        ut.ncmi(setting, cn=cn)
        ut.feature_pooling(setting, cn=cn, feature_list=feature_pool_list)

    cn_list = [cn for cn in cn_list if cn not in cn_remove]

    landmarks = lu.load_features(setting, feature_list=feature_list, cn_list=cn_list)
    exp_tre_list = ['elastix1-TRE_nonrigid', 'ANTs1-TRE_nonrigid']
    exp_loss = ['ANTs1']
    cn_list = setting['cn_range']
    lu.plot.boxplot_tre(setting, cn_list=cn_list, exp_tre_list=exp_tre_list)
    lu.plot.table_tre(setting, cn_list=cn_list, exp_tre_list=exp_tre_list)
    lu.plot.table_tre_cn(setting, cn_list=cn_list, exp='ANTs1-TRE_nonrigid')
    lu.plot.feature_tre_scatter(setting, cn_list=cn_list, feature_list=feature_scatter_list)
    ants_loss.plot_loss(setting, cn_list=np.arange(1, 11), exp_list=exp_loss, out=0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(current_experiment=None)