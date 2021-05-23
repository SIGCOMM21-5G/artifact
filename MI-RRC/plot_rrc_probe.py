import matplotlib.pyplot as plt
import sys
import numpy as np
from scipy import optimize

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
        return "5G_NR"

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
    elif (net_type == '5G_NR'):
        return "#ff7f0e"

def piecewise_linear(x, x0, y0, k1, k2):
    return np.piecewise(x, [x < x0], [lambda x:k1*x + y0-k1*x0, lambda x:k2*x + y0-k2*x0])

def main():
    filename = sys.argv[1]
    opened_file = open(file=filename)
    Lines = opened_file.readlines()
    time = {}
    times = {}
    network_type = {}
    rtt_count = {}
    interval_plot = []
    rtt_plot = []
    colors = []
    net_types = []
    colors_dict = {'Unknown': '#17becf', 'WiFi': "#bcbd22", '2G': "#7f7f7f", '3G': "#e377c2", '4G': "#1f77b4", '5G': "#ff7f0e", '5G_NR': "#ff7f0e"}

    for line in Lines:
        try:
            data_line = line.split()
            interval = float(data_line[0])
            rtt1 = int(data_line[2])
            rtt2 = int(data_line[3])
            network = translate_network_type(data_line[4])
            # print(line.split("\t")[3].split(" ")[0])
            is_data_good = data_line[-1]
        except IndexError:
            continue
        except ValueError:
            continue
        # print(interval)
        if is_data_good == "YEP":
            print("yep")
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

    fig, ax = plt.subplots()
    for g in np.unique(np.array(net_types)):
        idx = np.where(np.array(net_types) == g)
        ax.scatter(interval_plot[idx], rtt_plot[idx], c=colors_dict[g], label=g)
        # ax.plot(interval_plot[idx], rtt_plot[idx], c=colors_dict[g], label=g)
    # ax.plot(interval_plot, rtt_plot, c=colors_dict['5G_NR'])
    print(np.sort(interval_plot))
    
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
    # ax.annotate('', xy=(1.330, 107), xycoords='data', xytext=(1.260, 107), textcoords='data', color='red', arrowprops=dict(arrowstyle="<->",
    #                         connectionstyle="arc3"))
    # ax.annotate(r'$T_{long\_DRX}$', xy=(1.265, 97), weight='bold', fontsize=13)
    ax.legend(loc='lower right')
    plt.xlabel("Idel Time between Packets (s)")
    plt.ylabel("RTT (ms)")
    ax.grid()
    plt.show()
    return 0


if __name__ == "__main__":
    main()