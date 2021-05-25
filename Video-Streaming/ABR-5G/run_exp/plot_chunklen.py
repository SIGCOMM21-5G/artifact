import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import scipy.stats


RESULTS_FOLDER = './results_chunk_length/'
NUM_BINS = 100
BITS_IN_BYTE = 8.0
MILLISEC_IN_SEC = 1000.0
M_IN_B = 1000000.0
VIDEO_BIT_RATE = [20000, 40000, 60000, 80000, 110000, 160000]
COLOR_MAP = plt.cm.jet #nipy_spectral, Set1,Paired 
SIM_DP = 'sim_dp'
SCHEMES = ['_4s', '_2s', 'fastMPC']
VIDEO_LEN = {'_4s': 40, '_2s': 80, 'fastMPC': 158}

SCHEMES_NEW = ['4s', '2s', '1s'] #label for plot
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
    summary_all = {}
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

        print(log_file)

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
                time_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = time_ms
                bit_rate_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bit_rate
                buff_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = buff
                stall_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = stall
                bw_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bw
                raw_reward_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = reward
                break
    


    # calculate mean bitrate and stall rate
    for scheme in SCHEMES:
        summary_all[scheme] = {}
        # avg bitrate
        bitrate_avg_arr = []
        bitrate_total = 0
        total_chunk = 0
        summary_all[scheme]['all_br'] = []

        for log in bit_rate_all[scheme]:
            if len(bit_rate_all[scheme][log]) >= VIDEO_LEN[scheme]:
                bitrate_avg_arr.append(np.mean(bit_rate_all[scheme][log][:VIDEO_LEN[scheme]])/1000)
                bitrate_total += np.sum(np.array(bit_rate_all[scheme][log][:VIDEO_LEN[scheme]])/1000) #Mbis
                total_chunk += (VIDEO_LEN[scheme]-1)

        
        summary_all[scheme]['avg_br'] = np.mean(bitrate_avg_arr)
        summary_all[scheme]['all_br'] = bitrate_avg_arr

        reward_avg_arr = []
        reward_total = 0

        # reward 
        for log in raw_reward_all[scheme]:
            # print raw_reward_all[scheme][log]
            reward_avg_arr.append(np.mean(raw_reward_all[scheme][log][1:VIDEO_LEN[scheme]]))
            reward_total += np.sum(np.array(raw_reward_all[scheme][log][1:VIDEO_LEN[scheme]])) 

        summary_all[scheme]['reward'] = reward_avg_arr

        # avg stall rate
        stall_time_all = float(0)
        total_playback_time = 0
        avg_stall_arr = []
        summary_all[scheme]['all_stalled_rate'] = []

        for log in stall_all[scheme]:
            # print(scheme + ' ' + str(len(stall_all[scheme][log])))
            if len(stall_all[scheme][log]) >= VIDEO_LEN[scheme]:
                if scheme == '_2s':
                    print(len(stall_all[scheme][log][:VIDEO_LEN[scheme]]))
                    print(log + str(np.sum(np.array(stall_all[scheme][log][:VIDEO_LEN[scheme]]))/(158+np.sum(np.array(stall_all[scheme][log][:VIDEO_LEN[scheme]])))))
                    print(np.sum(np.array(stall_all[scheme][log][:VIDEO_LEN[scheme]])))
                avg_stall_arr.append(np.sum(np.array(stall_all[scheme][log][:VIDEO_LEN[scheme]]))/(158+np.sum(np.array(stall_all[scheme][log][:VIDEO_LEN[scheme]]))))
                stall_time_all += float(np.sum(stall_all[scheme][log][:VIDEO_LEN[scheme]], dtype=float)) # seconds
                total_playback_time = total_playback_time + 158 + np.sum(np.array(stall_all[scheme][log][:VIDEO_LEN[scheme]]))

        # print(avg_stall_arr)
        # print("total stall time %f" % stall_time_all)
        # print("total playback time %f" % total_playback_time)
        summary_all[scheme]['time_stalled_rate'] = np.mean(avg_stall_arr) * 100 # percentage
        summary_all[scheme]['all_stalled_rate'] = np.array(avg_stall_arr) * 100
        # print(summary_all[scheme]['time_stalled_rate'])



    fig = plt.figure(figsize=(6, 4.5))
    ax = fig.add_subplot(111)
    ax.set_ylabel('Normalized Bitrate', fontsize=20)
    ax.set_xlabel('Chunk Length', fontsize=20)
    x = np.arange(1,len(SCHEMES)+1)  # the label locations
    ax.set_ylim(0,1.2)
    ax.tick_params(axis='both', which='major', labelsize=15)
    ax2 = ax.twinx()
    ax2.set_ylim(0,25)
    ax2.set_yticks(np.arange(0, 25.0, 5.0), minor=False)
    # ax2.yticks(np.arange(0, 22.0, 5.0))
    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax2.set_ylabel('Playback Time\n Spent on Stall (%)', fontsize=20)
    width=0.35
    x = np.arange(1, len(SCHEMES)+1)  # the label locations

    bitrates = []
    std_bitrates = []
    stalls = []
    conf_stalls = []
    all_stalls = []
    for idx in range(len(SCHEMES)):
        m_x, left_m_x, right_m_x = mean_confidence_interval(summary_all[scheme]['all_stalled_rate'])
        bitrates.append(summary_all[SCHEMES[idx]]['avg_br']/160.0)
        std_bitrates.append(np.std(summary_all[SCHEMES[idx]]['all_br'])/160.0)
        stalls.append(summary_all[SCHEMES[idx]]['time_stalled_rate'])  
        conf_stalls.append(right_m_x-m_x)
        all_stalls.append(summary_all[SCHEMES[idx]]['all_stalled_rate'])
        


    # for idx in range(len(SCHEMES)):
    #     m_x, left_m_x, right_m_x = mean_confidence_interval(summay_all[scheme]['all_stalled_rate'])
    bar1 = ax.bar(x-width/2, bitrates, width/1.2, yerr=std_bitrates, capsize=4, color='sandybrown', edgecolor='saddlebrown', ecolor='saddlebrown', linewidth=2, label='Bitrate')
    # bar2 = ax2.bar(x+width/2, stalls, width/1.2, yerr=conf_stalls, capsize=4, color='white', edgecolor='blue', ecolor='blue', linewidth=2, label='Video Stall', hatch='/')
    # for idx in range(len(SCHEMES)):
    #     print(x[idx]+width/2)
    #     # bar = ax.bar(x[idx]-width/2, bitrates[idx], width, yerr=std_bitrates[idx], capsize=4, color='sandybrown', edgecolor='saddlebrown', ecolor='saddlebrown', linewidth=2, label='Bitrate')
    
    #     ax2.boxplot(summary_all[SCHEMES[idx]]['time_stalled_rate'], positions=[x[idx]+width/2], autorange=True, showfliers=False, widths=0.2)
    print(len(stalls))
    print(all_stalls)
    shifted_X = x + width/2

    bp = ax2.boxplot(all_stalls, positions=shifted_X, autorange=True, showfliers=False, widths=0.25, patch_artist=True)
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
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.set_xlim(0.5, 3.5)
    ax.set_xticks(x)
    ax.set_xticklabels(SCHEMES_NEW, fontsize=20)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax.legend([bar1, bp["boxes"][0]], ['Bitrate', 'Video Stall'], loc='upper center', bbox_to_anchor=(0.50, 1.08), fontsize=15, facecolor='whitesmoke') #bbox_to_anchor=(0.42, 1.00),
    # ax2.legend([bar1, bp["boxes"][0]], ['Bitrate', 'Video Stall'], loc='upper right', fontsize=15, facecolor='whitesmoke')
    fig.tight_layout()
    # plt.show()
    plt.savefig("Chunklength.png")

    return

if __name__ == '__main__':
	main()