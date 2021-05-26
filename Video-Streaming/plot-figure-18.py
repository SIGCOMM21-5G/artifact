import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import scipy.stats
import matplotlib.gridspec as gridspec


RESULTS_FOLDER = './Full-Results/Sec. 5.4 Interface Sel/'
RESULTS_FOLDER_PRED = './Full-Results/Sec. 5.3 Prediction/thrpt_prediction/'
NUM_BINS = 100
BITS_IN_BYTE = 8.0
MILLISEC_IN_SEC = 1000.0
M_IN_B = 1000000.0
VIDEO_LEN = 158
VIDEO_BIT_RATE = [20000, 40000, 60000, 80000, 110000, 160000]
COLOR_MAP = plt.cm.jet #nipy_spectral, Set1,Paired 
SIM_DP = 'sim_dp'
SCHEMES = ['fastMPC', 'interface', 'overhead']

SCHEMES_NEW = ['fastMPC\n (5G only)', 'intfMPC', 'intfMPC\n(no-overhead)'] #label for plot

LABEL = ['4G', '5G']

RESULTS_FOLDER_CHK = './Full-Results/Sec. 5.3 Prediction/chunk_length/'
SCHEMES_CHK = ['_4s', '_2s', 'fastMPC']
VIDEO_LEN_CHK = {'_4s': 40, '_2s': 80, 'fastMPC': 158}

SCHEMES_NEW_CHK = ['4s\n', '2s', '1s'] #label for plot

SCHEMES_PRED = ['hmMPC', 'MPC_GDBT', 'truthMPC']
SCHEMES_NEW_PRED = ['hmMPC', 'MPC_GDBT', 'truthMPC']


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h


def main():
    time_all = {}
    bit_rate_all = {}
    buff_all = {}
    stall_all = {}
    bw_all = {}
    raw_reward_all = {}
    summay_all = {}
    for scheme in SCHEMES:
        time_all[scheme] = {}
        raw_reward_all[scheme] = {}
        bit_rate_all[scheme] = {}
        buff_all[scheme] = {}
        stall_all[scheme] = {}
        bw_all[scheme] = {}

    log_files = os.listdir(RESULTS_FOLDER)
    for log_file in log_files:

        time_ms = []
        bit_rate = []
        buff = []
        bw = []
        stall = []
        reward = []


        with open(RESULTS_FOLDER + log_file, 'rb') as f:
            if SIM_DP in log_file:
                for line in f:
                    parse = line.split()
                    if len(parse) == 1:
                        reward = float(parse[0])
                    elif len(parse) >= 6:
                        time_ms.append(float(parse[3]))
                        bit_rate.append(VIDEO_BIT_RATE[int(parse[6])])
                        buff.append(float(parse[4]))
                        bw.append(float(parse[5]))

            else:
                for line in f:
                    try:
                        parse = line.split()
                        if len(parse) <= 1:
                            break
                        time_ms.append(float(parse[0]))
                        bit_rate.append(int(parse[1]))
                        buff.append(float(parse[2]))
                        stall.append(float(parse[3]))
                        # stall_total += float(parse[3])
                        bw.append(float(parse[4]) / float(parse[5]) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                        reward.append(float(parse[6]))
                    except ZeroDivisionError:
                        bw.append(float(parse[4]) / (float(parse[5])+1) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                        reward.append(float(parse[6]))

        if SIM_DP in log_file:
            time_ms = time_ms[::-1]
            bit_rate = bit_rate[::-1]
            buff = buff[::-1]
            bw = bw[::-1]
        
        time_ms = np.array(time_ms)
        time_ms -= time_ms[0]
        

        for scheme in SCHEMES:
            if scheme in log_file :
                if scheme == 'fastMPC' and 'interface' in log_file:
                    continue
                if scheme == 'fastMPC' and '4s' in log_file:
                    continue
                if scheme == 'interface' and 'interfaceMPC' in log_file:
                    continue
                if scheme == 'robustMPC' and 'truthrobustMPC' in log_file:
                    continue
                if scheme == 'rollbackMPC' and 'rollbackMPC4s' in log_file:
                    continue
                if scheme == 'RB' and 'truthRB' in log_file:
                    continue
                time_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = time_ms
                bit_rate_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bit_rate
                buff_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = buff
                stall_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = stall
                bw_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bw
                raw_reward_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = reward
                break

    # calculate mean bitrate and stall rate
    for scheme in SCHEMES:
        summay_all[scheme] = {}
        # avg bitrate
        bitrate_avg_arr = []
        bitrate_total = 0
        total_chunk = 0
        summay_all[scheme]['all_br'] = []
        if scheme != '_4s' and scheme != 'rollbackMPC4s':
            for log in bit_rate_all[scheme]:
                if len(bit_rate_all[scheme][log]) >= VIDEO_LEN:
                    bitrate_avg_arr.append(np.mean(bit_rate_all[scheme][log][1:VIDEO_LEN])/1000)
                    bitrate_total += np.sum(np.array(bit_rate_all[scheme][log][1:VIDEO_LEN])/1000) #Mbis
                    total_chunk += VIDEO_LEN
                else:
                    bitrate_avg_arr.append(np.mean(bit_rate_all[scheme][log])/1000)
                    bitrate_total += np.sum(np.array(bit_rate_all[scheme][log])/1000) #Mbis
                    total_chunk += len(bit_rate_all[scheme][log])
        else:
            for log in bit_rate_all[scheme]:
                if len(bit_rate_all[scheme][log]) >= 40:
                    bitrate_avg_arr.append(np.mean(bit_rate_all[scheme][log][:40])/1000)
                    bitrate_total += np.sum(np.array(bit_rate_all[scheme][log][:40])/1000) #Mbis
                    total_chunk += 40
                else:
                    bitrate_avg_arr.append(np.mean(bit_rate_all[scheme][log])/1000)
                    bitrate_total += np.sum(np.array(bit_rate_all[scheme][log])/1000) #Mbis
                    total_chunk += len(bit_rate_all[scheme][log])
        summay_all[scheme]['avg_br'] = np.mean(bitrate_avg_arr)
        summay_all[scheme]['all_br'] = bitrate_avg_arr

        reward_avg_arr = []
        reward_total = 0

        # reward 
        for log in raw_reward_all[scheme]:
            if len(raw_reward_all[scheme][log]) >= VIDEO_LEN:
                reward_avg_arr.append(np.mean(raw_reward_all[scheme][log][1:VIDEO_LEN]))
                reward_total += np.sum(np.array(raw_reward_all[scheme][log][1:VIDEO_LEN])) 
            else:
                reward_avg_arr.append(np.mean(raw_reward_all[scheme][log]))
                reward_total += np.sum(np.array(raw_reward_all[scheme][log])) #Mbis

        summay_all[scheme]['reward'] = reward_avg_arr

        # avg stall rate
        stall_time_all = float(0)
        total_playback_time = 0
        avg_stall_arr = []
        summay_all[scheme]['all_stalled_rate'] = []
        if scheme != '_4s' and scheme != 'rollbackMPC4s':
            for log in stall_all[scheme]:
                if len(stall_all[scheme][log]) >= VIDEO_LEN:
                    avg_stall_arr.append(np.sum(np.array(stall_all[scheme][log][1:VIDEO_LEN]))/(158+np.sum(np.array(stall_all[scheme][log][1:VIDEO_LEN]))))
                    stall_time_all += float(np.sum(np.array(stall_all[scheme][log][1:VIDEO_LEN], dtype=float))) # seconds
                    total_playback_time = total_playback_time + 158 + np.sum(np.array(stall_all[scheme][log][:VIDEO_LEN]))
                else:
                    avg_stall_arr.append(np.sum(np.array(stall_all[scheme][log]))/(len(stall_all[scheme][log])+np.sum(np.array(stall_all[scheme][log]))))
                    stall_time_all += float(np.sum(np.array(stall_all[scheme][log], dtype=float))) # seconds
                    total_playback_time = total_playback_time + len(stall_all[scheme][log]) + np.sum(np.array(stall_all[scheme][log]))
        else:
            for log in stall_all[scheme]:
                if len(stall_all[scheme][log]) >= 40:
                    avg_stall_arr.append(np.sum(np.array(stall_all[scheme][log][:40]))/(158+np.sum(np.array(stall_all[scheme][log][:40]))))
                    stall_time_all += float(np.sum(np.array(stall_all[scheme][log][:40], dtype=float))) # seconds
                    total_playback_time = total_playback_time + 158 + np.sum(np.array(stall_all[scheme][log][:40]))
                else:
                    avg_stall_arr.append(np.sum(np.array(stall_all[scheme][log]))/(len(stall_all[scheme][log])+np.sum(np.array(stall_all[scheme][log]))))
                    stall_time_all += float(np.sum(np.array(stall_all[scheme][log], dtype=float))) # seconds
                    total_playback_time = total_playback_time + len(stall_all[scheme][log])*4 + np.sum(np.array(stall_all[scheme][log]))
        # print("total stall time %f" % stall_time_all)
        # print("total playback time %f" % total_playback_time)
        summay_all[scheme]['time_stalled_rate'] = np.mean(avg_stall_arr) * 100 # percentage
        summay_all[scheme]['all_stalled_rate'] = np.array(avg_stall_arr) * 100


    time_all_chk = {}
    bit_rate_all_chk = {}
    buff_all_chk = {}
    stall_all_chk = {}
    bw_all_chk = {}
    raw_reward_all_chk = {}
    summary_all_chk = {}
    for scheme in SCHEMES_CHK:
        time_all_chk[scheme] = {}
        raw_reward_all_chk[scheme] = {}
        bit_rate_all_chk[scheme] = {}
        buff_all_chk[scheme] = {}
        stall_all_chk[scheme] = {}
        bw_all_chk[scheme] = {}

    log_files = os.listdir(RESULTS_FOLDER_CHK)
    for log_file in log_files:

        time_ms = []
        bit_rate = []
        buff = []
        bw = []
        stall = []
        reward = []


        with open(RESULTS_FOLDER_CHK + log_file, 'rb') as f:
            for line in f:
                try:
                    parse = line.split()
                    if len(parse) <= 1:
                        break
                    time_ms.append(float(parse[0]))
                    bit_rate.append(int(parse[1]))
                    buff.append(float(parse[2]))
                    stall.append(float(parse[3]))
                    bw.append(float(parse[4]) / float(parse[5]) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                    reward.append(float(parse[6]))
                except ZeroDivisionError:
                    bw.append(float(parse[4]) / (float(parse[5])+1) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                    reward.append(float(parse[6]))
        
        time_ms = np.array(time_ms)
        time_ms -= time_ms[0]

        for scheme in SCHEMES_CHK:
            if scheme in log_file :
                if scheme == 'fastMPC' and 'interface' in log_file:
                    continue
                if scheme == 'fastMPC' and '_4s' in log_file:
                    continue
                if scheme == 'fastMPC' and '_2s' in log_file:
                    continue
                if scheme == 'interface' and 'interfaceMPC' in log_file:
                    continue
                if scheme == 'robustMPC' and 'truthrobustMPC' in log_file:
                    continue
                if scheme == 'rollbackMPC' and 'rollbackMPC4s' in log_file:
                    continue
                if scheme == 'RB' and 'truthRB' in log_file:
                    continue
                time_all_chk[scheme][log_file[len('log_' + str(scheme) + '_'):]] = time_ms
                bit_rate_all_chk[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bit_rate
                buff_all_chk[scheme][log_file[len('log_' + str(scheme) + '_'):]] = buff
                stall_all_chk[scheme][log_file[len('log_' + str(scheme) + '_'):]] = stall
                bw_all_chk[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bw
                raw_reward_all_chk[scheme][log_file[len('log_' + str(scheme) + '_'):]] = reward
                break
    


    # calculate mean bitrate and stall rate
    for scheme in SCHEMES_CHK:
        summary_all_chk[scheme] = {}
        # avg bitrate
        bitrate_avg_arr = []
        bitrate_total = 0
        total_chunk = 0
        summary_all_chk[scheme]['all_br'] = []

        for log in bit_rate_all_chk[scheme]:
            if len(bit_rate_all_chk[scheme][log]) >= VIDEO_LEN_CHK[scheme]:
                bitrate_avg_arr.append(np.mean(bit_rate_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]])/1000)
                bitrate_total += np.sum(np.array(bit_rate_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]])/1000) #Mbis
                total_chunk += (VIDEO_LEN_CHK[scheme]-1)

        
        summary_all_chk[scheme]['avg_br'] = np.mean(bitrate_avg_arr)
        summary_all_chk[scheme]['all_br'] = bitrate_avg_arr

        reward_avg_arr = []
        reward_total = 0

        # reward 
        for log in raw_reward_all_chk[scheme]:
            reward_avg_arr.append(np.mean(raw_reward_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]]))
            reward_total += np.sum(np.array(raw_reward_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]])) 

        summary_all_chk[scheme]['reward'] = reward_avg_arr

        # avg stall rate
        stall_time_all = float(0)
        total_playback_time = 0
        avg_stall_arr = []
        summary_all_chk[scheme]['all_stalled_rate'] = []

        for log in stall_all_chk[scheme]:
            if len(stall_all_chk[scheme][log]) >= VIDEO_LEN_CHK[scheme]:
                avg_stall_arr.append(np.sum(np.array(stall_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]]))/(158+np.sum(np.array(stall_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]]))))
                stall_time_all += float(np.sum(stall_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]], dtype=float)) # seconds
                total_playback_time = total_playback_time + 158 + np.sum(np.array(stall_all_chk[scheme][log][1:VIDEO_LEN_CHK[scheme]]))

        summary_all_chk[scheme]['time_stalled_rate'] = np.mean(avg_stall_arr) * 100 # percentage
        summary_all_chk[scheme]['all_stalled_rate'] = np.array(avg_stall_arr) * 100


    time_all_pred = {}
    bit_rate_all_pred = {}
    buff_all_pred = {}
    bw_all_pred = {}
    raw_reward_all_pred = {}
    for scheme in SCHEMES_PRED:
        time_all_pred[scheme] = {}
        raw_reward_all_pred[scheme] = {}
        bit_rate_all_pred[scheme] = {}
        buff_all_pred[scheme] = {}
        bw_all_pred[scheme] = {}

    log_files = os.listdir(RESULTS_FOLDER_PRED)
    for log_file in log_files:

        time_ms = []
        bit_rate = []
        buff = []
        bw = []
        reward = []


        with open(RESULTS_FOLDER_PRED + log_file, 'rb') as f:
            for line in f:
                parse = line.split()
                if len(parse) <= 1:
                    break
                time_ms.append(float(parse[0]))
                bit_rate.append(int(parse[1]))
                buff.append(float(parse[2]))
                bw.append(float(parse[4]) / (float(parse[5])+1) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                reward.append(float(parse[6]))
        
        time_ms = np.array(time_ms)
        time_ms -= time_ms[0]
        

        for scheme in SCHEMES_PRED:
            if scheme in log_file:
                if scheme == 'robustMPC' and 'truthrobustMPC' in log_file:
                    continue
                if scheme == 'RB' and 'truthRB' in log_file:
                    continue
                if scheme == 'fastMPC' and 'interface' in log_file:
                    continue
                if scheme == 'rollbackMPC' and 'rollbackMPC4s' in log_file:
                    continue
                if scheme == 'fastMPC' and '4s' in log_file:
                    continue
                time_all_pred[scheme][log_file[len('log_' + str(scheme) + '_'):]] = time_ms
                bit_rate_all_pred[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bit_rate
                buff_all_pred[scheme][log_file[len('log_' + str(scheme) + '_'):]] = buff
                bw_all_pred[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bw
                raw_reward_all_pred[scheme][log_file[len('log_' + str(scheme) + '_'):]] = reward
                break

    # ---- ---- ---- ----
    # Reward records
    # ---- ---- ---- ----


    log_file_all = []
    reward_all = {}
    for scheme in SCHEMES_PRED:
        reward_all[scheme] = []

    for l in time_all_pred[SCHEMES_PRED[0]]:
        schemes_check = True
        if schemes_check:
            log_file_all.append(l)
            for scheme in SCHEMES_PRED:
                if scheme == SIM_DP:
                    reward_all[scheme].append(raw_reward_all_pred[scheme][l])
                elif scheme == '_4s' or scheme == 'rollbackMPC4s':
                    reward_all[scheme].append(np.sum(raw_reward_all_pred[scheme][l][1:40])/40)
                else:
                    reward_all[scheme].append(np.sum(raw_reward_all_pred[scheme][l][1:VIDEO_LEN])/VIDEO_LEN)

    mean_rewards = {}
    std_rewards = {}
    for scheme in SCHEMES_PRED:
        mean_rewards[scheme] = np.mean(reward_all[scheme])
        std_rewards[scheme] = np.std(reward_all[scheme])

    reward_values = [mean_rewards[k] for k in SCHEMES_PRED]
    reward_err = [std_rewards[k] for k in SCHEMES_PRED]


    width=0.35
    gs1 = gridspec.GridSpec(3, 1)
    fig, (pred, ax0, ax) = plt.subplots(1, 3, figsize=(15, 4.3))
    pred.set_ylabel('Normalized QoE', fontsize=20)
    pred.set_xlabel('(a) Throughput Prediction Scheme', fontsize=20)
    pred.bar(SCHEMES_NEW_PRED[0], np.array(reward_values[0])/np.max(np.array(list(mean_rewards.values()))), width, color='r', edgecolor='darkred', ecolor='r', linewidth=2)
    pred.bar(SCHEMES_NEW_PRED[1], np.array(reward_values[1])/np.max(np.array(list(mean_rewards.values()))), width, color='r', edgecolor='darkred', ecolor='r', linewidth=2)
    pred.bar(SCHEMES_NEW_PRED[2], np.array(reward_values[2])/np.max(np.array(list(mean_rewards.values()))), width, color='r', edgecolor='darkred', ecolor='r', linewidth=2)
    pred.tick_params(axis='both', which='major', labelsize=20)
    pred.set_xticklabels(SCHEMES_NEW_PRED, fontsize=16, rotation=8)
    
    ax.set_xlabel('(c) Interface Selection Scheme', fontsize=20)
    x = np.arange(1,len(SCHEMES)+1)  # the label locations
    ax.set_xticks(x)
    ax.set_ylim(0,1.2)
    ax.set_yticks(np.arange(0, 1.2, 0.25), minor=False)
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.set_xticklabels(SCHEMES_NEW, fontsize=16)
    ax2 = ax.twinx()
    ax2.set_ylim(0,12)
    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax2.yaxis.label.set_color('blue')
    ax2.set_ylabel('Playback Time\n Spent on Stall (%)', fontsize=20, rotation=270, labelpad=45, color='blue')
    x = np.arange(1, len(SCHEMES)+1)  # the label locations

    bitrates = []
    std_bitrates = []
    stalls = []
    conf_stalls = []
    for idx in range(len(SCHEMES)):
        m_x, left_m_x, right_m_x = mean_confidence_interval(summay_all[SCHEMES[idx]]['all_stalled_rate'])
        bitrates.append(summay_all[SCHEMES[idx]]['avg_br']/160.0)
        std_bitrates.append(np.std(summay_all[SCHEMES[idx]]['all_br'])/160.0)
        stalls.append(summay_all[SCHEMES[idx]]['time_stalled_rate'])  
        conf_stalls.append(right_m_x-m_x)


    bar1 = ax.bar(x-width/2, bitrates, width/1.2, yerr=std_bitrates, capsize=4, color='sandybrown', edgecolor='saddlebrown', ecolor='saddlebrown', linewidth=2, label='Bitrate')
    bar2 = ax2.bar(x+width/2, stalls, width/1.2, yerr=conf_stalls, capsize=4, color='white', edgecolor='blue', ecolor='blue', linewidth=2, label='Video Stall', hatch='/')


    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.tick_params(axis='y', which='major', labelsize=20, colors='blue')

    ax0.set_ylabel('Normalized Bitrate', fontsize=20)
    ax0.set_xlabel('(b) Chunk Length', fontsize=20)
    x = np.arange(1,len(SCHEMES)+1)  # the label locations
    ax0.set_ylim(0,1.2)
    ax0.tick_params(axis='both', which='major', labelsize=15)
    ax3 = ax0.twinx()
    ax3.set_ylim(0,25)
    ax3.set_yticks(np.arange(0, 25.0, 5.0), minor=False)
    ax3.tick_params(axis='both', which='major', labelsize=20)
    width=0.35
    x = np.arange(1, len(SCHEMES)+1)  # the label locations

    bitrates = []
    std_bitrates = []
    stalls = []
    conf_stalls = []
    all_stalls = []
    for idx in range(len(SCHEMES_CHK)):
        m_x, left_m_x, right_m_x = mean_confidence_interval(summary_all_chk[SCHEMES_CHK[idx]]['all_stalled_rate'])
        bitrates.append(summary_all_chk[SCHEMES_CHK[idx]]['avg_br']/160.0)
        std_bitrates.append(np.std(summary_all_chk[SCHEMES_CHK[idx]]['all_br'])/160.0)
        stalls.append(summary_all_chk[SCHEMES_CHK[idx]]['time_stalled_rate'])  
        conf_stalls.append(right_m_x-m_x)
        all_stalls.append(summary_all_chk[SCHEMES_CHK[idx]]['all_stalled_rate'])
        

    bar1 = ax0.bar(x-width/2, bitrates, width/1.2, yerr=std_bitrates, capsize=4, color='sandybrown', edgecolor='saddlebrown', ecolor='saddlebrown', linewidth=2, label='Bitrate')

    shifted_X = x + width/2

    bp = ax3.boxplot(all_stalls, positions=shifted_X, autorange=True, showfliers=False, widths=0.25, patch_artist=True)
    for cap in bp['caps']:
        cap.set(color='blue', linewidth=2)
    for med in bp['medians']:
        med.set(color='blue', linewidth=2)
    # bp['medians'][0].set(color='blue', linewidth=2)
    for whisker in bp['whiskers']:
        whisker.set(color='blue', linewidth=1.5, linestyle=':')
    for box in bp['boxes']:
        box.set(color='blue')
        box.set(linewidth=2)
        box.set(facecolor = 'white')
        box.set(hatch='/')
    bp['boxes'][0].set(label='Video Stall')
    ax0.tick_params(axis='both', which='major', labelsize=20)
    ax0.set_xlim(0.5, 3.5)
    ax0.set_xticks(x)
    ax0.set_xticklabels(SCHEMES_NEW_CHK, fontsize=16)
    ax0.spines['top'].set_visible(False)
    ax3.spines['top'].set_visible(False)
    ax3.tick_params(axis='both', which='major', labelsize=20)
    ax3.tick_params(axis='y', which='major', labelsize=20, colors='blue')
    # ax0.legend([bar1, bp["boxes"][0]], ['Bitrate', 'Video Stall'], loc='upper center', bbox_to_anchor=(0.50, 1.08), fontsize=15, facecolor='whitesmoke') #bbox_to_anchor=(0.42, 1.00),
    # ax2.legend([bar1, bp["boxes"][0]], ['Bitrate', 'Video Stall'], loc='upper right', fontsize=15, facecolor='whitesmoke')
    ax0.legend([bar1], ['Bitrate'], fontsize=15, loc='upper center', bbox_to_anchor=(0.7, 1.1), facecolor='whitesmoke') #bbox_to_anchor=(0.15, 1.2),
    ax.legend([bar2], ['Video Stall'], fontsize=15, loc='upper center', bbox_to_anchor=(0.1, 1.1), facecolor='whitesmoke')
    ax0.set_axisbelow(True)
    ax.set_axisbelow(True)
    ax0.yaxis.grid(linestyle='dashed')
    ax.set_axisbelow(True)
    ax.yaxis.grid(linestyle='dashed')
    plt.subplots_adjust(wspace=.02)
    fig.tight_layout()
    plt.savefig("plots/figure18.pdf")
    plt.savefig("plots/figure18.png")
    plt.savefig("plots/figure18.eps")
    return

if __name__ == '__main__':
	main()