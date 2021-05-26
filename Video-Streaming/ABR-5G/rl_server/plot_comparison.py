import numpy as np
import matplotlib.pyplot as plt


LOG_PATH = './results/log'
LOG_PATH2 = './results/log_fastMPC_5g_trace_1_driving'
PLOT_SAMPLES = 300
THROUGHPUT_PATH='../sim/cooked_traces/5g_trace_1_driving'


time_stamp = []
bit_rates = []
buffer_occupancies = []
rebuffer_times = []
rewards = []
time_stamp2 = []
bit_rates2 = []
buffer_occupancies2 = []
rebuffer_times2 = []
rewards2 = []
throughput = []
trace_timestamp = []

with open(LOG_PATH, 'rb') as f:
    for line in f:
        parse = line.split()
        time_stamp.append(float(parse[0]))
        bit_rates.append(float(parse[1]))
        buffer_occupancies.append(float(parse[2]))
        rebuffer_times.append(float(parse[3]))
        rewards.append(float(parse[6]))

with open(LOG_PATH2, 'rb') as f:
    for line in f:
        parse = line.split()
        time_stamp2.append(float(parse[0]))
        bit_rates2.append(float(parse[1]))
        buffer_occupancies2.append(float(parse[2]))
        rebuffer_times2.append(float(parse[3]))
        rewards2.append(float(parse[6]))

with open(THROUGHPUT_PATH, 'rb') as f:
    for line in f:
        parse = line.split()
        trace_timestamp.append(float(parse[0]))
        throughput.append(int(parse[1]))

time_stamp = time_stamp - np.min(time_stamp)
time_stamp2 = time_stamp2 - np.min(time_stamp2)

f, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)

truth = ax1.plot(time_stamp[-PLOT_SAMPLES:], rewards[-PLOT_SAMPLES:], label='truth')
fastMPC = ax1.plot(time_stamp2[-PLOT_SAMPLES:], rewards2[-PLOT_SAMPLES:], label='fastMPC')
ax1.set_title('Average reward: ' + str(np.mean(rewards[-PLOT_SAMPLES:])) + ', ' + str(np.mean(rewards2[-PLOT_SAMPLES:])))
ax1.set_ylabel('QoE')

ax2.plot(trace_timestamp[-PLOT_SAMPLES:], throughput[-PLOT_SAMPLES:])
ax2.set_ylabel('Throughput (Mbps)')

ax3.plot(time_stamp[-PLOT_SAMPLES:], bit_rates[-PLOT_SAMPLES:])
ax3.plot(time_stamp2[-PLOT_SAMPLES:], bit_rates2[-PLOT_SAMPLES:])
ax3.set_ylabel('Bitrate (Kpbs)')

# ax3.plot(time_stamp[-PLOT_SAMPLES:], buffer_occupancies[-PLOT_SAMPLES:])
# ax3.set_ylabel('buffer occupancy (sec)')

ax4.plot(time_stamp[-PLOT_SAMPLES:], rebuffer_times[-PLOT_SAMPLES:])
ax4.plot(time_stamp2[-PLOT_SAMPLES:], rebuffer_times2[-PLOT_SAMPLES:])
ax4.set_ylabel('Rebuffer Time (sec)')
ax4.set_xlabel('Time (s)')
ax4.legend(['MPC w/ future BW', 'fastMPC'])

f.subplots_adjust(hspace=0)

plt.show()