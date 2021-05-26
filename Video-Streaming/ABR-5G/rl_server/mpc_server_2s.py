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
CHUNK_LENGTH = 1
VIDEO_BIT_RATE = [20000, 40000, 60000, 80000, 110000, 160000]  # Kbps
BITRATE_REWARD = [1, 2, 3, 12, 15, 20]
BITRATE_REWARD_MAP = {0: 0, 20000: 1, 40000: 2, 60000: 3, 80000: 12, 110000: 15, 160000: 20}
M_IN_K = 1000.0
BUFFER_NORM_FACTOR = 10.0
CHUNK_TIL_VIDEO_END_CAP = 79.0
TOTAL_VIDEO_CHUNKS = 79
DEFAULT_QUALITY = 0  # default video quality without agent
REBUF_PENALTY = 160  # 1 sec rebuffering -> this number of Mbps
SMOOTH_PENALTY = 1
TRAIN_SEQ_LEN = 100  # take as a train batch
MODEL_SAVE_INTERVAL = 100
RANDOM_SEED = 42
RAND_RANGE = 1000
SUMMARY_DIR = './results_chunk_length'
LOG_FILE = './results_chunk_length/log'
LOG_BW = './bw_prediction/log'
# in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
NN_MODEL = None
startup_time = time.time()

CHUNK_COMBO_OPTIONS = []

# video chunk sizes - 4s
# size_video1 = [56294595,55475964,232146143,119505339,73867208,102497605,163416115,55616070,44785813,46650228,114842163,79494977,37791381,27693627,53357619,56589177,74460781,94383331,71616778,125037367,56037611,56374991,70368918,78755744,58315435,103342407,50327508,99522857,78914493,101780103,84581308,100529018,91643249,65507911,78053308,64177082,75479141,33015172,15606388,2583063]
# size_video2 = [55772286,50056342,150326571,62563120,45932342,70263691,118470939,36977194,30304543,31640106,82670502,53844172,25241849,17612046,34630358,36351090,48939331,63676925,48415094,90353482,37652804,37724381,48719934,53152745,39946823,72955109,32265160,72264134,52599470,69290902,57274675,68830684,63577183,43643258,54833000,43739515,50648540,21091748,10506893,1238719]
# size_video3 = [52080380,35753203,89266132,42874871,33598049,54500904,91612048,26589827,22374327,23286131,63003755,39032388,18212172,12496958,24456291,25454957,34601570,45759557,35020797,68058586,26906439,27105345,35702098,37903697,28838008,54194968,22170405,54781999,37566576,49638583,41041452,49312278,46514551,30826930,40580300,31751999,35909875,14291046,6623983,721973]
# size_video4 = [46482585,23554049,58794468,32649655,25172333,43153278,71663973,19809391,16918810,17577718,48559765,28923153,13475098,9258894,17773261,18251508,25018572,33578732,25978506,52358791,19880856,20052348,26918168,27693330,21574256,41372697,16205677,42416676,27758934,36412714,30294633,36125570,35075957,22434932,31025455,23538540,26251860,10421715,4167667,364267]
# size_video5 = [38164385,12219626,36401521,22323996,16843169,30292099,49776912,13219047,11298304,11538526,32612148,18897266,8835936,6164483,11144827,10988128,15548912,21367184,16871664,36186972,13022427,13192281,17916019,17503216,14210687,28080347,10740960,29126247,17920781,23591448,19784308,23056383,23563860,14403134,21210654,15410162,16948862,6535302,2277866,163722]
# size_video6 = [21721358,4488750,18417315,11585571,8665426,16527091,27079366,6833125,6120306,5826123,13641342,9692684,4799292,3493007,5408533,4708213,6795051,9714808,7866910,19329564,6371084,6461825,8848334,7918654,7233951,13345652,5522347,14183298,8587506,11572437,9706676,10607647,11973082,6780194,10953212,7294384,8093068,2796995,1126743,64205]


# video chunk sizes - 2s
size_video1 = [14929707,44147819,38785859,17658536,100767000,128611905,72652354,45807917,23321872,50623178,50601822,51548908,36583542,126634779,30885146,25605653,22421293,22469732,22397259,24249062,66035061,48981522,44641838,35151436,21430543,16231263,5636789,22059227,28191877,25042796,27281085,29208375,28005634,46665385,50358062,43912649,34250091,37283670,75230318,49667787,27387361,28690406,29114861,27245721,32434825,37866372,37936447,41256465,27287487,30827704,25575054,79838334,25759924,24302153,61129717,38286820,36197911,42345522,51428615,50441162,52354547,32364877,55076470,45561624,42485123,48838749,31126333,34386617,38284629,39356359,32004867,31856748,41686636,34394042,16769087,16947076,12008386,4269938,2413076,365650]
size_video2 = [14929707,43105425,34486272,15011672,81269154,64057580,36735456,25528337,14334576,32276831,34273990,36260396,24918887,93799287,20241275,17355447,15198239,15360788,15436753,16343051,47587683,35525202,31250786,23111848,14429131,10784692,3217684,14465961,18780277,15875012,17834356,18571865,17620576,31666077,34107477,29620330,22878143,25558418,56251068,34021932,18178511,19493600,19888317,17837557,21973455,26717133,25286817,28222242,18778843,20995407,17279929,57271091,16605283,15528125,44752080,27406301,24308925,28049052,34984477,34434092,35709667,21716378,37669861,31331830,29317532,34002742,20815648,22895006,26320380,28194931,22142667,21360054,28399044,22770724,10764942,10821142,8194238,2913477,1190822,271180]
size_video3 = [14929541,38430185,24366692,10719472,49310181,36903091,25031039,18034210,9442903,24579254,26496620,28144554,18838149,72878891,14387394,12659697,11162745,11388687,11506506,11871431,36190105,27108833,23240791,16228464,10400554,7769280,2210697,10302068,13486624,10970064,12626592,12838637,12026590,22857799,24569943,21207759,16384861,18631298,43110372,24866711,12870544,14050116,14388908,12697293,15883986,19802655,17909332,20250871,13636183,15093699,12402770,43001501,11606155,10478713,34043580,20647102,17507235,19857700,25062721,24713171,25708490,15468171,26941117,22567047,21226357,25060661,14780046,16113965,19062084,21298581,16293784,15268964,20393473,15969917,7307783,7476034,5451566,1529431,631522,242540]
size_video4 = [15083614,32419973,16057946,7003735,30367840,26794605,19133407,13530274,6354322,19118420,20993520,22176094,14532367,57086776,10720902,9427304,8395071,8641216,8784358,8828714,27746166,20920144,17629836,11640396,7641283,5787746,1607871,7638302,9986945,7775586,9107654,9125547,8446744,16792289,18051312,15522226,11985604,13977853,33359937,18918123,9447177,10436010,10721051,9321482,11825266,15061748,13025619,14864528,10218093,11253758,9213538,33044658,8606144,7523656,26413550,15937654,13049809,14565640,18398702,18169870,19076220,11345125,19706941,16618356,15778208,19123767,10802470,11707154,14247286,16616689,12162506,11210013,15057894,11566997,5397346,5336477,3555879,872839,328018,184093]
size_video5 = [14901079,25238199,8088547,3788109,16582062,18697302,13261127,8823518,3712829,13193359,14762921,15408933,9918109,39665707,7141143,6366651,5566290,5776244,5869414,5654270,18415047,14116083,11890766,7205198,4915338,3878056,1089007,5064096,6449543,4667547,5398697,5551292,5049700,10618667,11481257,9857469,7570267,9262332,23093681,12995111,6149509,6860659,7043627,6128392,7783679,10089034,8184931,9449580,6610893,7525807,6063345,22531404,5713788,4982999,18089712,10980946,8549605,9268554,11930233,11803042,12639431,7254902,12556649,10686635,10315768,13124700,6923453,7540617,9482612,11610073,8025897,7273106,9840631,7387134,3250162,3449728,1985667,382723,129434,57633]
size_video6 = [11954855,11985188,3082121,1274148,7289848,9975168,6901001,4333650,1464771,7130725,8204773,8139807,5227974,21687457,3629543,3352814,3048668,3098852,3089002,2741120,7276296,6228603,6371675,3410781,2561475,2214795,676638,2805867,3324785,2085296,2324807,2370901,2116821,4747341,5202423,4501588,3360712,4494075,12281338,6967281,2979162,3382723,3455662,2996063,3728870,5090470,3688535,4312309,3168202,4034094,3053390,10418288,2887191,2614025,8516635,5653922,4221633,4330255,5847940,5829627,6338504,3436423,5761506,4980339,4954403,6957185,3148859,3672602,4758082,6115616,3698381,3540428,4754710,3477704,1444666,1444957,984450,136823,57394,15273]



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
            # self.ground_truth = [78,117,110,108,100,124,109,108,87,116,86,124,8,4,110,75,13,4,116,112,115,98,13,112,91,116,108,95,125,96,54,13,106,107,121,96,101,107,110,112,148,143,195,141,14,44,14,41,30,29,121,119,123,102,106,114,106,83,112,105,110,87,118,106,115,109,110,95,109,112,122,108,111,116,24,9,125,108,47,15,104,89,109,99,108,91,124,59,96,87,31,33,19,97,118,131,140,157,159,182,192,257,292,340,391,500,598,581,272,227,400,624,678,685,717,665,493,718,729,751,92,0,116,104,109,121,105,96,449,791,693,878,969,924,905,760,738,510,22,301,30,67,31,13,39,85,98,125,303,358,14,2,0,61,60,96,111,89,212,276,333,317,335,360,387,410,411,432,439,505,550,571,637,642,602,686,500,549,634,772,887,462,64,501,618,594,657,727,789,656,769,840,765,680,637,637,692,711,705,826,761,637,621,616,554,668,765,704,568,661,575,645,719,692,785,714,701,663,569,548,624,634,658,589,666,325,62,0,31,111]
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
                        curr_buffer += CHUNK_LENGTH
                        
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
                    reward = (bitrate_sum/1000.) - (160*curr_rebuffer_time) - (smoothness_diffs/1000.)

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
        run(log_file_path=LOG_FILE + '_fastMPC_' + trace_file +'_2s', bw_file_path=LOG_BW + '_fastMPC_' + trace_file)
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
