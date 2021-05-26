#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import base64
import urllib
import sys
import os
import json
import time
os.environ['CUDA_VISIBLE_DEVICES']=''

import numpy as np
import time
import itertools

######################## FAST MPC #######################

S_INFO = 5  # bit_rate, buffer_size, rebuffering_time, bandwidth_measurement, chunk_til_video_end
S_LEN = 8  # take how many frames in the past
MPC_FUTURE_CHUNK_COUNT = 5
VIDEO_BIT_RATE = [2000, 4000, 8000, 12000, 16000, 20000]  # Kbps
BITRATE_REWARD = [1, 2, 3, 12, 15, 20]
BITRATE_REWARD_MAP = {0: 0, 2000: 1, 4000: 2, 8000: 3, 12000: 12, 20000: 15, 40000: 20}
M_IN_K = 1000.0
BUFFER_NORM_FACTOR = 10.0
CHUNK_TIL_VIDEO_END_CAP = 157.0
TOTAL_VIDEO_CHUNKS = 157
DEFAULT_QUALITY = 0  # default video quality without agent
REBUF_PENALTY = 20  # 1 sec rebuffering -> this number of Mbps
SMOOTH_PENALTY = 1
TRAIN_SEQ_LEN = 100  # take as a train batch
MODEL_SAVE_INTERVAL = 100
RANDOM_SEED = 42
RAND_RANGE = 1000
SUMMARY_DIR = './results'
LOG_FILE = './results/log'
LOG_BW = './bw_prediction/log'
# in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
NN_MODEL = None
startup_time = time.time()

CHUNK_COMBO_OPTIONS = []

# video chunk sizes
size_video1 = [334476,11007815,8849724,3191121,1661718,1315024,698359,730082,4047415,2863079,4167844,5571764,4925652,2030157,2240782,2211169,382046,1113969,820127,6357933,4814284,3419258,3944328,4284196,3022025,2248581,9946363,11684632,1849732,1942795,1704756,1697111,1529441,1568649,1677618,1415096,1894067,1186604,1068386,1700843,2536859,4742872,4955535,1260540,3605246,2770338,1855168,1666915,1555467,1008919,1227619,1015853,384076,295687,1328674,1492829,1484812,1868314,1253406,887933,1153403,1249023,1423973,1060162,1080597,1156442,2222640,2587311,2178351,3121089,2857420,1702477,1531670,1863424,1987392,2505586,9620218,2561608,3633991,3324070,1560020,1429188,1754144,1626020,1739228,1722735,1538145,1473412,1498968,2247334,3156442,1895098,1939135,1842874,2235830,2202171,2242042,1081763,2409013,1615028,1413467,1632450,5664827,4578115,1783835,1093613,975642,1658005,3055257,5355572,3278424,2318501,2473561,1730311,1455812,2869222,3226650,2705936,2998622,2928342,3059979,3367422,1950694,1541020,2926720,2991202,3002106,2015412,2894863,2185316,3370605,3492243,1307592,1881404,1806471,1945842,2538877,2298557,2831497,3200905,2180586,1500505,1939246,1599193,2364826,2517454,1883143,1726706,707364,796460,596962,947625,832859,151562,90390,50278,26471,40620]
size_video2 = [335737,11642034,9061343,2846282,1379579,1083781,533454,508812,2514829,1861181,2835412,4074608,3844696,1630440,1712120,1662097,243072,793783,531720,5045162,3858422,2713103,3070467,3391518,2424462,1798203,8032438,9808342,1491397,1560434,1396705,1392963,1276651,1314540,1407326,1196263,1627563,987649,864635,1366872,2025194,2595110,3209770,1080711,3005751,2251469,1498439,1329461,1254418,879546,1055149,883588,347560,267077,1128983,1257735,1265527,1524381,995715,674495,885875,928626,1062903,799389,812821,856497,1700457,1970588,1652704,2412882,2213643,1294662,1157734,1439296,1558739,1982918,7754684,2122146,2951725,2707022,1258293,1132545,1405832,1314152,1387998,1362449,1219048,1160520,1180684,1739841,2506643,1488968,1507223,1424538,1714252,1710495,1751030,875075,1998050,1336691,1179696,1291599,4082189,3284299,1412347,909953,808459,1370506,2325287,4018361,2566881,1890880,2005276,1359018,1134985,2294159,2601076,2155956,2411136,2355841,2451277,2690936,1552444,1207957,2277016,2335112,2348675,1575943,2268474,1727401,2744751,2853458,1012501,1508766,1446069,1560727,2029094,1857827,2294649,2580724,1699891,1171248,1549070,1299702,1877910,1991172,1469635,1366341,564365,622694,449729,748394,676139,123294,70186,50504,24518,36255]
size_video3 = [334022,9869079,7078153,1798447,946554,768486,398693,358785,1838971,1382199,2052265,3005823,2879726,1267052,1316661,1263534,150125,555328,323573,4001900,3029729,2083035,2281353,2599148,1926191,1427209,6361262,7838407,1127469,1179779,1078151,1086181,1029204,1054251,1132419,977239,1356524,801103,686354,1097671,1598754,1172467,1818385,890138,2345010,1735323,1153767,1020736,965874,762421,883591,750345,317174,245047,926307,1028305,1059850,1192343,755853,481371,632141,627832,711870,555825,558836,579891,1196803,1363367,1137409,1719028,1582861,901281,798342,1031599,1153146,1472726,5789048,1677334,2233179,2053317,953056,835287,1072056,1005233,1040790,1009563,911305,852154,864029,1222697,1822246,1089714,1097827,1010680,1202900,1236644,1286142,675899,1606544,1066218,948747,970495,2424481,1902440,1031824,732536,645392,1104267,1592936,2618824,1820110,1448467,1521463,1006183,831839,1735764,1969173,1618621,1825708,1780068,1844656,2010421,1158554,873968,1651288,1697771,1712532,1149171,1666069,1269548,2108361,2206878,752992,1143645,1081066,1175321,1515596,1397801,1735873,1955680,1256122,872352,1175796,1004408,1393009,1466703,1060685,1011581,422329,458857,318722,566180,531853,95334,52187,32002,22693,26015]
size_video4 = [334032,6594552,4402139,1043358,567502,472646,274373,222226,1213073,927735,1463326,2054811,1928241,898461,929156,886614,90752,376357,197626,2995445,2226527,1501029,1558531,1856343,1433055,1055512,4647286,5615227,764013,795179,741228,760332,769288,779865,838056,709811,997014,576726,481423,753582,1035369,420196,876880,659947,1538893,1116845,770196,678418,663968,596131,642153,561624,252381,198847,672121,755974,808254,848961,531866,318027,411948,387504,434147,349710,349575,360691,767399,838282,690145,1110276,1024586,566069,498552,676507,770118,962786,3596154,1238543,1526348,1410236,659155,563159,756304,730895,731159,678447,621176,556204,568078,747231,1138250,724195,728813,631476,728502,819353,864484,496044,1258285,818447,743969,689321,1121938,667445,682795,564053,493680,823677,878603,1192759,1046702,982243,1004344,687087,564465,1193260,1350143,1085010,1231535,1204741,1227805,1328172,755940,542221,1043429,1080376,1087843,735758,1086740,818102,1450968,1535058,516135,781150,723162,787496,1008090,920901,1141486,1305395,854393,602217,819411,705221,905448,951381,663404,662118,284661,305283,197766,385891,375542,71077,37732,26108,20475,22446]
size_video5 = [60629,1072422,1121405,728514,508013,395538,297276,247728,1172629,740561,905521,975494,873443,420093,432386,430845,114664,272444,180836,1138797,922146,760526,866360,821406,576666,399536,2503359,2158640,352618,355918,335697,336592,257949,254944,280530,274347,407719,221839,208863,331412,560025,480043,639392,307952,852435,548688,370252,330522,298688,200752,280436,254413,92084,85090,285433,361866,347546,396965,264442,201160,227906,301480,401522,296659,306130,320231,505705,560900,477844,593358,552627,356467,298528,372582,432861,576027,2234357,560537,577595,643057,299663,284317,341921,337442,361712,356599,349268,330614,348018,462525,845902,452278,403995,391858,447328,442130,467709,242111,564856,387198,371539,364606,883642,678863,376102,268819,249895,388840,510672,813914,569070,587015,600946,296369,286854,566404,695021,594594,629131,474066,623944,654640,416970,336627,598150,590759,584579,441665,567172,503622,629808,657376,207349,432669,432968,461467,530571,602139,716984,719449,335356,213548,339747,339538,477871,491670,462611,415951,156751,181344,138957,198063,181915,46143,32698,12091,9218,10349]
size_video6 = [28717,460475,550011,401179,293086,214799,175377,126522,626817,406114,441827,462042,399182,223999,253238,232808,53518,132258,92415,561148,471077,384976,400244,397638,293991,211138,1087425,857095,184468,183961,176954,182889,140413,144943,154268,158694,228494,126130,118843,188016,304948,170066,272575,186904,456927,280891,191747,173510,154053,110074,160637,149779,56754,53519,169833,215358,206134,217891,140910,102461,116607,155212,217018,183768,180999,190757,256572,266457,226765,291626,266212,180131,150082,194148,217851,280960,858567,332031,305540,333656,160196,147947,181748,182744,193051,187271,187611,178722,181938,234596,434199,233056,211986,206031,231293,230178,244545,129141,292677,214984,207438,191321,349717,238341,166138,143551,134758,234393,235703,350754,274054,331523,335983,155670,149398,300323,381707,307893,330196,246363,318766,331330,222025,172849,283772,295812,292595,237899,278978,251210,331975,336166,103282,226221,231602,243196,276595,319717,362132,341295,160167,109795,177029,179671,243891,253748,245996,221647,79754,89303,74829,98095,96538,25513,16279,7912,5970,7621]

def get_chunk_size(quality, index):
    if ( index < 0 or index > TOTAL_VIDEO_CHUNKS ):
        return 0
    # note that the quality and video labels are inverted (i.e., quality 8 is highest and this pertains to video1)
    sizes = {5: size_video1[index], 4: size_video2[index], 3: size_video3[index], 2: size_video4[index], 1: size_video5[index], 0: size_video6[index]}
    return sizes[quality]

def make_request_handler(input_dict):

    class Request_Handler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.input_dict = input_dict
            self.log_file = input_dict['log_file']
            #self.saver = input_dict['saver']
            self.s_batch = input_dict['s_batch']
            self.bw_file = input_dict['log_bw']
            # hard code the entire trace here
            # self.startup_time = time.time()
            #self.a_batch = input_dict['a_batch']
            #self.r_batch = input_dict['r_batch']
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            print post_data

            if ( 'pastThroughput' in post_data ):
                # @Hongzi: this is just the summary of throughput/quality at the end of the load
                # so we don't want to use this information to send back a new quality
                print "Summary: ", post_data
            else:
                # option 1. reward for just quality
                # reward = post_data['lastquality']
                # option 2. combine reward for quality and rebuffer time
                #           tune up the knob on rebuf to prevent it more
                # reward = post_data['lastquality'] - 0.1 * (post_data['RebufferTime'] - self.input_dict['last_total_rebuf'])
                # option 3. give a fixed penalty if video is stalled
                #           this can reduce the variance in reward signal
                # reward = post_data['lastquality'] - 10 * ((post_data['RebufferTime'] - self.input_dict['last_total_rebuf']) > 0)

                # option 4. use the metric in SIGCOMM MPC paper
                rebuffer_time = float(post_data['RebufferTime'] -self.input_dict['last_total_rebuf'])

                # --linear reward--
                reward = VIDEO_BIT_RATE[post_data['lastquality']] / M_IN_K \
                        - REBUF_PENALTY * rebuffer_time / M_IN_K \
                        - SMOOTH_PENALTY * np.abs(VIDEO_BIT_RATE[post_data['lastquality']] -
                                                  self.input_dict['last_bit_rate']) / M_IN_K

                # --log reward--
                # log_bit_rate = np.log(VIDEO_BIT_RATE[post_data['lastquality']] / float(VIDEO_BIT_RATE[0]))   
                # log_last_bit_rate = np.log(self.input_dict['last_bit_rate'] / float(VIDEO_BIT_RATE[0]))

                # reward = log_bit_rate \
                #          - 4.3 * rebuffer_time / M_IN_K \
                #          - SMOOTH_PENALTY * np.abs(log_bit_rate - log_last_bit_rate)

                # --hd reward--
                # reward = BITRATE_REWARD[post_data['lastquality']] \
                #         - 8 * rebuffer_time / M_IN_K - np.abs(BITRATE_REWARD[post_data['lastquality']] - BITRATE_REWARD_MAP[self.input_dict['last_bit_rate']])

                self.input_dict['last_bit_rate'] = VIDEO_BIT_RATE[post_data['lastquality']]
                self.input_dict['last_total_rebuf'] = post_data['RebufferTime']

                # retrieve previous state
                if len(self.s_batch) == 0:
                    state = [np.zeros((S_INFO, S_LEN))]
                else:
                    state = np.array(self.s_batch[-1], copy=True)

                # compute bandwidth measurement
                video_chunk_fetch_time = post_data['lastChunkFinishTime'] - post_data['lastChunkStartTime']
                video_chunk_size = post_data['lastChunkSize']

                # compute number of video chunks left
                video_chunk_remain = TOTAL_VIDEO_CHUNKS - self.input_dict['video_chunk_coount']
                self.input_dict['video_chunk_coount'] += 1

                # dequeue history record
                state = np.roll(state, -1, axis=1)

                # this should be S_INFO number of terms
                try:
                    state[0, -1] = VIDEO_BIT_RATE[post_data['lastquality']] / float(np.max(VIDEO_BIT_RATE))
                    state[1, -1] = post_data['buffer'] / BUFFER_NORM_FACTOR
                    state[2, -1] = rebuffer_time / M_IN_K
                    state[3, -1] = float(video_chunk_size) / float(video_chunk_fetch_time) / M_IN_K  # kilo byte / ms
                    state[4, -1] = np.minimum(video_chunk_remain, CHUNK_TIL_VIDEO_END_CAP) / float(CHUNK_TIL_VIDEO_END_CAP)
                except ZeroDivisionError:
                    # this should occur VERY rarely (1 out of 3000), should be a dash issue
                    # in this case we ignore the observation and roll back to an eariler one
                    if len(self.s_batch) == 0:
                        state = [np.zeros((S_INFO, S_LEN))]
                    else:
                        state = np.array(self.s_batch[-1], copy=True)

                # log wall_time, bit_rate, buffer_size, rebuffer_time, video_chunk_size, download_time, reward
                self.log_file.write(str(time.time()) + '\t' +
                                    str(VIDEO_BIT_RATE[post_data['lastquality']]) + '\t' +
                                    str(post_data['buffer']) + '\t' +
                                    str(rebuffer_time / M_IN_K) + '\t' +
                                    str(video_chunk_size) + '\t' +
                                    str(video_chunk_fetch_time) + '\t' +
                                    str(reward) + '\n')
                self.log_file.flush()

                # pick bitrate according to MPC           
                # first get harmonic mean of last 5 bandwidths
                past_bandwidths = state[3,-5:]
                while past_bandwidths[0] == 0.0:
                    past_bandwidths = past_bandwidths[1:]
                #if ( len(state) < 5 ):
                #    past_bandwidths = state[3,-len(state):]
                #else:
                #    past_bandwidths = state[3,-5:]
                bandwidth_sum = 0
                for past_val in past_bandwidths:
                    bandwidth_sum += (1/float(past_val))
                future_bandwidth = 1.0/(bandwidth_sum/len(past_bandwidths))
                self.bw_file.write(str(time.time()) + '\t' + str(future_bandwidth) + '\n')
                self.bw_file.flush()
                # print("future bandwidth est = %d" % future_bandwidth)
                # print("time passed since start: %f" % (time.time()-startup_time))
                # future_bandwidth_truth = self.ground_truth[int(time.time()-startup_time)+1]
                # print("future bandwidth = %d" % future_bandwidth_truth)

                # future chunks length (try 4 if that many remaining)
                last_index = int(post_data['lastRequest'])
                future_chunk_length = MPC_FUTURE_CHUNK_COUNT
                if ( TOTAL_VIDEO_CHUNKS - last_index < 4 ):
                    future_chunk_length = TOTAL_VIDEO_CHUNKS - last_index

                # all possible combinations of 5 chunk bitrates (9^5 options)
                # iterate over list and for each, compute reward and store max reward combination
                max_reward = -100000000
                best_combo = ()
                start_buffer = float(post_data['buffer'])
                #start = time.time()
                for full_combo in CHUNK_COMBO_OPTIONS:
                    combo = full_combo[0:future_chunk_length]
                    # calculate total rebuffer time for this combination (start with start_buffer and subtract
                    # each download time and add 2 seconds in that order)
                    curr_rebuffer_time = 0
                    curr_buffer = start_buffer
                    bitrate_sum = 0
                    smoothness_diffs = 0
                    last_quality = int(post_data['lastquality'])
                    for position in range(0, len(combo)):
                        chunk_quality = combo[position]
                        index = last_index + position + 1 # e.g., if last chunk is 3, then first iter is 3+0+1=4
                        download_time = (get_chunk_size(chunk_quality, index)/1000000.)/future_bandwidth # this is MB/MB/s --> seconds
                        if ( curr_buffer < download_time ):
                            curr_rebuffer_time += (download_time - curr_buffer)
                            curr_buffer = 0
                        else:
                            curr_buffer -= download_time
                        curr_buffer += 1
                        
                        # linear reward
                        bitrate_sum += VIDEO_BIT_RATE[chunk_quality]
                        smoothness_diffs += abs(VIDEO_BIT_RATE[chunk_quality] - VIDEO_BIT_RATE[last_quality])

                        # log reward
                        # log_bit_rate = np.log(VIDEO_BIT_RATE[chunk_quality] / float(VIDEO_BIT_RATE[0]))
                        # log_last_bit_rate = np.log(VIDEO_BIT_RATE[last_quality] / float(VIDEO_BIT_RATE[0]))
                        # bitrate_sum += log_bit_rate
                        # smoothness_diffs += abs(log_bit_rate - log_last_bit_rate)

                        # hd reward
                        # bitrate_sum += BITRATE_REWARD[chunk_quality]
                        # smoothness_diffs += abs(BITRATE_REWARD[chunk_quality] - BITRATE_REWARD[last_quality])

                        last_quality = chunk_quality
                    # compute reward for this combination (one reward per 5-chunk combo)
                    # bitrates are in Mbits/s, rebuffer in seconds, and smoothness_diffs in Mbits/s

                    # linear reward 
                    reward = (bitrate_sum/1000.) - (REBUF_PENALTY*curr_rebuffer_time) - (smoothness_diffs/1000.)

                    # log reward
                    # reward = (bitrate_sum) - (4.3*curr_rebuffer_time) - (smoothness_diffs)

                    # hd reward
                    # reward = bitrate_sum - (8*curr_rebuffer_time) - (smoothness_diffs)

                    if ( reward > max_reward ):
                        max_reward = reward
                        best_combo = combo
                # send data to html side (first chunk of best combo)
                send_data = 0 # no combo had reward better than -1000000 (ERROR) so send 0
                if ( best_combo != () ): # some combo was good
                    send_data = str(best_combo[0])

                end = time.time()
                #print "TOOK: " + str(end-start)

                end_of_video = False
                if ( post_data['lastRequest'] == TOTAL_VIDEO_CHUNKS ):
                    send_data = "REFRESH"
                    end_of_video = True
                    self.input_dict['last_total_rebuf'] = 0
                    self.input_dict['last_bit_rate'] = DEFAULT_QUALITY
                    self.input_dict['video_chunk_coount'] = 0
                    # self.log_file.write('\n')  # so that in the log we know where video ends

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', len(send_data))
                self.send_header('Access-Control-Allow-Origin', "*")
                self.end_headers()
                self.wfile.write(send_data)

                # record [state, action, reward]
                # put it here after training, notice there is a shift in reward storage

                if end_of_video:
                    self.s_batch = [np.zeros((S_INFO, S_LEN))]
                else:
                    self.s_batch.append(state)

        def do_GET(self):
            print >> sys.stderr, 'GOT REQ'
            self.send_response(200)
            #self.send_header('Cache-Control', 'Cache-Control: no-cache, no-store, must-revalidate max-age=0')
            self.send_header('Cache-Control', 'max-age=3000')
            self.send_header('Content-Length', 20)
            self.end_headers()
            self.wfile.write("console.log('here');")

        def log_message(self, format, *args):
            return

    return Request_Handler


def run(server_class=HTTPServer, port=8333, log_file_path=LOG_FILE, bw_file_path=LOG_BW):

    np.random.seed(RANDOM_SEED)

    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)

    # make chunk combination options
    for combo in itertools.product([0,1,2,3,4,5], repeat=5):
        CHUNK_COMBO_OPTIONS.append(combo)

    with open(log_file_path, 'wb') as log_file:
        with open(bw_file_path, 'wb') as bw_file:
            bw_file.write(str(startup_time)+'\n')
            s_batch = [np.zeros((S_INFO, S_LEN))]

            last_bit_rate = DEFAULT_QUALITY
            last_total_rebuf = 0
            # need this storage, because observation only contains total rebuffering time
            # we compute the difference to get

            video_chunk_count = 0

            input_dict = {'log_file': log_file,
                        'log_bw': bw_file,
                        'last_bit_rate': last_bit_rate,
                        'last_total_rebuf': last_total_rebuf,
                        'video_chunk_coount': video_chunk_count,
                        's_batch': s_batch}

            # interface to abr_rl server
            handler_class = make_request_handler(input_dict=input_dict)

            server_address = ('localhost', port)
            httpd = server_class(server_address, handler_class)
            print 'Listening on port ' + str(port)
            httpd.serve_forever()


def main():
    startup_time = time.time()
    if len(sys.argv) == 2:
        trace_file = sys.argv[1]
        run(log_file_path=LOG_FILE + '_fastMPC_' + trace_file, bw_file_path=LOG_BW + '_fastMPC_' + trace_file)
    else:
        run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Keyboard interrupted."
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
