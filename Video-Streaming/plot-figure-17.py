import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import scipy.stats


RESULTS_FOLDER = './Full-Results/Sec. 5.2 Existing ABR/5G/results_driving/'
RESULTS_FOLDER_4G = './Full-Results/Sec. 5.2 Existing ABR/4G/results_driving/'
NUM_BINS = 100
BITS_IN_BYTE = 8.0
MILLISEC_IN_SEC = 1000.0
M_IN_B = 1000000.0
VIDEO_LEN = 158
VIDEO_BIT_RATE = [20000, 40000, 60000, 80000, 110000, 160000]
COLOR_MAP = plt.cm.jet #nipy_spectral, Set1,Paired 
SIM_DP = 'sim_dp'
SCHEMES = ['BB', 'RB', 'BOLA', 'fastMPC', 'robustMPC', 'RL', 'FESTIVE']

SCHEMES_NEW = ['BBA', 'RB', 'BOLA', 'fastMPC', 'rMPC', 'RL', 'FESTIVE'] #label for plot
LABEL = ['4G', '5G']

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

        if len(time_ms) == 0:
            continue
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
    

    # parse the 4G results
    time_all_4G = {}
    bit_rate_all_4G = {}
    buff_all_4G = {}
    stall_all_4G = {}
    bw_all_4G= {}
    raw_reward_all_4G = {}
    summay_all_4G = {}
    for scheme in SCHEMES:
        time_all_4G[scheme] = {}
        raw_reward_all_4G[scheme] = {}
        bit_rate_all_4G[scheme] = {}
        buff_all_4G[scheme] = {}
        stall_all_4G[scheme] = {}
        bw_all_4G[scheme] = {}

    # stall_total = 0.0
    log_files = os.listdir(RESULTS_FOLDER_4G)
    for log_file in log_files:

        time_ms = []
        bit_rate = []
        buff = []
        bw = []
        stall = []
        reward = []

        with open(RESULTS_FOLDER_4G + log_file, 'rb') as f:
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
                time_all_4G[scheme][log_file[len('log_' + str(scheme) + '_'):]] = time_ms
                bit_rate_all_4G[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bit_rate
                buff_all_4G[scheme][log_file[len('log_' + str(scheme) + '_'):]] = buff
                stall_all_4G[scheme][log_file[len('log_' + str(scheme) + '_'):]] = stall
                bw_all_4G[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bw
                raw_reward_all_4G[scheme][log_file[len('log_' + str(scheme) + '_'):]] = reward
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
        # print(scheme)
        # print(bitrate_total)
        # print(total_chunk)
        # print(float(bitrate_total)/total_chunk)
        # print(bitrate_avg_arr)
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

        # print("avg reward for scheme %s is %f", (scheme, np.mean(reward_avg_arr)))

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
                    total_playback_time = total_playback_time + 158 + np.sum(np.array(stall_all[scheme][log][:40]))
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

        # 4G summarize
        summay_all_4G[scheme] = {}
        bitrate_avg_arr_4G = []
        for log in bit_rate_all_4G[scheme]:
            if len(bit_rate_all_4G[scheme][log]) >= VIDEO_LEN:
                bitrate_avg_arr_4G.append(np.mean(bit_rate_all_4G[scheme][log][1:VIDEO_LEN])/1000)
            else:
                bitrate_avg_arr_4G.append(np.mean(bit_rate_all_4G[scheme][log])/1000)
        summay_all_4G[scheme]['avg_br'] = np.mean(bitrate_avg_arr_4G)
        summay_all_4G[scheme]['all_br'] = bitrate_avg_arr_4G

        # reward 
        reward_avg_arr_4G = []
        for log in raw_reward_all_4G[scheme]:
            # print raw_reward_all_4G[scheme][log]
            if len(raw_reward_all_4G[scheme][log]) >= VIDEO_LEN:
                reward_avg_arr_4G.append(np.mean(raw_reward_all_4G[scheme][log][1:VIDEO_LEN]))
            else:
                reward_avg_arr_4G.append(np.mean(raw_reward_all_4G[scheme][log]))
        summay_all_4G[scheme]['reward'] = reward_avg_arr

        # avg stall rate
        avg_stall_arr_4G = []
        summay_all_4G[scheme]['all_stalled_rate'] = []
        for log in stall_all_4G[scheme]:
            if len(stall_all_4G[scheme][log]) >= VIDEO_LEN:
                avg_stall_arr_4G.append(np.sum(np.array(stall_all_4G[scheme][log][1:VIDEO_LEN]))/(158+np.sum(np.array(stall_all_4G[scheme][log][1:VIDEO_LEN]))))
            else:
                avg_stall_arr_4G.append(np.sum(np.array(stall_all_4G[scheme][log]))/(len(stall_all_4G[scheme][log])+np.sum(np.array(stall_all_4G[scheme][log]))))
        summay_all_4G[scheme]['time_stalled_rate'] = np.mean(avg_stall_arr_4G) * 100 # percentage
        summay_all_4G[scheme]['all_stalled_rate'] = np.array(avg_stall_arr_4G) * 100


    fig, (ax, ax2, ax3) = plt.subplots(1, 3, figsize=(20,4))
    # ax = fig.add_subplot(111)
    ax.set_xlim(12, 0)
    ax.set_ylim(0.5, 1)
    ax.hlines(0.8, 0, 5, linestyle='--', color='maroon')
    ax.vlines(5, 0.8, 1, linestyle='--', color='maroon')
    ax.set_axisbelow(True)
    ax.xaxis.grid(linestyle='dashed')
    ax.yaxis.grid(linestyle='dashed')
    plt.xticks(np.arange(12, 0.0, -4.0))
    # ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    for scheme in SCHEMES:
        # print(np.mean(summay_all[scheme]['reward']))
        # print("mean for scheme %s are %f, %f" % (scheme, np.mean(summay_all[scheme]['all_stalled_rate']), np.mean(summay_all[scheme]['all_br'])))
        m_x, left_m_x, right_m_x = mean_confidence_interval(summay_all[scheme]['all_stalled_rate'])
        m_y, left_m_y, right_m_y = mean_confidence_interval(summay_all[scheme]['all_br'])
        # print("confidence interval scheme %s are %f, %f" % (scheme, m_x-left_m_x, m_y-left_m_y))
        # print("variance scheme %s are %f, %f" % (scheme, np.std(summay_all[scheme]['all_stalled_rate']), np.std(summay_all[scheme]['all_br'])))
        ax.errorbar(summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br']/160.0, xerr=m_x-left_m_x, yerr=(m_y-left_m_y)/160.0, capsize=4)
        ax.scatter(summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br']/160.0)
        if scheme == "interfaceMPC":
            ax.annotate(scheme + ' (no overhead)', (summay_all[scheme]['time_stalled_rate']-0.1, summay_all[scheme]['avg_br']+0.01), fontsize=19)
        elif scheme == "interface":
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate']+1.3, summay_all[scheme]['avg_br']/160.0-0.6/160.0), fontsize=19)
        elif scheme == "truthMPC":
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate']-0.1, summay_all[scheme]['avg_br']/160.0+0.1/160.0), fontsize=19)
        elif scheme == "BB":
            ax.annotate("BBA", (summay_all[scheme]['time_stalled_rate']+1.3, summay_all[scheme]['avg_br']/160.0-0.05), fontsize=19)
        elif scheme == 'RL':
            ax.annotate("Pensieve", (summay_all[scheme]['time_stalled_rate']-0.1, summay_all[scheme]['avg_br']/160.0+2/160.0), fontsize=19)
        elif scheme == 'BOLA':
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate']-0.1, summay_all[scheme]['avg_br']/160.0-0.05), fontsize=19)
        elif scheme == 'rollbackMPC4s':
            ax.annotate("4s (w/ rollback)", (summay_all[scheme]['time_stalled_rate']-0.1, summay_all[scheme]['avg_br']/160.0+0.1/160.0), fontsize=19)
        elif scheme == 'fastMPC':
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate']-0.1, summay_all[scheme]['avg_br']/160.0-0.05), fontsize=19)
        elif scheme == 'FESTIVE':
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate']+2.5, summay_all[scheme]['avg_br']/160.0+0.01), fontsize=19)
        elif scheme == 'robustMPC':
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate']+1.6, summay_all[scheme]['avg_br']/160.0+0.04), fontsize=19)
        else:
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate']-0.1, summay_all[scheme]['avg_br']/160.0+2/160.0), fontsize=19)
    
    ax.annotate("Better QoE", fontsize=20,
        horizontalalignment="center",
        xy=(11, 0.55), xycoords='data',
        xytext=(9, 0.63), textcoords='data',
        arrowprops=dict(arrowstyle="<-, head_width=0.3",
                        connectionstyle="arc3", lw=3)
            )

    # bb = t.get_bbox_patch()
    # bb.set_boxstyle("rarrow", pad=0.6)
    ax.set_xlabel('Time Spent on Stall (%)', fontsize=20)
    ax.set_ylabel('Normalized Bitrate', fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=20)

    # fig = plt.figure(figsize=(8,6))
    # ax2 = fig.add_subplot(111)
    ax2.set_xlim(12, 0)
    ax2.set_ylim(0.5, 1)
    ax2.hlines(0.8, 0, 5, linestyle='--', color='maroon')
    ax2.vlines(5, 0.8, 1, linestyle='--', color='maroon')
    ax2.set_axisbelow(True)
    ax2.xaxis.grid(linestyle='dashed')
    ax2.yaxis.grid(linestyle='dashed')
    plt.xticks(np.arange(12, 0.0, -4.0))
    for scheme in SCHEMES:
        m_x, left_m_x, right_m_x = mean_confidence_interval(summay_all_4G[scheme]['all_stalled_rate'])
        m_y, left_m_y, right_m_y = mean_confidence_interval(summay_all_4G[scheme]['all_br'])
        # print("mean for scheme %s are %f, %f" % (scheme, np.mean(summay_all_4G[scheme]['all_stalled_rate']), np.mean(summay_all_4G[scheme]['all_br'])))
        ax2.errorbar(summay_all_4G[scheme]['time_stalled_rate'], summay_all_4G[scheme]['avg_br']/20.0, xerr=m_x-left_m_x, yerr=(m_y-left_m_y)/20.0, capsize=4)
        ax2.scatter(summay_all_4G[scheme]['time_stalled_rate'], summay_all_4G[scheme]['avg_br']/20.0)
        if scheme == 'fastMPC':
            ax2.annotate(scheme, (summay_all_4G[scheme]['time_stalled_rate']+2.5, summay_all_4G[scheme]['avg_br']/20.0-0.05), fontsize=19)
        elif scheme == 'robustMPC':
            ax2.annotate(scheme, (summay_all_4G[scheme]['time_stalled_rate']+1.55, summay_all_4G[scheme]['avg_br']/20.0-0.053), fontsize=19)
        elif scheme == 'RL':
            # ax2.annotate('Pensieve', (summay_all_4G[scheme]['time_stalled_rate']+6, summay_all_4G[scheme]['avg_br']/20.0-0.03), fontsize=15)
            pass
        elif scheme == 'BB':
            ax2.annotate('BBA', (summay_all_4G[scheme]['time_stalled_rate']-0.15, summay_all_4G[scheme]['avg_br']/20.0-0.05), fontsize=19)
        elif scheme == 'FESTIVE':
            ax2.annotate(scheme, (summay_all_4G[scheme]['time_stalled_rate']+3.55, summay_all_4G[scheme]['avg_br']/20.0-0.02), fontsize=19)
        else:
            ax2.annotate(scheme, (summay_all_4G[scheme]['time_stalled_rate']-0.15, summay_all_4G[scheme]['avg_br']/20.0+0.01), fontsize=19)

    ax2.set_xlabel('Time Spent on Stall (%)', fontsize=20)
    ax2.set_ylabel('Normalized Bitrate', fontsize=20)
    ax2.tick_params(axis='both', which='major', labelsize=20)

    ax2.annotate("Better QoE", fontsize=20,
        horizontalalignment="center",
        xy=(11, 0.55), xycoords='data',
        xytext=(9, 0.63), textcoords='data',
        arrowprops=dict(arrowstyle="<-, head_width=0.3",
                        connectionstyle="arc3", lw=3)
        )
    ax2.annotate("Pensieve", fontsize=19,
        horizontalalignment="center",
        xy=(summay_all_4G['RL']['time_stalled_rate'], summay_all_4G['RL']['avg_br']/20.0), xycoords='data',
        xytext=(10, 0.9), textcoords='data',
        arrowprops=dict(arrowstyle="<-, head_width=0.1",
            connectionstyle="arc3, rad=0.3", lw=1, ls='--', color='saddlebrown'
        )
    )


    # fig = plt.figure(figsize=(8,6))
    # ax3 = fig.add_subplot(111)
    ax3.yaxis.grid(linestyle='dashed')
    ax3.set_ylabel('Playback Time\n Spent on Stall (%)', fontsize=20)
    # ax.set_xlabel('ABR Algorithm', fontsize=20)
    width=1.0
    x = np.arange(1,len(SCHEMES)+1)  # the label locations
    # colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(mean_rewards.keys()))]
    for idx in range(len(SCHEMES)):
        # print(SCHEMES[idx] + " median 5G: " + str(np.min(summay_all[SCHEMES[idx]]['all_stalled_rate'])) + " median 4G: " + str(np.min(summay_all_4G[SCHEMES[idx]]['all_stalled_rate'])))
        # print(np.median(summay_all[SCHEMES[idx]]['all_stalled_rate'])/np.median(summay_all_4G[SCHEMES[idx]]['all_stalled_rate']))
        b1 = ax3.boxplot(summay_all_4G[SCHEMES[idx]]['all_stalled_rate'], positions=np.array([x[idx]-width/5]), autorange=True, showfliers=False, widths=0.25, patch_artist=True)
        b1['boxes'][0].set(color='saddlebrown')
        b1['boxes'][0].set(linewidth=2)
        b1['boxes'][0].set(facecolor = 'sandybrown')
        b1['boxes'][0].set(label=LABEL[0])
        for cap in b1['caps']:
            cap.set(color='saddlebrown', linewidth=2)
        b1['medians'][0].set(color='saddlebrown', linewidth=2)
        for whisker in b1['whiskers']:
            whisker.set(color='saddlebrown', linewidth=1.5, linestyle=':')
        b2 = ax3.boxplot(summay_all[SCHEMES[idx]]['all_stalled_rate'], positions=np.array([x[idx]+width/5]), autorange=True, showfliers=False, widths=0.25, patch_artist=True)
        b2['boxes'][0].set(color='blue')
        b2['boxes'][0].set(linewidth=2)
        b2['boxes'][0].set(facecolor = 'white')
        b2['boxes'][0].set(hatch='/')
        b2['boxes'][0].set(label=LABEL[1])
        for cap in b2['caps']:
            cap.set(color='blue', linewidth=2)
        b2['medians'][0].set(color='blue', linewidth=2)
        for whisker in b2['whiskers']:
            whisker.set(color='blue', linewidth=1.5, linestyle=':')
    ax3.set_xticks(x)
    ax3.set_xticklabels(SCHEMES_NEW, fontsize=17, rotation=25)
    ax3.set_xlim([0.2, 8])
    ax3.tick_params(axis='both', which='major', labelsize=20)
    plt.yticks(np.arange(0, 20.0, 5.0))
    plt.legend([b1["boxes"][0], b2["boxes"][0]], ['4G', '5G'], fontsize=20, facecolor='whitesmoke')
    fig.tight_layout()
    # plt.show()
    plt.savefig("plots/figure17.pdf")
    plt.savefig("plots/figure17.png")
    plt.savefig("plots/figure17.eps")

    return

if __name__ == '__main__':
	main()