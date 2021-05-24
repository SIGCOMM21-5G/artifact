import matplotlib.pyplot as plt
import sys
import numpy as np
from scipy import optimize
import matplotlib.patches as patches

def translate_network_type(net_type):
    if (net_type == '0'):
        return "Unknown"
    elif (net_type == '1'):
        return "WiFi"
    elif (net_type == '2'):
        return "2G"
    elif (net_type == '3'):
        return "3G"
    elif (net_type == '4'):
        return "4G"
    elif (net_type == '5'):
        return "5G"
    elif (net_type == '6'):
        return "5G"

def determine_color_net_type(net_type):
    if (net_type == 'Unknown'):
        return '#17becf'
    elif (net_type == 'WiFi'):
        return "#bcbd22"
    elif (net_type == '2G'):
        return "#7f7f7f"
    elif (net_type == '3G'):
        return "#e377c2"
    elif (net_type == '4G'):
        return "#1f77b4"
    elif (net_type == '5G'):
        return "#ff7f0e"
    elif (net_type == '5G'):
        return "#ff7f0e"

def piecewise_linear(x, x0, y0, k1, k2):
    return np.piecewise(x, [x < x0], [lambda x:k1*x + y0-k1*x0, lambda x:k2*x + y0-k2*x0])

def parse_raw_log(filename):
    with open(filename, 'r') as f:
        Lines = f.readlines()
        time = {}
        times = {}
        network_type = {}
        rtt_count = {}
        interval_plot = []
        rtt_plot = []
        colors = []
        net_types = []
        count = 0
        for line in Lines:
            try:
                data_line = line.split(",")
                interval = float(data_line[1])
                rtt1 = int(data_line[3])
                rtt2 = int(data_line[4])
                network = translate_network_type(data_line[-2])
                # print(line.split("\t")[3].split(" ")[0])
                is_data_good = data_line[-1][:-1]
                count += 1
            except IndexError:
                continue
            except ValueError:
                continue
            if is_data_good == "YEP" and count % 10 == 0:
                if interval in time:
                        times[interval].append((rtt1+rtt2)/2)
                        time[interval] += (rtt1+rtt2)/2
                        rtt_count[interval] += 1
                        network_type[interval] = network
                    # else:
                    #     time[interval] += 0
                else:
                        times[interval] = [(rtt1+rtt2)/2]
                        time[interval] = (rtt1+rtt2)/2
                        rtt_count[interval] = 1
                        network_type[interval] = network
        for k,v in times.items():
            interval_plot.append(k)
            rtt_plot.append(np.median(np.array(v)))
            colors.append(determine_color_net_type(network_type[k]))
            net_types.append(network_type[k])
        interval_plot = np.array(interval_plot)
        rtt_plot = np.array(rtt_plot)
        colors = np.array(colors)
    return interval_plot, rtt_plot, net_types

def parse_log_old(filename):
    with open(filename, 'r') as f:
        Lines = f.readlines()
        time = {}
        times = {}
        network_type = {}
        rtt_count = {}
        interval_plot = []
        rtt_plot = []
        colors = []
        net_types = []
        for line in Lines:
            try:
                data_line = line.split(",")
                interval = float(data_line[0])
                rtt1 = int(data_line[2])
                rtt2 = int(data_line[3])
                network = translate_network_type(data_line[-2])
                # print(line.split("\t")[3].split(" ")[0])
                is_data_good = data_line[-1][:-1]
                # print(is_data_good)
            except IndexError:
                continue
            except ValueError:
                continue
            if is_data_good == "YEP":
                if interval in time:
                        times[interval].append((rtt1+rtt2)/2)
                        time[interval] += (rtt1+rtt2)/2
                        rtt_count[interval] += 1
                        network_type[interval] = network
                    # else:
                    #     time[interval] += 0
                else:
                        times[interval] = [(rtt1+rtt2)/2]
                        time[interval] = (rtt1+rtt2)/2
                        rtt_count[interval] = 1
                        network_type[interval] = network
        for k,v in times.items():
            interval_plot.append(k)
            rtt_plot.append(np.median(np.array(v)))
            colors.append(determine_color_net_type(network_type[k]))
            net_types.append(network_type[k])
        interval_plot = np.array(interval_plot)
        rtt_plot = np.array(rtt_plot)
        colors = np.array(colors)
    return interval_plot, rtt_plot, net_types

def main():
    filename_SA = sys.argv[1]
    filename_NSA1 = sys.argv[2]
    filename_NSA2 = sys.argv[3]
    filename_4G = sys.argv[4]
    opened_file = open(file=filename_NSA2)
    Lines = opened_file.readlines()
    time = {}
    times = {}
    network_type = {}
    rtt_count = {}
    interval_plot = []
    rtt_plot = []
    colors = []
    net_types = []
    colors_dict = {'Unknown': '#17becf', 'WiFi': "#bcbd22", '2G': "#7f7f7f", '3G': "#e377c2", '4G': "#1f77b4", '5G': "#ff7f0e"}

    for line in Lines:
        try:
            data_line = line.split(" ")
            interval = float(data_line[2])
            rtt1 = int(line.split("\t")[1])
            rtt2 = int(line.split("\t")[2])
            network = translate_network_type(line.split("\t")[3].split(" ")[0])
            # print(line.split("\t")[3].split(" ")[0])
            is_data_good = data_line[-1].split("\n")[0]
            # print(is_data_good)
        except IndexError:
            continue
        except ValueError:
            continue
        # print(interval)
        if is_data_good == "YEP":
            if interval in time:
                    times[interval].append((rtt1+rtt2)/2)
                    time[interval] += (rtt1+rtt2)/2
                    rtt_count[interval] += 1
                    network_type[interval] = network
                # else:
                #     time[interval] += 0
            else:
                    times[interval] = [(rtt1+rtt2)/2]
                    time[interval] = (rtt1+rtt2)/2
                    rtt_count[interval] = 1
                    network_type[interval] = network
            # else:
            #     time[interval] = 0
            #     rtt_count[interval] = 0
    
    # print(time)
    # print(rtt_count)
    print(time)
    # for k, v in time.items():
    #     interval_plot.append(k)
    #     rtt_plot.append(v/rtt_count[k])
    #     colors.append(determine_color_net_type(network_type[k]))
    #     net_types.append(network_type[k])
    
    for k,v in times.items():
        interval_plot.append(k)
        rtt_plot.append(np.median(np.array(v)))
        colors.append(determine_color_net_type(network_type[k]))
        net_types.append(network_type[k])
    # print(interval_plot)
    # print(rtt_plot)
    
    # print(colors)
    interval_plot = np.array(interval_plot)
    rtt_plot = np.array(rtt_plot)
    colors = np.array(colors)

    # xd = np.linspace(10, 15, 100)
    # p, e = optimize.curve_fit(piecewise_linear, interval_plot, rtt_plot)
    interval_sa, rtt_sa, net_types_sa = parse_log_old(filename_SA)
    interval_nsa1, rtt_nsa1, net_types_nsa1 = parse_raw_log(filename_NSA1)
    interval_4g, rtt_4g, net_types_4g = parse_raw_log(filename_4G)

    print(interval_sa)
    print(rtt_sa)
    print(interval_nsa1)
    print(rtt_nsa1)

    fig = plt.figure(figsize=(13,6))
    ax0 =fig.add_subplot(221)
    for g in np.unique(np.array(net_types_sa)):
        idx = np.where(np.array(net_types_sa) == g)
        ax0.scatter(interval_sa[idx], rtt_sa[idx], c=colors_dict[g], label=g)
    ax1 = fig.add_subplot(222)
    for g in np.unique(np.array(net_types_nsa1)):
        idx = np.where(np.array(net_types_nsa1) == g)
        ax1.scatter(interval_nsa1[idx], rtt_nsa1[idx], c=colors_dict[g], label=g)
    
    ax2 = fig.add_subplot(223)
    for g in np.unique(np.array(net_types)):
        idx = np.where(np.array(net_types) == g)
        ax2.scatter(interval_plot[idx], rtt_plot[idx], c=colors_dict[g], label=g)
    
    ax3 = fig.add_subplot(224)
    for g in np.unique(np.array(net_types_4g)):
        idx = np.where(np.array(net_types_4g) == g)
        ax3.scatter(interval_4g[idx], rtt_4g[idx], c=colors_dict[g], label=g)
        # ax.lot(interval_plot[idx], rtt_plot[idx], c=colors_dict[g], label=g)
    # ax.scatter(interval_plot, rtt_plot, c=colors, label=net_types)
    # ax.plot(xd, piecewise_linear(xd, *p))
    # plt.axvline(1.260, color='red' , linestyle='--')

    # Annotation for Ttail
    # plt.axhline(380, color='red', linestyle='--')
    # plt.axhline(1580, color='red', linestyle='--')
    # plt.axvline(12.50, color='red' , linestyle='--')
    # plt.axvline(13.75, color='red' , linestyle='--')
    # ax.annotate('$T_{tail}$', xy=(10.2, 117), xycoords='data', xytext=(10.4, 180), textcoords='data', weight='bold', fontsize=13, arrowprops=dict(arrowstyle="->",
    #                     connectionstyle="arc3"))
    # ax.annotate('', xy=(12.5, 380), xycoords='data', xytext=(13.75, 380), textcoords='data', weight='bold', arrowprops=dict(arrowstyle="<->",
    #                     connectionstyle="arc3"))
    # ax.annotate('', xy=(8, 1580), xycoords='data', xytext=(8, 380), textcoords='data', weight='bold', arrowprops=dict(arrowstyle="<->",
    #                 connectionstyle="arc3"))
    # ax.annotate(r'$T_{paging}$', xy=(12.8, 300), weight='bold', fontsize=13)
    # ax.annotate(r'$T_{paging}$ - $T_{oni}$', xy=(8.1, 900), weight='bold', fontsize=13)                        
    # ax.annotate(r'$T_{tail}$', xy=(12.5, 180), weight='bold', fontsize=13)

    # Annotation for Long DRX
    # ax.set_ylim([110,1650])
    # ax2.annotate('', xy=(1.330, 107), xycoords='data', xytext=(1.260, 107), textcoords='data', color='red', arrowprops=dict(arrowstyle="<->",
                            # connectionstyle="arc3"))
    # ax.annotate(r'$T_{long\_DRX}$', xy=(1.265, 97), weight='bold', fontsize=13)

    # ax2.axvline(10.20, color='red', linestyle='--')

    # ax2.annotate('', xy=(7.8, 400), xycoords='data', xytext=(10.2, 400), textcoords='data', arrowprops=dict(arrowstyle="<->", connectionstyle="arc3"))
    # ax2.text(7.8, 500, 'RRC_CONNECTED', fontsize=12)

    ax2.set_ylim(0, 1780)
    ax2.set_yticks(np.arange(0, 1780, 500), minor=False)
    ax2.set_xlim(7.8, 15.2)
    nsa2_conn = patches.Rectangle((7.8,1650),10.2-7.8,200,linewidth=1,edgecolor='forestgreen',facecolor='forestgreen')
    nsa2_idle = patches.Rectangle((10.2,1650),15.2-10.2,200,linewidth=1,edgecolor='magenta',facecolor='magenta')
    ax2.add_patch(nsa2_conn)
    ax2.add_patch(nsa2_idle)

    ax0.set_ylim(0, 1880)
    ax0.set_yticks(np.arange(0, 1880, 500), minor=False)
    ax0.set_xlim(7.8, 20.2)
    sa_conn = patches.Rectangle((7.8,1750),10.2-7.8,200,linewidth=1,edgecolor='forestgreen',facecolor='forestgreen', label='RRC_CONNECTED')
    sa_inac = patches.Rectangle((10.2,1750),15.0-10.2,200,linewidth=1,edgecolor='crimson',facecolor='crimson', label='RRC_INACTIVE')
    sa_idle = patches.Rectangle((15.0,1750),20.2-15,200,linewidth=1,edgecolor='magenta',facecolor='magenta', label='RRC_IDLE')
    ax0.add_patch(sa_conn)
    ax0.add_patch(sa_inac)
    ax0.add_patch(sa_idle)

    ax1.set_ylim(0, 1880)
    ax1.set_yticks(np.arange(0, 1880, 500), minor=False)
    ax1.set_xlim(7.8, 19.0)
    nsa1_conn = patches.Rectangle((7.8,1750),10.2-7.8,200,linewidth=1,edgecolor='forestgreen',facecolor='forestgreen', label='RRC_CONNECTED')
    nsa1_idle = patches.Rectangle((10.2,1750),19.0-10.2,200,linewidth=1,edgecolor='magenta',facecolor='magenta', label='RRC_IDLE')
    ax1.add_patch(nsa1_conn)
    ax1.add_patch(nsa1_idle)

    ax3.set_ylim(0, 1780)
    ax3.set_yticks(np.arange(0, 1780, 500), minor=False)
    ax3.set_xlim(7.8, 15.2)
    fourg_conn = patches.Rectangle((7.8,1650),10.2-7.8,200,linewidth=1,edgecolor='forestgreen',facecolor='forestgreen', label='RRC_CONNECTED')
    fourg_idle = patches.Rectangle((10.1,1650),15.2-10.1,200,linewidth=1,edgecolor='magenta',facecolor='magenta', label='RRC_IDLE')
    inac_label = patches.Rectangle((18.2,1650),15.0-10.2,0,linewidth=1,edgecolor='crimson',facecolor='crimson', label='RRC_INACTIVE')
    ax3.add_patch(fourg_conn)
    ax3.add_patch(fourg_idle)  
    ax3.add_patch(inac_label) 



    ax0.set_title('T-Mobile SA 5G', fontsize=18)
    ax1.set_title('T-Mobile NSA 5G', fontsize=18)
    ax2.set_title('Verizon NSA 5G', fontsize=18)
    ax3.set_title('T-Mobile 4G', fontsize=18)
    ax2.legend(loc='lower center', fontsize=15, bbox_to_anchor=(0.4, -0.8), ncol=2, facecolor='whitesmoke')
    plt.legend([fourg_conn, fourg_idle, inac_label], ['RRC_CONNECTED', 'RRC_IDLE', 'RRC_INACTIVE'], fontsize=15, ncol=3, loc='lower center', bbox_to_anchor=(0.2, -0.8), facecolor='whitesmoke')
    ax2.set_xlabel("Idle Time between Packets (s)", fontsize=18)
    ax3.set_xlabel("Idle Time between Packets (s)", fontsize=18)
    ax2.set_ylabel("RTT (ms)", fontsize=20)
    ax0.set_ylabel("RTT (ms)", fontsize=20)
    ax0.tick_params(axis="both", labelsize = 18)
    ax3.tick_params(axis="both", labelsize = 18)
    ax1.tick_params(axis="both", labelsize = 18)
    ax2.tick_params(axis="both", labelsize = 18)

    plt.tight_layout()
    plt.show()
    return 0


if __name__ == "__main__":
    main()