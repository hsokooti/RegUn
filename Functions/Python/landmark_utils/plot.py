import matplotlib.pyplot as plt
from .landmark_utils import *
import Functions.Python.color_constants as color_constants


def boxplot_tre(setting, cn_list=None, exp_tre_list=None):
    """
    :param setting:
    :param cn_list:
    :param exp_tre_list: in this format:'EMPIRE10_crop3-TRE_affine', 'EMPIRE10_crop10-TRE_nonrigid'
    :return:
    """
    all_landmarks, all_landmarks_merged, legend_list = read_landmarks_pkl(setting, cn_list=cn_list, exp_tre_list=exp_tre_list)
    color_dict = color_constants.color_dict()
    tre_cn = []
    tre_merged = []
    bar_per_cn = len(exp_tre_list)
    positions1 = np.empty(len(cn_list)*bar_per_cn)
    xtick_locs = np.empty(len(cn_list))
    xtick_labels = [None] * len(cn_list)
    gap = 0
    for cn_i, cn in enumerate(cn_list):
        for exp_i, exp_full_name in enumerate(exp_tre_list):
            if 'cn'+str(cn) in all_landmarks[exp_full_name].keys():
                tre_cn.append(all_landmarks[exp_full_name]['cn'+str(cn)][exp_full_name.rsplit('-', maxsplit=1)[1]])
            else:
                tre_cn.append(np.zeros(300))
            positions1[bar_per_cn * cn_i + exp_i] = bar_per_cn * cn_i + exp_i + gap
            if cn_i == 0:
                tre_merged.append(all_landmarks_merged[exp_full_name][exp_full_name.rsplit('-', maxsplit=1)[1]])
        xtick_locs[cn_i] = bar_per_cn * cn_i + gap + (bar_per_cn-1)/2
        xtick_labels[cn_i] = 'cn'+str(cn)
        gap = gap + 1

    fig1, axe1 = plt.subplots(num=1, figsize=(18, 10))
    fig2, axe2 = plt.subplots(num=2, figsize=(18, 10))
    bplot1 = axe1.boxplot(tre_cn,
                          vert=True,  # vertical box aligmnent
                          patch_artist=True,  # fill with color
                          positions=positions1)
    bplot2 = axe2.boxplot(tre_merged,
                          vert=True,  # vertical box aligmnent
                          patch_artist=True,  # fill with color
                          positions=np.arange(len(tre_merged)))
    color_keys = ['pink', 'lightblue', 'red1', 'blue', 'green', 'purple', 'orange', 'cyan2', 'brick', 'cobaltgreen', 'deeppink4', 'gold1', 'midnightblue',
                  'chartreuse4', 'darkolivegreen', 'indigo', 'seagreen4', 'blue4']

    colors = [color_dict[color_key] for color_key in color_keys]
    for patch, color in zip(bplot1['boxes'], colors[0:bar_per_cn] * bar_per_cn * len(cn_list)):
        patch.set_facecolor(color)
    for patch, color in zip(bplot2['boxes'], colors[0:bar_per_cn] * bar_per_cn):
        patch.set_facecolor(color)

    axe1_ylim = axe1.get_ylim()[1]
    axe2_ylim = axe2.get_ylim()[1]
    # axe1.set_ylim(axe1_ylim + 10)
    # axe2.set_ylim(axe2_ylim + 10)
    legend_position1 = axe1.get_ylim()[1] - 2
    legend_position2 = axe2.get_ylim()[1] - 2
    for legend_i, legend_text in enumerate(legend_list):
        axe1.text(3, legend_position1, legend_text, ha="left", family='sans-serif', size=10, color=colors[legend_i])
        axe2.text(0.5, legend_position2, legend_text, ha="left", family='sans-serif', size=10, color=colors[legend_i])
        legend_position1 = legend_position1 - 1.8
        legend_position2 = legend_position2 - 1.8

    if not os.path.exists(su.address_generator(setting, 'reportFolder')):
        os.makedirs(su.address_generator(setting, 'reportFolder'))
    plt.figure(1)
    plt.xticks(xtick_locs, xtick_labels, fontsize=16)
    plt.title('data:'+setting['data']+', current_experiment:'+setting['current_experiment'])
    plt.draw()
    plt.savefig(su.address_generator(setting, 'TRE_BoxPlot_cn'))
    plt.close()
    plt.figure(2)
    plt.draw()
    plt.savefig(su.address_generator(setting, 'TRE_BoxPlot_Merged'))
    plt.close()


def table_tre(setting, cn_list=None, exp_tre_list=None):
    """
    :param setting:
    :param cn_list:
    :param exp_tre_list: in this format:'EMPIRE10_crop3-TRE_affine', 'EMPIRE10_crop10-TRE_nonrigid'
    :return:
    """
    all_landmarks, all_landmarks_merged, legend_list = read_landmarks_pkl(setting, cn_list=cn_list, exp_tre_list=exp_tre_list)
    tab = dict()
    latex_str = dict()
    value_tab = np.empty([len(exp_tre_list), 3], dtype=object)
    header_tab = ['Experiment', 'TRE mean-std', 'TRE median']
    for exp_i, exp in enumerate(exp_tre_list):
        tab[exp] = {}
        latex_str[exp] = '&'+legend_list[exp_i] + ' &test '
        tab[exp]['mean'] = np.mean(all_landmarks_merged[exp][exp.rsplit('-', maxsplit=1)[1]])
        tab[exp]['std'] = np.std(all_landmarks_merged[exp][exp.rsplit('-', maxsplit=1)[1]])
        tab[exp]['median'] = np.median(all_landmarks_merged[exp][exp.rsplit('-', maxsplit=1)[1]])
        value_tab[exp_i, 0] = legend_list[exp_i]
        value_tab[exp_i, 1] = '${:.2f}\pm{:.2f}$'.format(tab[exp]['mean'], tab[exp]['std'])
        value_tab[exp_i, 2] = '${:.2f}$'.format(tab[exp]['median'])
        latex_str[exp] += '&\scriptsize${:.2f}\pm{:.2f}$'.format(tab[exp]['mean'], tab[exp]['std'])
    plt.rc('font', family='serif')
    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_visible(False)
    table = ax.table(cellText=value_tab, colLabels=header_tab, loc='center', colLoc='left', cellLoc='left', colWidths=[0.4, 0.08, 0.08])
    table.scale(1.7, 1.7)
    ax.axis('off')
    ax.axis('tight')
    fig.tight_layout()
    plt.draw()
    plt.savefig(su.address_generator(setting, 'TRE_Table_Merged'))
    plt.close()


def table_tre_cn(setting, cn_list=None, exp=None):
    """
    :param setting:
    :param cn_list:
    :param exp: in this format:'EMPIRE10_crop3-TRE_affine', 'EMPIRE10_crop10-TRE_nonrigid'
    :return:
    """
    all_landmarks, all_landmarks_merged, legend_list = read_landmarks_pkl(setting, cn_list=cn_list, exp_tre_list=[exp])
    tab = dict()
    latex_str = dict()
    value_tab = np.empty([len(cn_list), 3], dtype=object)
    header_tab = ['Experiment', 'TRE mean-std', 'TRE median']
    for cn_i, cn in enumerate(cn_list):
        tab[cn] = {}
        # latex_str[cn] = '&'+legend_list[cn_i] + ' &test '
        tab[cn]['mean'] = np.mean(all_landmarks[exp]['cn'+str(cn)][exp.rsplit('-', maxsplit=1)[1]])
        tab[cn]['std'] = np.std(all_landmarks[exp]['cn'+str(cn)][exp.rsplit('-', maxsplit=1)[1]])
        tab[cn]['median'] = np.median(all_landmarks[exp]['cn'+str(cn)][exp.rsplit('-', maxsplit=1)[1]])
        value_tab[cn_i, 0] = legend_list[0] + '-cn' + str(cn)
        value_tab[cn_i, 1] = '${:.2f}\pm{:.2f}$'.format(tab[cn]['mean'], tab[cn]['std'])
        value_tab[cn_i, 2] = '${:.2f}$'.format(tab[cn]['median'])
        # latex_str[cn] += '&\scriptsize${:.2f}\pm{:.2f}$'.format(tab[cn]['mean'], tab[cn]['std'])
    plt.rc('font', family='serif')
    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_visible(False)
    ax.table(cellText=value_tab, colLabels=header_tab, loc='center', colLoc='left', cellLoc='left', fontsize=50)
    ax.axis('off')
    ax.axis('tight')
    fig.tight_layout()
    plt.draw()
    plt.savefig(su.address_generator(setting, 'TRE_Table_cn'))
    plt.close()


def feature_tre_scatter(setting, cn_list=None, feature_list=None, exp=None):
    """

    :param setting:
    :param cn_list:
    :param feature_list:
                the exact name of the feature: ['stdT', 'E_T', 'Jac', 'MIND', 'CV', 'NC', 'MI']
                or pooled feature with the one index: ['stdT_pooled_0', 'E_T_pooled_5', 'CV_pooled_11']
                or a combination of both
    :param exp:
    :return:
    """
    if exp is None:
        exp = setting['current_experiment']
    if cn_list is None:
        cn_list = setting['cn_range']
    if not os.path.isdir(su.address_generator(setting, 'ReportFeatureFolder')):
        os.makedirs(su.address_generator(setting, 'ReportFeatureFolder'))
    all_landmarks, all_landmarks_merged, legend_list = read_landmarks_pkl(setting, cn_list=cn_list, exp_list=[exp])

    test_data = all_landmarks_merged[exp]['NCMI_pooled'][:, 26]
    A = (test_data < 2)
    B = np.where(test_data < -2)
    I = np.where(np.logical_and(test_data < 2, test_data > -2))
    I1 = np.where(np.logical_or(test_data < -10, test_data > 10))
    I1 = np.where((test_data < -10) & (test_data > 10))
    bins = [np.min(test_data), 2, 10, np.max(test_data)]
    plt.hist(test_data, log=True, bins=[-1, 0, 1, 2, 3, 4])


    plt.rc('font', family='serif')
    ind_sort = np.argsort(all_landmarks_merged[exp]['TRE_nonrigid'])
    for feature in feature_list:
        if len(feature.split('_')) > 2:
            if feature.split('_')[-2] == 'pooled':
                feature_name = feature.rsplit('_', maxsplit=1)[0]
                pooled_index = int(feature.rsplit('_', maxsplit=1)[-1])
                feature_data = all_landmarks_merged[exp][feature_name][:, pooled_index]
        else:
            feature_data = all_landmarks_merged[exp][feature]
        fig1, axe1 = plt.subplots(num=1, figsize=(16, 8))
        plt.plot(all_landmarks_merged[exp]['TRE_nonrigid'], feature_data, 'o')
        plt.title('data:' + setting['data'] + ', current_experiment:' + exp + ', feature:' + feature)
        plt.draw()
        plt.savefig(su.address_generator(setting, 'FeatureScatter', feature=feature))
        plt.close()

        fig2, axe2 = plt.subplots(num=2, figsize=(16, 8))
        plt.plot(feature_data[ind_sort], label='TRE', color='cyan')
        plt.plot(all_landmarks_merged[exp]['TRE_nonrigid'][ind_sort], label=feature, color='blue')
        plt.title('data:' + setting['data'] + ', current_experiment:' + exp + ', feature:' + feature)
        axe2.legend(fontsize='xx-large')
        plt.draw()
        plt.savefig(su.address_generator(setting, 'FeatureScatterSort', feature=feature))
        plt.close()


def feature_tre_boxplot(setting, cn_list=None, feature_list=None, exp=None):
    if exp is None:
        exp = setting['current_experiment']
    if cn_list is None:
        cn_list = setting['cn_range']
    if os.path.isdir(su.address_generator(setting, 'ReportFeatureFolder')):
        os.makedirs(su.address_generator(setting, 'ReportFeatureFolder'))
    all_landmarks, all_landmarks_merged, legend_list = read_landmarks_pkl(setting, cn_list=cn_list, exp_list=[exp])
    raise ValueError(' not completerd')
    for feature in feature_list:
        fig1, axe1 = plt.subplots(num=1, figsize=(16, 8))
        plt.plot(all_landmarks_merged[exp][feature], all_landmarks_merged[exp]['TRE_nonrigid'], 'o')
        plt.title('data:' + setting['data'] + ', current_experiment:' + exp + ', feature:' + feature)
        plt.draw()
        plt.savefig(su.address_generator(setting, 'FeatureBoxPlot', feature=feature))

