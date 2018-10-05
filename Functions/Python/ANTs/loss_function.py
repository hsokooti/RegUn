import copy
import os
import numpy as np
import matplotlib.pyplot as plt
import Functions.Python.setting_utils as su
import copy
from matplotlib.pyplot import cm
import Functions.Python.color_constants as color_constants


def loss_function(setting, cn_list=None, out=None, exp_list=None):
    loss = dict()
    number_of_stages_dic = {'ANTs1': 4}
    loss['max_stage'] = 0
    for exp in exp_list:
        loss['max_stage'] = max(loss['max_stage'], number_of_stages_dic[exp])

    for stage in range(loss['max_stage']):
        for cn in cn_list:
            loss['max_itr_stage' + str(stage)+'_cn'+str(cn)] = 0
    for exp in exp_list:
        loss[exp] = {}
        if not su.load_setting(exp, data=setting['data'], where_to_run=setting['whereToRun']):
            setting_exp = copy.deepcopy(setting)
            setting_exp['current_experiment'] = exp
        else:
            setting_exp = su.load_setting(exp, data=setting['data'], where_to_run=setting['whereToRun'])
        number_of_stages = number_of_stages_dic[exp]
        for cn in cn_list:
            nonrigid_folder = su.address_generator(setting_exp, 'nonRigidFolder', cn=cn, out=out)
            jobout_list = []
            for file in os.listdir(nonrigid_folder):
                if 'jobOut' in file:
                    jobout_list.append(file)
            jobout_address = nonrigid_folder + jobout_list[-1]
            with open(jobout_address, 'r') as f:
                jobout_str = f.read()

            loss[exp]['cn'+str(cn)] = {}
            loss[exp]['cn'+str(cn)]['loss_points'] = []
            stage = copy.copy(number_of_stages)
            for line in jobout_str.splitlines():
                if 'XDIAGNOSTIC' in line:
                    stage = stage - 1
                    loss[exp]['cn'+str(cn)]['stage'+str(stage)] = {}
                    loss[exp]['cn'+str(cn)]['stage'+str(stage)]['loss'] = []
                if 'WDIAGNOSTIC' in line:
                    loss[exp]['cn'+str(cn)]['stage'+str(stage)]['loss'].append(float(line.split(',')[2]))

            for stage in range(number_of_stages-1, -1, -1):
                if 'stage'+str(stage) in loss[exp]['cn'+str(cn)].keys():
                    loss[exp]['cn'+str(cn)]['stage'+str(stage)]['first_itr'] = loss[exp]['cn'+str(cn)]['stage'+str(stage)]['loss'][0]
                    loss[exp]['cn'+str(cn)]['stage'+str(stage)]['last_itr'] = loss[exp]['cn'+str(cn)]['stage'+str(stage)]['loss'][-1]
                    loss[exp]['cn'+str(cn)]['loss_points'].append(loss[exp]['cn'+str(cn)]['stage'+str(stage)]['first_itr'])
                    loss[exp]['cn'+str(cn)]['loss_points'].append(loss[exp]['cn'+str(cn)]['stage'+str(stage)]['last_itr'])
                    y = loss[exp]['cn'+str(cn)]['stage'+str(stage)]['loss']
                    if len(y) > loss['max_itr_stage'+str(stage)+'_cn'+str(cn)]:
                        loss['max_itr_stage'+str(stage)+'_cn'+str(cn)] = len(y)
                        # print('max_len_itr_stage{} is {}. exp='.format(stage, loss['max_itr_stage'+str(stage)+'_cn'+str(cn)]) + exp + ', cn={}, stage={}'.format(cn, stage))
    return loss


def plot_loss(setting, cn_list=None, out=None, exp_list=None):
    loss = loss_function(setting, cn_list=cn_list, out=out, exp_list=exp_list)
    stage_len = 20
    inter_stage_len = 1
    horizontal_number = []
    horizontal_limit = dict()
    xtick_locs = []
    xtick_labels = []
    xtick_labels_dict = dict()
    color_dict = color_constants.color_dict()
    color_keys = ['red1', 'blue', 'green', 'purple', 'orange', 'cyan2', 'brick', 'cobaltgreen', 'deeppink4', 'gold1', 'midnightblue',
                  'chartreuse4', 'darkolivegreen', 'indigo', 'seagreen4', 'blue4']
    color_list = [color_dict[color_key] for color_key in color_keys]
    # x = np.linspace(0.0, 1.0, 50)
    # color_list = cm.get_cmap('prism')(x)[:, :3]

    number_of_stages = loss['max_stage']
    for i_stage, stage in enumerate(range(number_of_stages-1, -1, -1)):
        horizontal_limit['stage'+str(stage)] = {}
        horizontal_limit['stage'+str(stage)]['start'] = i_stage * stage_len + inter_stage_len - 1
        horizontal_limit['stage'+str(stage)]['end'] = i_stage * stage_len + stage_len - 1
        xtick_locs.append((horizontal_limit['stage'+str(stage)]['start']+horizontal_limit['stage'+str(stage)]['end'])/2)
        xtick_labels.append('stage'+str(stage))
    for cn in cn_list:
        xtick_labels_dict['cn'+str(cn)] = []
        for stage in range(number_of_stages-1, -1, -1):
            xtick_labels_dict['cn'+str(cn)].append('stage'+str(stage)+'-'+str(loss['max_itr_stage'+str(stage)+'_cn'+str(cn)]))

    exp_dict = su.exp_info()
    for cn in cn_list:
        fig1, axe1 = plt.subplots(num=1, figsize=(18, 6))
        for exp_i, exp in enumerate(exp_list):
            printed_label = False
            for stage in range(number_of_stages - 1, -1, -1):
                if 'stage' + str(stage) in loss[exp]['cn' + str(cn)].keys():
                    loss_exp_stage = loss[exp]['cn' + str(cn)]['stage' + str(stage)]['loss'].copy()
                    horizontal_number_fixed = np.linspace(horizontal_limit['stage' + str(stage)]['start'],
                                                          horizontal_limit['stage' + str(stage)]['end'],
                                                          loss['max_itr_stage'+str(stage)+'_cn'+str(cn)])
                    horizontal_number_stage = horizontal_number_fixed[0:len(loss_exp_stage)]
                    if not printed_label:
                        loss_label = exp + '_' + exp_dict[exp + '-TRE_nonrigid']
                        printed_label = True
                    else:
                        loss_label = None
                    axe1.plot(horizontal_number_stage, loss_exp_stage, color=color_list[exp_i], label=loss_label)
        axe1.legend()
        plt.xticks(xtick_locs,  xtick_labels_dict['cn'+str(cn)], fontsize=16)
        plt.title('copd' + str(cn))
        plt.draw()
        plt.savefig(su.address_generator(setting, 'LossPlotItr', cn=cn))
        plt.close()

    for cn in cn_list:
        fig1, axe1 = plt.subplots(num=1, figsize=(18, 6))
        for exp_i, exp in enumerate(exp_list):
            horizontal_number = []
            loss_exp = []
            for stage in range(number_of_stages-1, -1, -1):
                if 'stage'+str(stage) in loss[exp]['cn'+str(cn)].keys():
                    y = loss[exp]['cn'+str(cn)]['stage'+str(stage)]['loss'].copy()
                    horizontal_number.extend(np.linspace(horizontal_limit['stage'+str(stage)]['start'],
                                                     horizontal_limit['stage' + str(stage)]['end'],
                                                     len(y)))
                    loss_exp.extend(y)
            axe1.plot(horizontal_number, loss_exp, label=exp+'_'+exp_dict[exp+'-TRE_nonrigid'], color=color_list[exp_i])
        axe1.legend()
        plt.xticks(xtick_locs, xtick_labels, fontsize=16)
        plt.title('copd'+str(cn))
        plt.draw()
        plt.savefig(su.address_generator(setting, 'LossPlot', cn=cn))
        plt.close()

