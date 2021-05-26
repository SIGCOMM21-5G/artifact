/**
 * The copyright in this software is being made available under the BSD License,
 * included below. This software may be subject to other third party and contributor
 * rights, including patent rights, and no such rights are granted under this license.
 *
 * Copyright (c) 2013, Dash Industry Forum.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *  * Redistributions of source code must retain the above copyright notice, this
 *  list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright notice,
 *  this list of conditions and the following disclaimer in the documentation and/or
 *  other materials provided with the distribution.
 *  * Neither the name of Dash Industry Forum nor the names of its
 *  contributors may be used to endorse or promote products derived from this software
 *  without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND ANY
 *  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 *  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 *  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 *  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 *  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 *  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 *  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 *  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 */

import SwitchRequest from '../rules/SwitchRequest';
import BitrateInfo from '../vo/BitrateInfo';
import DOMStorage from '../utils/DOMStorage';
import ABRRulesCollection from '../rules/abr/ABRRulesCollection';
import MediaPlayerModel from '../models/MediaPlayerModel';
import FragmentModel from '../models/FragmentModel';
import EventBus from '../../core/EventBus';
import Events from '../../core/events/Events';
import FactoryMaker from '../../core/FactoryMaker';
import ManifestModel from '../models/ManifestModel';
import DashManifestModel from '../../dash/models/DashManifestModel';
import VideoModel from '../models/VideoModel';
import DashMetrics from '../../dash/DashMetrics';
import MetricsModel from '../models/MetricsModel';

const ABANDON_LOAD = 'abandonload';
const ALLOW_LOAD = 'allowload';
const DEFAULT_VIDEO_BITRATE = 1000;
const DEFAULT_AUDIO_BITRATE = 100;
const QUALITY_DEFAULT = 5;
//const dashMetrics = this.context.dashMetrics;
//const metricsModel = this.context.metricsModel;

function AbrController() {
    let context = this.context;
    let eventBus = EventBus(context).getInstance();
    let abrAlgo = -1;
    let bitrateArray = [2000,2000,2000,4000,8000,12000,16000,20000,20000];
    let reservoir = 5;
    let cushion = 10;
    let p_rb = 1;
    let pastThroughput = [];
    let pastDownloadTime = [];
    let bandwidthEstLog = [];
    let horizon = 5; // number of chunks considered
    let lastRequested = 0;
    let lastQuality = 1;
    let alpha = 12;
    let qualityLog = [];
    let switchUpCount = 0;
    let switchUpThreshold = [0,1,2,3,4,5,6,7,8,9];
    let p = 0.85;
    let lastIndex = -1;
    let instance,
        abrRulesCollection,
        rulesController,
        streamController,
        autoSwitchBitrate,
        topQualities,
        qualityDict,
        confidenceDict,
        bitrateDict,
        ratioDict,
        averageThroughputDict,
        streamProcessorDict,
        abandonmentStateDict,
        abandonmentTimeout,
        limitBitrateByPortal,
        usePixelRatioInLimitBitrateByPortal,
        manifestModel,
        dashManifestModel,
        videoModel,
        dashMetrics,
        metricsModel,
        mediaPlayerModel,
        domStorage;
    let truth_bw = [];
    let startup_time = 0;

    function setup() {
        autoSwitchBitrate = {video: true, audio: true};
        topQualities = {};
        qualityDict = {};
        confidenceDict = {};
        bitrateDict = {};
        ratioDict = {};
        averageThroughputDict = {};
        abandonmentStateDict = {};
        streamProcessorDict = {};
        limitBitrateByPortal = false;
        usePixelRatioInLimitBitrateByPortal = false;
        domStorage = DOMStorage(context).getInstance();
        mediaPlayerModel = MediaPlayerModel(context).getInstance();
        manifestModel = ManifestModel(context).getInstance();
        dashManifestModel = DashManifestModel(context).getInstance();
        videoModel = VideoModel(context).getInstance();
        dashMetrics = DashMetrics(context).getInstance();
        metricsModel = MetricsModel(context).getInstance();
    }

    function initialize(type, streamProcessor) {
        streamProcessorDict[type] = streamProcessor;
        abandonmentStateDict[type] = abandonmentStateDict[type] || {};
        abandonmentStateDict[type].state = ALLOW_LOAD;
        eventBus.on(Events.LOADING_PROGRESS, onFragmentLoadProgress, this);


    }

    // returns size of last chunk using HTTPRequest object (not hardcoded :))
    function last_chunk_size(lastreq) {
        var tot = 0;
        for ( var tt = 0; tt < lastreq.trace.length; tt++ ) {
            tot = tot + lastreq.trace[tt].b[0];
        }
        return tot;
    }

    function next_chunk_size(index, quality) {
        quality = 5;
        // Racecar video!
        // index is the index of the *next* chunk
        //var size_video1 = [1680951,1637558,1371111,1684293,1400042,1792609,1213669,1191552,1888982,1381292,1593129,1384566,1918298,1605664,1356382,1278860,1580165,1315506,1642869,928190,1416000,865548,1284104,1692271,1504744,1484004,1405086,891371,1401736,1743545,1084561,1099310,1789869,1675658,1636106,1492615,1200522,1787763,1690817,1459339,1250444,1691788,1403315,1732710,1270067,1514363,1615320,1507682,1260622,1784654,1352160,1115913,1637646,1546975,1637443,1475444,1616179,1113960,466635,1727956,1316739,1373312,458410,320487,573826],
        //size_video2 = [1184008,1123706,854424,1150093,902304,1237428,763515,840707,1279590,930828,996858,950867,1285933,1049248,984261,876058,1054391,875132,996451,660126,1032091,626844,949274,1197901,1001670,994288,925341,623084,977347,1184694,766276,834528,1285071,1017030,1080835,1078945,788728,1165402,1123991,937434,804808,1178153,922947,1175468,903392,970351,1094905,931644,854957,1179875,978233,794797,1073857,942081,1074761,1033448,1181202,660582,297985,1188866,910001,974311,314327,221329,445973],
        //size_video3 = [604139,577615,418531,555427,469238,614632,393715,428426,594788,527047,460827,500774,621760,556545,476734,417508,552639,462442,552256,303234,522859,337637,471941,598737,560588,487684,479873,284277,564825,546935,394056,442514,610493,523364,574457,499175,412705,586327,560284,476697,408166,570011,502061,569274,444948,507586,525450,541979,391886,539537,506089,408110,515570,462132,574826,523754,572621,344553,157240,610010,460871,480012,169331,126490,236234],
        //size_video4 = [361158,370284,246858,357922,264156,371586,241808,270621,327839,334864,313171,253682,348331,319047,311275,282933,308899,289234,307870,207573,354546,208087,305510,364291,331480,298846,298034,195290,327636,354076,261457,272419,344053,307537,344697,301834,261403,332467,324205,276260,260969,357539,301214,320538,292593,290952,325914,285965,266844,327707,308757,271734,313780,284833,295589,331270,307411,224531,94934,385537,306688,310705,95847,78651,162260],
        //size_video5 = [207189,219272,134208,204651,164461,230942,136746,150366,193697,193362,189146,153391,195591,177177,190923,155030,185660,164741,179442,131632,198676,115285,148044,181978,200708,177663,176815,109489,203211,196841,161524,151656,182521,172804,211407,171710,170866,178753,175461,184494,154382,206330,175870,178679,173567,172998,189473,172737,163181,181882,186151,164281,172026,173011,162488,201781,176856,137099,57015,234214,172494,184405,61936,43268,81580];

        // 9-bitrate weird video with 4 second chunks
        var size_video1 = [334214,13819603,14761600,6197322,3366934,2388527,1337181,1516777,6992542,4670402,6337067,8649687,7694430,3120599,3556672,3601736,851839,2048798,1615178,9221867,6925662,5107248,5983042,6550918,4560294,3477264,15119235,17086928,2904227,3080374,2614228,2603487,2273905,2324111,2496996,2137120,2822406,1877828,1744004,2701293,4035682,10249190,9313837,1800297,5247417,4369205,3027785,2714517,2495254,1418787,1759856,1443091,515178,399331,1932352,2200562,2200310,2935296,2075064,1560323,1977896,2214398,2505477,1867298,1899610,2084083,3787007,4443718,3767341,5237247,4789456,2917624,2665512,3167213,3283105,4040189,14818629,3813010,5525681,5078895,2459250,2396395,2808719,2602178,2784520,2793245,2478875,2396021,2431330,3736972,4912906,3141527,3324957,3135984,3830140,3685245,3779001,1670403,3634849,2456384,2136795,2675913,9755233,7989574,2865504,1701090,1504172,2532559,5162972,9188085,5260359,3555409,3807320,2940126,2555278,4652714,5117627,4422268,4808511,4659323,4883785,5364898,3179715,2576251,4933169,5031585,5003763,3391676,4764359,3572818,5185844,5345082,2349371,3045284,2926617,3144094,4112445,3587883,4373914,5060695,3681128,2585405,3169245,2543862,3843297,4131860,3152934,2833725,1229134,1414401,1084360,1619381,1331951,252398,167121,79905,34582,66408],
        size_video2 = [334476,11007815,8849724,3191121,1661718,1315024,698359,730082,4047415,2863079,4167844,5571764,4925652,2030157,2240782,2211169,382046,1113969,820127,6357933,4814284,3419258,3944328,4284196,3022025,2248581,9946363,11684632,1849732,1942795,1704756,1697111,1529441,1568649,1677618,1415096,1894067,1186604,1068386,1700843,2536859,4742872,4955535,1260540,3605246,2770338,1855168,1666915,1555467,1008919,1227619,1015853,384076,295687,1328674,1492829,1484812,1868314,1253406,887933,1153403,1249023,1423973,1060162,1080597,1156442,2222640,2587311,2178351,3121089,2857420,1702477,1531670,1863424,1987392,2505586,9620218,2561608,3633991,3324070,1560020,1429188,1754144,1626020,1739228,1722735,1538145,1473412,1498968,2247334,3156442,1895098,1939135,1842874,2235830,2202171,2242042,1081763,2409013,1615028,1413467,1632450,5664827,4578115,1783835,1093613,975642,1658005,3055257,5355572,3278424,2318501,2473561,1730311,1455812,2869222,3226650,2705936,2998622,2928342,3059979,3367422,1950694,1541020,2926720,2991202,3002106,2015412,2894863,2185316,3370605,3492243,1307592,1881404,1806471,1945842,2538877,2298557,2831497,3200905,2180586,1500505,1939246,1599193,2364826,2517454,1883143,1726706,707364,796460,596962,947625,832859,151562,90390,50278,26471,40620],
        size_video3 = [335737,11642034,9061343,2846282,1379579,1083781,533454,508812,2514829,1861181,2835412,4074608,3844696,1630440,1712120,1662097,243072,793783,531720,5045162,3858422,2713103,3070467,3391518,2424462,1798203,8032438,9808342,1491397,1560434,1396705,1392963,1276651,1314540,1407326,1196263,1627563,987649,864635,1366872,2025194,2595110,3209770,1080711,3005751,2251469,1498439,1329461,1254418,879546,1055149,883588,347560,267077,1128983,1257735,1265527,1524381,995715,674495,885875,928626,1062903,799389,812821,856497,1700457,1970588,1652704,2412882,2213643,1294662,1157734,1439296,1558739,1982918,7754684,2122146,2951725,2707022,1258293,1132545,1405832,1314152,1387998,1362449,1219048,1160520,1180684,1739841,2506643,1488968,1507223,1424538,1714252,1710495,1751030,875075,1998050,1336691,1179696,1291599,4082189,3284299,1412347,909953,808459,1370506,2325287,4018361,2566881,1890880,2005276,1359018,1134985,2294159,2601076,2155956,2411136,2355841,2451277,2690936,1552444,1207957,2277016,2335112,2348675,1575943,2268474,1727401,2744751,2853458,1012501,1508766,1446069,1560727,2029094,1857827,2294649,2580724,1699891,1171248,1549070,1299702,1877910,1991172,1469635,1366341,564365,622694,449729,748394,676139,123294,70186,50504,24518,36255],
        size_video4 = [334022,9869079,7078153,1798447,946554,768486,398693,358785,1838971,1382199,2052265,3005823,2879726,1267052,1316661,1263534,150125,555328,323573,4001900,3029729,2083035,2281353,2599148,1926191,1427209,6361262,7838407,1127469,1179779,1078151,1086181,1029204,1054251,1132419,977239,1356524,801103,686354,1097671,1598754,1172467,1818385,890138,2345010,1735323,1153767,1020736,965874,762421,883591,750345,317174,245047,926307,1028305,1059850,1192343,755853,481371,632141,627832,711870,555825,558836,579891,1196803,1363367,1137409,1719028,1582861,901281,798342,1031599,1153146,1472726,5789048,1677334,2233179,2053317,953056,835287,1072056,1005233,1040790,1009563,911305,852154,864029,1222697,1822246,1089714,1097827,1010680,1202900,1236644,1286142,675899,1606544,1066218,948747,970495,2424481,1902440,1031824,732536,645392,1104267,1592936,2618824,1820110,1448467,1521463,1006183,831839,1735764,1969173,1618621,1825708,1780068,1844656,2010421,1158554,873968,1651288,1697771,1712532,1149171,1666069,1269548,2108361,2206878,752992,1143645,1081066,1175321,1515596,1397801,1735873,1955680,1256122,872352,1175796,1004408,1393009,1466703,1060685,1011581,422329,458857,318722,566180,531853,95334,52187,32002,22693,26015],
        size_video5 = [334032,6594552,4402139,1043358,567502,472646,274373,222226,1213073,927735,1463326,2054811,1928241,898461,929156,886614,90752,376357,197626,2995445,2226527,1501029,1558531,1856343,1433055,1055512,4647286,5615227,764013,795179,741228,760332,769288,779865,838056,709811,997014,576726,481423,753582,1035369,420196,876880,659947,1538893,1116845,770196,678418,663968,596131,642153,561624,252381,198847,672121,755974,808254,848961,531866,318027,411948,387504,434147,349710,349575,360691,767399,838282,690145,1110276,1024586,566069,498552,676507,770118,962786,3596154,1238543,1526348,1410236,659155,563159,756304,730895,731159,678447,621176,556204,568078,747231,1138250,724195,728813,631476,728502,819353,864484,496044,1258285,818447,743969,689321,1121938,667445,682795,564053,493680,823677,878603,1192759,1046702,982243,1004344,687087,564465,1193260,1350143,1085010,1231535,1204741,1227805,1328172,755940,542221,1043429,1080376,1087843,735758,1086740,818102,1450968,1535058,516135,781150,723162,787496,1008090,920901,1141486,1305395,854393,602217,819411,705221,905448,951381,663404,662118,284661,305283,197766,385891,375542,71077,37732,26108,20475,22446],
        size_video6 = [60629,1072422,1121405,728514,508013,395538,297276,247728,1172629,740561,905521,975494,873443,420093,432386,430845,114664,272444,180836,1138797,922146,760526,866360,821406,576666,399536,2503359,2158640,352618,355918,335697,336592,257949,254944,280530,274347,407719,221839,208863,331412,560025,480043,639392,307952,852435,548688,370252,330522,298688,200752,280436,254413,92084,85090,285433,361866,347546,396965,264442,201160,227906,301480,401522,296659,306130,320231,505705,560900,477844,593358,552627,356467,298528,372582,432861,576027,2234357,560537,577595,643057,299663,284317,341921,337442,361712,356599,349268,330614,348018,462525,845902,452278,403995,391858,447328,442130,467709,242111,564856,387198,371539,364606,883642,678863,376102,268819,249895,388840,510672,813914,569070,587015,600946,296369,286854,566404,695021,594594,629131,474066,623944,654640,416970,336627,598150,590759,584579,441665,567172,503622,629808,657376,207349,432669,432968,461467,530571,602139,716984,719449,335356,213548,339747,339538,477871,491670,462611,415951,156751,181344,138957,198063,181915,46143,32698,12091,9218,10349],
        size_video7 = [28717,460475,550011,401179,293086,214799,175377,126522,626817,406114,441827,462042,399182,223999,253238,232808,53518,132258,92415,561148,471077,384976,400244,397638,293991,211138,1087425,857095,184468,183961,176954,182889,140413,144943,154268,158694,228494,126130,118843,188016,304948,170066,272575,186904,456927,280891,191747,173510,154053,110074,160637,149779,56754,53519,169833,215358,206134,217891,140910,102461,116607,155212,217018,183768,180999,190757,256572,266457,226765,291626,266212,180131,150082,194148,217851,280960,858567,332031,305540,333656,160196,147947,181748,182744,193051,187271,187611,178722,181938,234596,434199,233056,211986,206031,231293,230178,244545,129141,292677,214984,207438,191321,349717,238341,166138,143551,134758,234393,235703,350754,274054,331523,335983,155670,149398,300323,381707,307893,330196,246363,318766,331330,222025,172849,283772,295812,292595,237899,278978,251210,331975,336166,103282,226221,231602,243196,276595,319717,362132,341295,160167,109795,177029,179671,243891,253748,245996,221647,79754,89303,74829,98095,96538,25513,16279,7912,5970,7621],
        size_video8 = [28717,460475,550011,401179,293086,214799,175377,126522,626817,406114,441827,462042,399182,223999,253238,232808,53518,132258,92415,561148,471077,384976,400244,397638,293991,211138,1087425,857095,184468,183961,176954,182889,140413,144943,154268,158694,228494,126130,118843,188016,304948,170066,272575,186904,456927,280891,191747,173510,154053,110074,160637,149779,56754,53519,169833,215358,206134,217891,140910,102461,116607,155212,217018,183768,180999,190757,256572,266457,226765,291626,266212,180131,150082,194148,217851,280960,858567,332031,305540,333656,160196,147947,181748,182744,193051,187271,187611,178722,181938,234596,434199,233056,211986,206031,231293,230178,244545,129141,292677,214984,207438,191321,349717,238341,166138,143551,134758,234393,235703,350754,274054,331523,335983,155670,149398,300323,381707,307893,330196,246363,318766,331330,222025,172849,283772,295812,292595,237899,278978,251210,331975,336166,103282,226221,231602,243196,276595,319717,362132,341295,160167,109795,177029,179671,243891,253748,245996,221647,79754,89303,74829,98095,96538,25513,16279,7912,5970,7621],
        size_video9 = [28717,460475,550011,401179,293086,214799,175377,126522,626817,406114,441827,462042,399182,223999,253238,232808,53518,132258,92415,561148,471077,384976,400244,397638,293991,211138,1087425,857095,184468,183961,176954,182889,140413,144943,154268,158694,228494,126130,118843,188016,304948,170066,272575,186904,456927,280891,191747,173510,154053,110074,160637,149779,56754,53519,169833,215358,206134,217891,140910,102461,116607,155212,217018,183768,180999,190757,256572,266457,226765,291626,266212,180131,150082,194148,217851,280960,858567,332031,305540,333656,160196,147947,181748,182744,193051,187271,187611,178722,181938,234596,434199,233056,211986,206031,231293,230178,244545,129141,292677,214984,207438,191321,349717,238341,166138,143551,134758,234393,235703,350754,274054,331523,335983,155670,149398,300323,381707,307893,330196,246363,318766,331330,222025,172849,283772,295812,292595,237899,278978,251210,331975,336166,103282,226221,231602,243196,276595,319717,362132,341295,160167,109795,177029,179671,243891,253748,245996,221647,79754,89303,74829,98095,96538,25513,16279,7912,5970,7621];

        // 9-bitrate wierd video with 2 second chunks
        //var size_video1 = [1535564, 1620285, 1269756, 1371500, 1299593, 1110665, 1537560, 1419367, 1443640, 1150344, 1048950, 1338900, 1251304, 1303358, 1481963, 1482209, 1279246, 1261881, 1294098, 1259269, 1288054, 1353055, 1551507, 1325069, 1198053, 1295347, 1521939, 1350854, 1336747, 968044, 1440635, 1415247, 1160228, 1727664, 1187073, 1287849, 1415619, 1413330, 1002890, 1507766, 1242136, 1302168, 1388401, 1251722, 1416202, 1321234, 1178151, 1381047, 1483665, 1144404, 1306854, 1319882, 1589851, 1219615, 1039973, 1294102, 1508564, 1266796, 1594067, 1316179, 1300219, 1186007, 1375130, 1346691, 1162886, 1318148, 1369247, 1680134, 1305914, 1283088, 1324467, 1227251, 1218548, 1177530, 1317341, 1551747, 1138380, 1451108, 1452943, 1143820, 1205956, 1256526, 1423203, 1332599, 1379156, 1294023, 1575368, 1270880, 1324969, 1319305, 1266576, 1493740, 1211363, 1099485, 1352346, 1294667, 826712],
        //    size_video2 = [1145867, 1208905, 931675, 1191390, 1057080, 1119993, 1026761, 1134116, 1245559, 987497, 866042, 1075583, 1028110, 1129425, 1200782, 1089390, 988925, 1066544, 1106191, 1063010, 1110709, 1062813, 1023521, 1078931, 1013406, 1196057, 1208483, 1066893, 1053130, 952269, 1089380, 1063103, 1015405, 1274284, 960433, 1099079, 1120348, 1100378, 962301, 1194428, 1021594, 1018179, 1128044, 1048425, 1172522, 1048984, 937673, 1106402, 1230806, 955984, 1014536, 1090695, 1259901, 1135687, 796181, 1175867, 1018254, 1116360, 1118076, 1046064, 1047156, 1066037, 1087601, 1060251, 1093037, 1098037, 1065720, 1221041, 1172284, 1135503, 1111459, 1032489, 929057, 990724, 968221, 1179246, 984872, 1148998, 1126258, 1019862, 1045316, 1063175, 1086668, 1097903, 1075409, 1046519, 1172168, 1046934, 1041771, 1083179, 1039387, 1207119, 981184, 979956, 1074550, 1080462, 716829],
        //    size_video3 = [838177, 890702, 651428, 780381, 655721, 645147, 795676, 724605, 865600, 606958, 541774, 682486, 694157, 694246, 802642, 836127, 667592, 680419, 724714, 705051, 633275, 721273, 837102, 682849, 695459, 727460, 825782, 752561, 673680, 557765, 678997, 792068, 655603, 836023, 674271, 684530, 776218, 760938, 566838, 769212, 734163, 680953, 796704, 671422, 791202, 714558, 595055, 728935, 733271, 650464, 718126, 762338, 850550, 697022, 499827, 642144, 742392, 756078, 818999, 742264, 660056, 681145, 709784, 787899, 656266, 701815, 773105, 814188, 796431, 696241, 728458, 711438, 549722, 589569, 662264, 836745, 642226, 785252, 792766, 609521, 649530, 689970, 743514, 783785, 671295, 671707, 923362, 663888, 738933, 725988, 658877, 824650, 663951, 567505, 642371, 722166, 444706],
        //    size_video4 = [495048, 539060, 437741, 519944, 415491, 462280, 484055, 449221, 574817, 421932, 372339, 428719, 439072, 466443, 534691, 525796, 441111, 411722, 456147, 457741, 462377, 477442, 467687, 449741, 457375, 489476, 521611, 514843, 463299, 358332, 457104, 466066, 433614, 533085, 405177, 480537, 514593, 473115, 371722, 552033, 451259, 440345, 494837, 460394, 511811, 456215, 428734, 445441, 470212, 427764, 444101, 461834, 565945, 510654, 341943, 416254, 495342, 477456, 490721, 485090, 459017, 414412, 459491, 494962, 428526, 456536, 477188, 558141, 530351, 495705, 475834, 468108, 353512, 375450, 431352, 507235, 415898, 492767, 506488, 424089, 452910, 405540, 512319, 512686, 431588, 454667, 547853, 426119, 496972, 462022, 447379, 534685, 450418, 380312, 384989, 461381, 299425],
        //    size_video5 = [327613, 340673, 276919, 334168, 288757, 282294, 302840, 314841, 377182, 275692, 235035, 285280, 284149, 277642, 363649, 345885, 297290, 287556, 265573, 295248, 296546, 310864, 311963, 282115, 302189, 322093, 356218, 331153, 298737, 228213, 276952, 310924, 277828, 339414, 272818, 308675, 338685, 300519, 249937, 336902, 296437, 305301, 324368, 291838, 337157, 319314, 262029, 274638, 312753, 274483, 290243, 300092, 374242, 322134, 228278, 258882, 321476, 301420, 332540, 308907, 300873, 269519, 307698, 312585, 282432, 301917, 319380, 350749, 368023, 322230, 309314, 289413, 239148, 248664, 259764, 315827, 274832, 331052, 325385, 262121, 301419, 265485, 330862, 310590, 303327, 296150, 359626, 275235, 329656, 300547, 295821, 342840, 294842, 243770, 250973, 299933, 195725],
        //    size_video6 = [218953, 231330, 189055, 209810, 173551, 177261, 192106, 190249, 244719, 166842, 144451, 174113, 155385, 197257, 214125, 223037, 188432, 186326, 173759, 189036, 164860, 188360, 216458, 188676, 193547, 192804, 218223, 216186, 190601, 146458, 175934, 190280, 178660, 182171, 178984, 193979, 211644, 193952, 149419, 201294, 198269, 188203, 215218, 184676, 205911, 195942, 165344, 178456, 183414, 176489, 183089, 196611, 226486, 199295, 146202, 131514, 198153, 202243, 202296, 198212, 201625, 156593, 193435, 206887, 173993, 195841, 202095, 210742, 229255, 171833, 210226, 154935, 165847, 155217, 151742, 209823, 182646, 195681, 220617, 170063, 155313, 190203, 183299, 201206, 186793, 185300, 254643, 183638, 205106, 193881, 180990, 212814, 177217, 153836, 136731, 177376, 127977],
        //    size_video7 = [141282, 155827, 125040, 132607, 112034, 114896, 128783, 123227, 153185, 98829, 91248, 113559, 99498, 123232, 144645, 147821, 130594, 120658, 108676, 116393, 99197, 120017, 147651, 116841, 123631, 126590, 142765, 139888, 108656, 94771, 113881, 127315, 115095, 117183, 116064, 120714, 133999, 123482, 100333, 138757, 127851, 122093, 136872, 115124, 135495, 119260, 98662, 116296, 127350, 109471, 120123, 127296, 149628, 123861, 86384, 83717, 124461, 134057, 132811, 124026, 129450, 116099, 124053, 130463, 106432, 121818, 128740, 136393, 146766, 119155, 116658, 111724, 106768, 100540, 99244, 131075, 110452, 120822, 141803, 115278, 103398, 107080, 118718, 128730, 121092, 117544, 170763, 120712, 135391, 121879, 121149, 138163, 115203, 103073, 84570, 107278, 72118],
        //    size_video8 = [87486, 94315, 72359, 83221, 69454, 70403, 80447, 74985, 93429, 70013, 57408, 68881, 68664, 84631, 85468, 88381, 77573, 73137, 66739, 72366, 65243, 76597, 85767, 70381, 77722, 83024, 92471, 87330, 81250, 58801, 65418, 72895, 72592, 70917, 73337, 77279, 87034, 78350, 62807, 78074, 78628, 79043, 82951, 74861, 85635, 78292, 66474, 71180, 73720, 73034, 74564, 79374, 95994, 85907, 57365, 53790, 75974, 77631, 72618, 76411, 84619, 72802, 76840, 80648, 68498, 75383, 77996, 85448, 90638, 88690, 85088, 74826, 63965, 67645, 51279, 72732, 70543, 73711, 83697, 66294, 74364, 73604, 78605, 83252, 71766, 73444, 100122, 72190, 85506, 81519, 77235, 82829, 73288, 64219, 52565, 65856, 56135],
        //    size_video9 = [59721, 74169, 55032, 56752, 47530, 48364, 52820, 49355, 64369, 36633, 43649, 48694, 42830, 45718, 63990, 62758, 50828, 51562, 46648, 48850, 44969, 49044, 60496, 50175, 53080, 52660, 56317, 52637, 49375, 42919, 50742, 53291, 45243, 50672, 52599, 49961, 55560, 51362, 40881, 50600, 55679, 55011, 53260, 48729, 51771, 52515, 44112, 50897, 53045, 46375, 53733, 50278, 61823, 44786, 36547, 39424, 52936, 59631, 51464, 52019, 57212, 48904, 49561, 51894, 46883, 51827, 52188, 55886, 55434, 53024, 41482, 52031, 47934, 47183, 44698, 51038, 47461, 51041, 57897, 43518, 43460, 43535, 45080, 56131, 49937, 49600, 77138, 51357, 54264, 51314, 51060, 58447, 44994, 38175, 46089, 49101, 28312];


        // upper number is 96 if 2 second chunks for weird video
        // if 4 second chunks, make that number 48
        // 64 for old video (racecar)
        if (index < 0 || index > 157) {
            return 0;
        }
        var chunkSize = [size_video1[index], size_video2[index], size_video3[index], size_video4[index], size_video5[index], size_video6[index], size_video7[index], size_video8[index], size_video9[index]];
        //switch (quality) {
        //    case 4:
        //        chunkSize = size_video1[index];
        //        break;
        //    case 3:
        //        chunkSize = size_video2[index];
        //        break;
        //    case 2:
        //        chunkSize = size_video3[index];
        //        break;
        //    case 1:
        //        chunkSize = size_video4[index];
        //        break;
        //    case 0:
        //        chunkSize = size_video5[index];
        //        break;
        //    default:
        //        chunkSize = 0;
        //        break;
        //}
        return chunkSize;
    }

    function getStabilityScore(b, b_ref, b_cur) {
        var score = 0,
        n = 0;
        if (lastIndex >= 1) {
            for (var i = Math.max(0, lastIndex + 1 - horizon); i<= lastIndex - 1; i++) {
            if (qualityLog[i] != qualityLog[i+1]) {
                n = n + 1;
            }
            }
        }
        if (b != b_cur) {
            n = n + 1;
        }
        score = Math.pow(2,n);
        return score;
    }

    function getEfficiencyScore(b, b_ref, w, bitrateArray) {
        var score = 0;
        score = Math.abs( bitrateArray[b]/Math.min(w, bitrateArray[b_ref]) - 1 );
        return score;
    }

    function getCombinedScore(b, b_ref, b_cur, w, bitrateArray) {
        var stabilityScore = 0,
        efficiencyScore = 0,
        totalScore = 0;
        // compute
        stabilityScore = getStabilityScore(b, b_ref, b_cur);
        efficiencyScore = getEfficiencyScore(b, b_ref, w, bitrateArray);
        totalScore = stabilityScore + alpha*efficiencyScore;
        return totalScore;  
    }

    function getBitrateFestive(prevQuality, bufferLevel, bwPrediction, lastRequested, bitrateArray) {
        // var self = this, 
        var bitrate = 0,
        tmpBitrate = 0,
        b_target = 0,
        b_ref = 0,
        b_cur = prevQuality + 2,
        score_cur = 0,
        score_ref = 0;
        // TODO: implement FESTIVE logic
        // 1. log previous quality
        qualityLog[lastRequested] = prevQuality;
        lastIndex = lastRequested;
        // 2. compute b_target
        tmpBitrate = p*bwPrediction;
        console.log("zry: bitrate prev " + prevQuality); // check this line about prevQuality
        console.log("zry: tmpBitrate " + tmpBitrate); //30000
        for (var i = 7; i>=2; i--) { // todo: use bitrateArray.length
            if (bitrateArray[i] <= tmpBitrate) {
                b_target = i;
                break;
            }
            b_target = i;
        }
        console.log("zry: b_target " + b_target); //30000
        // 3. compute b_ref
        if (b_target > b_cur) {
            switchUpCount = switchUpCount + 1;
            console.log("zry: switchUpCount " + switchUpCount); 
            if (switchUpCount > switchUpThreshold[b_cur]) {
            b_ref = b_cur + 1;
            } else {
            b_ref = b_cur;
            }
        } else if (b_target < b_cur) {
            b_ref = b_cur - 1;
            switchUpCount = 0;
        } else {
            b_ref = b_cur;
            switchUpCount = 0; // this means need k consecutive "up" to actually switch up
        }
        console.log("zry: b_ref " + b_ref); 
        console.log("zry: b_cur " + b_cur); 

        // 4. delayed update
        if (b_ref != b_cur) { // need to switch
            // compute scores
            score_cur = getCombinedScore(b_cur, b_ref, b_cur, bwPrediction, bitrateArray);
            score_ref = getCombinedScore(b_ref, b_ref, b_cur, bwPrediction, bitrateArray);
            console.log("zry: score_cur " + score_cur); 
            console.log("zry: score_ref " + score_ref); 
            if ((score_cur <= score_ref) && score_cur != 1) {
                bitrate = b_cur;
            } else {
                bitrate = b_ref;
                if (bitrate > b_cur) { // clear switchupcount
                    switchUpCount = 0;
                }
            }
        } else {
            bitrate = b_cur;
        }
        // 5. return
        console.log("zry: bitrate " + bitrate); 
        if (bitrate > 2) {
            bitrate -= 2;
        }
        return bitrate;
    }

    function predict_throughput(lastRequested, lastQuality, lastHTTPRequest) {
        // var self = this,
        var bandwidthEst = 0,
        lastDownloadTime,
        lastThroughput,
        lastChunkSize,
        tmpIndex,
        tmpSum = 0,
        tmpDownloadTime = 0;
        // First, log last download time and throughput
        if (lastHTTPRequest && lastRequested >= 0) {
            lastDownloadTime = (lastHTTPRequest._tfinish.getTime() - lastHTTPRequest.tresponse.getTime()) / 1000; //seconds
            if (lastDownloadTime <0.1) {
                lastDownloadTime = 0.1;
            }
            lastChunkSize = last_chunk_size(lastHTTPRequest);
            //lastChunkSize = self.vbr.getChunkSize(lastRequested, lastQuality);
            lastThroughput = lastChunkSize*8/lastDownloadTime/1000;
            // Log last chunk
            pastThroughput[lastRequested] = lastThroughput;
            pastDownloadTime[lastRequested] = lastDownloadTime;
        }
        // Next, predict future bandwidth
        if (pastThroughput.length === 0) {
            return 0;
        } else {
            tmpIndex = Math.max(0, lastRequested + 1 - horizon);
            tmpSum = 0;
            tmpDownloadTime = 0;
            for (var i = tmpIndex; i<= lastRequested; i++) {
                tmpSum = tmpSum + pastDownloadTime[i]/pastThroughput[i];
                tmpDownloadTime = tmpDownloadTime + pastDownloadTime[i];
            }
            bandwidthEst = tmpDownloadTime/tmpSum;
            bandwidthEst = 1/tmpSum;
            bandwidthEstLog[lastRequested] = bandwidthEst;
            return bandwidthEst;
        }   
    }

    function setConfig(config) {
        if (!config) return;

        if (config.abrRulesCollection) {
            abrRulesCollection = config.abrRulesCollection;
        }
        if (config.rulesController) {
            rulesController = config.rulesController;
        }
        if (config.streamController) {
            streamController = config.streamController;
        }
    }

    function getBitrateBB(bLevel) {
        // var self = this,
        var tmpBitrate = 0,
        tmpQuality = 0;
        if (bLevel <= reservoir) {
            tmpBitrate = bitrateArray[0];
        } else if (bLevel > reservoir + cushion) {
            tmpBitrate = bitrateArray[8];
        } else {
            tmpBitrate = bitrateArray[0] + (bitrateArray[8] - bitrateArray[0])*(bLevel - reservoir)/cushion;
        }
        
        // findout matching quality level
        for (var i = 7; i>=2; i--) {
            if (tmpBitrate >= bitrateArray[i]) {
                tmpQuality = i;
                break;
            }
            tmpQuality = i;
        }
        //return 9;
        return tmpQuality - 2;
        // return 0;
    }

    function getBitrateRB(bandwidth) {
        // var self = this,
        var tmpBitrate = 0,
        tmpQuality = 0;
        
        tmpBitrate = bandwidth*p_rb;
        
        // findout matching quality level
        for (var i = 7; i>=2; i--) {
            if (tmpBitrate >= bitrateArray[i]) {
                tmpQuality = i;
                break;
            }
            tmpQuality = i;
        }
        return tmpQuality - 2;  
        // return 0;
    }

    function getTopQualityIndexFor(type, id) {
        var idx;
        topQualities[id] = topQualities[id] || {};

        if (!topQualities[id].hasOwnProperty(type)) {
            topQualities[id][type] = 0;
        }

        idx = checkMaxBitrate(topQualities[id][type], type);
        idx = checkMaxRepresentationRatio(idx, type, topQualities[id][type]);
        idx = checkPortalSize(idx, type);
        return idx;
    }

    /**
     * @param {string} type
     * @returns {number} A value of the initial bitrate, kbps
     * @memberof AbrController#
     */
    function getInitialBitrateFor(type) {

        let savedBitrate = domStorage.getSavedBitrateSettings(type);

        if (!bitrateDict.hasOwnProperty(type)) {
            if (ratioDict.hasOwnProperty(type)) {
                let manifest = manifestModel.getValue();
                let representation = dashManifestModel.getAdaptationForType(manifest, 0, type).Representation;

                if (Array.isArray(representation)) {
                    let repIdx = Math.max(Math.round(representation.length * ratioDict[type]) - 1, 0);
                    bitrateDict[type] = representation[repIdx].bandwidth;
                } else {
                    bitrateDict[type] = 0;
                }
            } else if (!isNaN(savedBitrate)) {
                bitrateDict[type] = savedBitrate;
            } else {
                bitrateDict[type] = (type === 'video') ? DEFAULT_VIDEO_BITRATE : DEFAULT_AUDIO_BITRATE;
            }
        }

        return bitrateDict[type];
    }

    /**
     * @param {string} type
     * @param {number} value A value of the initial bitrate, kbps
     * @memberof AbrController#
     */
    function setInitialBitrateFor(type, value) {
        bitrateDict[type] = value;
    }

    function getInitialRepresentationRatioFor(type) {
        if (!ratioDict.hasOwnProperty(type)) {
            return null;
        }

        return ratioDict[type];
    }

    function setInitialRepresentationRatioFor(type, value) {
        ratioDict[type] = value;
    }

    function getMaxAllowedBitrateFor(type) {
        if (bitrateDict.hasOwnProperty('max') && bitrateDict.max.hasOwnProperty(type)) {
            return bitrateDict.max[type];
        }
        return NaN;
    }

    // TODO  change bitrateDict structure to hold one object for video and audio with initial and max values internal.
    // This means you need to update all the logic around initial bitrate DOMStorage, RebController etc...
    function setMaxAllowedBitrateFor(type, value) {
        bitrateDict.max = bitrateDict.max || {};
        bitrateDict.max[type] = value;
    }

    function getMaxAllowedRepresentationRatioFor(type) {
        if (ratioDict.hasOwnProperty('max') && ratioDict.max.hasOwnProperty(type)) {
            return ratioDict.max[type];
        }
        return 1;
    }

    function setMaxAllowedRepresentationRatioFor(type, value) {
        ratioDict.max = ratioDict.max || {};
        ratioDict.max[type] = value;
    }

    function getAutoSwitchBitrateFor(type) {
        return autoSwitchBitrate[type];
    }

    function setAutoSwitchBitrateFor(type, value) {
        autoSwitchBitrate[type] = value;
    }

    function getLimitBitrateByPortal() {
        return limitBitrateByPortal;
    }

    function setLimitBitrateByPortal(value) {
        limitBitrateByPortal = value;
    }

    function getUsePixelRatioInLimitBitrateByPortal() {
        return usePixelRatioInLimitBitrateByPortal;
    }

    function setUsePixelRatioInLimitBitrateByPortal(value) {
        usePixelRatioInLimitBitrateByPortal = value;
    }

    function nextChunkQuality(buffer, lastRequested, lastQuality, rebuffer) {
        const metrics = metricsModel.getReadOnlyMetricsFor('video');
        //console.log("ORIG THROUGH: " + getAverageThroughput("video"));
        //var lastHTTPRequest = dashMetrics.getHttpRequests(metricsModel.getReadOnlyMetricsFor('video'))[lastRequested];
        var lastHTTPRequest = dashMetrics.getCurrentHttpRequest(metrics);
        var bandwidthEst = predict_throughput(lastRequested, lastQuality, lastHTTPRequest);
        var xhr, data, bufferLevelAdjusted;
        switch(abrAlgo) {
            case 2:
                xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:8333", false);
                xhr.onreadystatechange = function() {
                    if ( xhr.readyState == 4 && xhr.status == 200 ) {
                        console.log("GOT RESPONSE:" + xhr.responseText + "---");
                        if ( xhr.responseText == "REFRESH" ) {
                            document.location.reload(true);
                        }
                    }
                };
                data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'Type': 'BB', 'lastquality': lastQuality, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                xhr.send(JSON.stringify(data));
                console.log("Algorithm: Buffer based!!!");
                return getBitrateBB(buffer);
            case 3:
                xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:8333", false);
                xhr.onreadystatechange = function() {
                    if ( xhr.readyState == 4 && xhr.status == 200 ) {
                        console.log("GOT RESPONSE:" + xhr.responseText + "---");
                        if ( xhr.responseText == "REFRESH" ) {
                            document.location.reload(true);
                        }
                    }
                };
                data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'Type': 'RB', 'lastquality': lastQuality, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                xhr.send(JSON.stringify(data));
                console.log("Algorithm: Rate based!!!");
                return getBitrateRB(bandwidthEst);
            case 4:
                var quality = 2;
                xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:8333", false);
                xhr.onreadystatechange = function() {
                    if ( xhr.readyState == 4 && xhr.status == 200 ) {
                        console.log("GOT RESPONSE:" + xhr.responseText + "---");
                        if ( xhr.responseText != "REFRESH" ) {
                            quality = parseInt(xhr.responseText, 10);
                        } else {
                            document.location.reload(true);
                        }
                    }
                };
                bufferLevelAdjusted = buffer-0.15-0.4-4;
                data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'lastquality': lastQuality, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                xhr.send(JSON.stringify(data));
                console.log("QUALITY RETURNED IS: " + quality);
                return quality;
            case 5:
                xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:8333", false);
                xhr.onreadystatechange = function() {
                    if ( xhr.readyState == 4 && xhr.status == 200 ) {
                        console.log("GOT RESPONSE:" + xhr.responseText + "---");
                        if ( xhr.responseText == "REFRESH" ) {
                            document.location.reload(true);
                        }
                    }
                };
                data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'Type': 'Festive', 'lastquality': lastQuality, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                xhr.send(JSON.stringify(data));
                bufferLevelAdjusted = buffer-0.15-0.4-4;
                console.log("Using FESTIVE now !!!");
                return getBitrateFestive(lastQuality, bufferLevelAdjusted, bandwidthEst, lastRequested, bitrateArray);
            case 6:
                xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:8333", false);
                xhr.onreadystatechange = function() {
                    if ( xhr.readyState == 4 && xhr.status == 200 ) {
                        console.log("GOT RESPONSE:" + xhr.responseText + "---");
                        if ( xhr.responseText == "REFRESH" ) {
                            document.location.reload(true);
                        }
                    }
                };
                data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'Type': 'Bola', 'lastquality': lastQuality, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                xhr.send(JSON.stringify(data));
                console.log("Algorithm: BOLA!!!");
                return -1;
            case 7:
                // ground truth rate based
                var curr_time = Date.now() / 1000;
                var curr_idx = Math.floor(curr_time-startup_time);
                var bw_truth = 0;
                // TODO: how much bw should we take
                if (curr_idx + 1 > truth_bw.length) {
                    bw_truth = truth_bw[truth_bw.length-1];
                } else {
                    bw_truth = (truth_bw[curr_idx] + truth_bw[curr_idx+1])/2;
                }
                xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:8333", false);
                xhr.onreadystatechange = function() {
                    if ( xhr.readyState == 4 && xhr.status == 200 ) {
                        console.log("GOT RESPONSE:" + xhr.responseText + "---");
                        if ( xhr.responseText == "REFRESH" ) {
                            document.location.reload(true);
                        }
                    }
                };
                data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'Type': 'RB_Truth', 'lastquality': lastQuality, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                xhr.send(JSON.stringify(data));
                console.log("Algorithm: Rate based ground truth!!!");
                return getBitrateRB(bw_truth);
            default:
                // defaults to lowest quality always
                xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:8333", false);
                xhr.onreadystatechange = function() {
                    if ( xhr.readyState == 4 && xhr.status == 200 ) {
                        console.log("GOT RESPONSE:" + xhr.responseText + "---");
                        if ( xhr.responseText == "REFRESH" ) {
                            document.location.reload(true);
                        }
                    }
                };
                data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'Type': 'Fixed Quality (0)', 'lastquality': 0, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                xhr.send(JSON.stringify(data));
                return 0;
        }
    }

    function getPlaybackQuality(streamProcessor, completedCallback, buffer=0, rebuffer=0) {
        const type = streamProcessor.getType();
        const streamInfo = streamProcessor.getStreamInfo();
        const streamId = streamInfo.id;

        const callback = function (res) {

            const topQualityIdx = getTopQualityIndexFor(type, streamId);

            let newQuality = res.value;
            if (newQuality < 0) {
                newQuality = 0;
            }
            if (newQuality > topQualityIdx) {
                newQuality = topQualityIdx;
            }

            const oldQuality = getQualityFor(type, streamInfo);
            if (newQuality !== oldQuality && (abandonmentStateDict[type].state === ALLOW_LOAD || newQuality > oldQuality)) {
                setConfidenceFor(type, streamId, res.confidence);
                changeQuality(type, streamInfo, oldQuality, newQuality, res.reason);
            }
            if (completedCallback) {
                completedCallback();
            }
        };

        console.log("ABR enabled? (" + autoSwitchBitrate + ")");
        if (!getAutoSwitchBitrateFor(type)) {
            if (completedCallback) {
                completedCallback();
            }
        } else {
            const rules = abrRulesCollection.getRules(ABRRulesCollection.QUALITY_SWITCH_RULES);
            rulesController.applyRules(rules, streamProcessor, callback, getQualityFor(type, streamInfo), function (currentValue, newValue) {
                currentValue = currentValue === SwitchRequest.NO_CHANGE ? 0 : currentValue;
                if ( abrAlgo === 0 ) { // use the default return value
                    const metrics = metricsModel.getReadOnlyMetricsFor('video');
                    var lastHTTPRequest = dashMetrics.getCurrentHttpRequest(metrics);
                    var bandwidthEst = predict_throughput(lastRequested, lastQuality, lastHTTPRequest);
                    // defaults to lowest quality always
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", "http://localhost:8333", false);
                    xhr.onreadystatechange = function() {
                        if ( xhr.readyState == 4 && xhr.status == 200 ) {
                            console.log("GOT RESPONSE:" + xhr.responseText + "---");
                            if ( xhr.responseText == "REFRESH" ) {
                                document.location.reload(true);
                            }
                        }
                    };
                    var bufferLevelAdjusted = buffer-0.15-0.4-4;
                    var data = {'nextChunkSize': next_chunk_size(lastRequested+1), 'Type': 'Default', 'lastquality': 0, 'buffer': buffer, 'bufferAdjusted': bufferLevelAdjusted, 'bandwidthEst': bandwidthEst, 'lastRequest': lastRequested, 'RebufferTime': rebuffer, 'lastChunkFinishTime': lastHTTPRequest._tfinish.getTime(), 'lastChunkStartTime': lastHTTPRequest.tresponse.getTime(), 'lastChunkSize': last_chunk_size(lastHTTPRequest)};
                    xhr.send(JSON.stringify(data));
                    return Math.max(currentValue, newValue);
                }
                lastQuality = nextChunkQuality(buffer, lastRequested, lastQuality, rebuffer);
                lastRequested = lastRequested + 1;
                if ( abrAlgo == 6 ) {
                    lastQuality = Math.max(currentValue, newValue);
                    return Math.max(currentValue, newValue);
                }
                newValue = lastQuality;
                return lastQuality;
            });
        }
    }

    function setAbrAlgorithm(algo) {
        abrAlgo = algo;
        console.log("set abr algorithm to " + algo);
    }

    function setTruthBandwidth(bw_array) {
        truth_bw = bw_array;
        console.log("set bw truth to " + truth_bw);
    }

    function setStartTime(start_time) {
        startup_time = start_time;
        console.log("set startup time to " + startup_time);
    }

    function setPlaybackQuality(type, streamInfo, newQuality, reason) {
        const id = streamInfo.id;
        const oldQuality = getQualityFor(type, streamInfo);
        const isInt = newQuality !== null && !isNaN(newQuality) && (newQuality % 1 === 0);

        if (!isInt) throw new Error('argument is not an integer');

        if (newQuality !== oldQuality && newQuality >= 0 && newQuality <= getTopQualityIndexFor(type, id)) {
            changeQuality(type, streamInfo, oldQuality, newQuality, reason);
        }
    }

    function changeQuality(type, streamInfo, oldQuality, newQuality, reason) {
        setQualityFor(type, streamInfo.id, newQuality);
        eventBus.trigger(Events.QUALITY_CHANGE_REQUESTED, {mediaType: type, streamInfo: streamInfo, oldQuality: oldQuality, newQuality: newQuality, reason: reason});
    }


    function setAbandonmentStateFor(type, state) {
        abandonmentStateDict[type].state = state;
    }

    function getAbandonmentStateFor(type) {
        return abandonmentStateDict[type].state;
    }

    /**
     * @param {MediaInfo} mediaInfo
     * @param {number} bitrate A bitrate value, kbps
     * @returns {number} A quality index <= for the given bitrate
     * @memberof AbrController#
     */
    function getQualityForBitrate(mediaInfo, bitrate) {

        const bitrateList = getBitrateList(mediaInfo);

        if (!bitrateList || bitrateList.length === 0) {
            return QUALITY_DEFAULT;
        }

        for (let i = bitrateList.length - 1; i >= 0; i--) {
            const bitrateInfo = bitrateList[i];
            if (bitrate * 1000 >= bitrateInfo.bitrate) {
                return i;
            }
        }
        return 0;
    }

    /**
     * @param {MediaInfo} mediaInfo
     * @returns {Array|null} A list of {@link BitrateInfo} objects
     * @memberof AbrController#
     */
    function getBitrateList(mediaInfo) {
        if (!mediaInfo || !mediaInfo.bitrateList) return null;

        var bitrateList = mediaInfo.bitrateList;
        var type = mediaInfo.type;

        var infoList = [];
        var bitrateInfo;

        for (var i = 0, ln = bitrateList.length; i < ln; i++) {
            bitrateInfo = new BitrateInfo();
            bitrateInfo.mediaType = type;
            bitrateInfo.qualityIndex = i;
            bitrateInfo.bitrate = bitrateList[i].bandwidth;
            bitrateInfo.width = bitrateList[i].width;
            bitrateInfo.height = bitrateList[i].height;
            infoList.push(bitrateInfo);
        }

        return infoList;
    }

    function setAverageThroughput(type, value) {
        averageThroughputDict[type] = value;
    }

    function getAverageThroughput(type) {
        return averageThroughputDict[type];
    }

    function updateTopQualityIndex(mediaInfo) {
        var type = mediaInfo.type;
        var streamId = mediaInfo.streamInfo.id;
        var max = mediaInfo.representationCount - 1;

        setTopQualityIndex(type, streamId, max);

        return max;
    }

    function isPlayingAtTopQuality(streamInfo) {
        var isAtTop;
        var streamId = streamInfo.id;
        var audioQuality = getQualityFor('audio', streamInfo);
        var videoQuality = getQualityFor('video', streamInfo);

        isAtTop = (audioQuality === getTopQualityIndexFor('audio', streamId)) &&
            (videoQuality === getTopQualityIndexFor('video', streamId));

        return isAtTop;
    }

    function reset () {
        eventBus.off(Events.LOADING_PROGRESS, onFragmentLoadProgress, this);
        clearTimeout(abandonmentTimeout);
        abandonmentTimeout = null;
        setup();
    }

    function getQualityFor(type, streamInfo) {
        var id = streamInfo.id;
        var quality;

        qualityDict[id] = qualityDict[id] || {};

        if (!qualityDict[id].hasOwnProperty(type)) {
            qualityDict[id][type] = QUALITY_DEFAULT;
        }

        quality = qualityDict[id][type];
        return quality;
    }

    function setQualityFor(type, id, value) {
        qualityDict[id] = qualityDict[id] || {};
        qualityDict[id][type] = value;
    }

    function getConfidenceFor(type, id) {
        var confidence;

        confidenceDict[id] = confidenceDict[id] || {};

        if (!confidenceDict[id].hasOwnProperty(type)) {
            confidenceDict[id][type] = 0;
        }

        confidence = confidenceDict[id][type];

        return confidence;
    }

    function setConfidenceFor(type, id, value) {
        confidenceDict[id] = confidenceDict[id] || {};
        confidenceDict[id][type] = value;
    }

    function setTopQualityIndex(type, id, value) {
        topQualities[id] = topQualities[id] || {};
        topQualities[id][type] = value;
    }

    function checkMaxBitrate(idx, type) {
        var maxBitrate = getMaxAllowedBitrateFor(type);
        if (isNaN(maxBitrate) || !streamProcessorDict[type]) {
            return idx;
        }
        var maxIdx = getQualityForBitrate(streamProcessorDict[type].getMediaInfo(), maxBitrate);
        return Math.min (idx , maxIdx);
    }

    function checkMaxRepresentationRatio(idx, type, maxIdx) {
        var maxRepresentationRatio = getMaxAllowedRepresentationRatioFor(type);
        if (isNaN(maxRepresentationRatio) || maxRepresentationRatio >= 1 || maxRepresentationRatio < 0) {
            return idx;
        }
        return Math.min( idx , Math.round(maxIdx * maxRepresentationRatio) );
    }

    function checkPortalSize(idx, type) {
        if (type !== 'video' || !limitBitrateByPortal || !streamProcessorDict[type]) {
            return idx;
        }

        var hasPixelRatio = usePixelRatioInLimitBitrateByPortal && window.hasOwnProperty('devicePixelRatio');
        var pixelRatio = hasPixelRatio ? window.devicePixelRatio : 1;
        var element = videoModel.getElement();
        var elementWidth = element.clientWidth * pixelRatio;
        var elementHeight = element.clientHeight * pixelRatio;
        var manifest = manifestModel.getValue();
        var representation = dashManifestModel.getAdaptationForType(manifest, 0, type).Representation;
        var newIdx = idx;

        if (elementWidth > 0 && elementHeight > 0) {
            while (
                newIdx > 0 &&
                representation[newIdx] &&
                elementWidth < representation[newIdx].width &&
                elementWidth - representation[newIdx - 1].width < representation[newIdx].width - elementWidth
            ) {
                newIdx = newIdx - 1;
            }

            if (representation.length - 2 >= newIdx && representation[newIdx].width === representation[newIdx + 1].width) {
                newIdx = Math.min(idx, newIdx + 1);
            }
        }

        return newIdx;
    }

    function onFragmentLoadProgress(e) {
        const type = e.request.mediaType;
        if (getAutoSwitchBitrateFor(type)) {

            const rules = abrRulesCollection.getRules(ABRRulesCollection.ABANDON_FRAGMENT_RULES);
            const scheduleController = streamProcessorDict[type].getScheduleController();
            if (!scheduleController) return;// There may be a fragment load in progress when we switch periods and recreated some controllers.

            const callback = function (switchRequest) {
                if (switchRequest.confidence === SwitchRequest.STRONG &&
                    switchRequest.value < getQualityFor(type, streamController.getActiveStreamInfo())) {

                    const fragmentModel = scheduleController.getFragmentModel();
                    const request = fragmentModel.getRequests({state: FragmentModel.FRAGMENT_MODEL_LOADING, index: e.request.index})[0];
                    if (request) {
                        //TODO Check if we should abort or if better to finish download. check bytesLoaded/Total
                        fragmentModel.abortRequests();
                        setAbandonmentStateFor(type, ABANDON_LOAD);
                        setPlaybackQuality(type, streamController.getActiveStreamInfo(), switchRequest.value, switchRequest.reason);
                        eventBus.trigger(Events.FRAGMENT_LOADING_ABANDONED, {streamProcessor: streamProcessorDict[type], request: request, mediaType: type});

                        clearTimeout(abandonmentTimeout);
                        abandonmentTimeout = setTimeout(() => {
                            setAbandonmentStateFor(type, ALLOW_LOAD);
                            abandonmentTimeout = null;
                        }, mediaPlayerModel.getAbandonLoadTimeout());
                    }
                }
            };

            rulesController.applyRules(rules, streamProcessorDict[type], callback, e, function (currentValue, newValue) {
                return newValue;
            });
        }
    }

    instance = {
        isPlayingAtTopQuality: isPlayingAtTopQuality,
        updateTopQualityIndex: updateTopQualityIndex,
        getAverageThroughput: getAverageThroughput,
        getBitrateList: getBitrateList,
        getQualityForBitrate: getQualityForBitrate,
        getMaxAllowedBitrateFor: getMaxAllowedBitrateFor,
        setMaxAllowedBitrateFor: setMaxAllowedBitrateFor,
        getMaxAllowedRepresentationRatioFor: getMaxAllowedRepresentationRatioFor,
        setMaxAllowedRepresentationRatioFor: setMaxAllowedRepresentationRatioFor,
        getInitialBitrateFor: getInitialBitrateFor,
        setInitialBitrateFor: setInitialBitrateFor,
        getInitialRepresentationRatioFor: getInitialRepresentationRatioFor,
        setInitialRepresentationRatioFor: setInitialRepresentationRatioFor,
        setAutoSwitchBitrateFor: setAutoSwitchBitrateFor,
        getAutoSwitchBitrateFor: getAutoSwitchBitrateFor,
        setLimitBitrateByPortal: setLimitBitrateByPortal,
        getLimitBitrateByPortal: getLimitBitrateByPortal,
        getUsePixelRatioInLimitBitrateByPortal: getUsePixelRatioInLimitBitrateByPortal,
        setUsePixelRatioInLimitBitrateByPortal: setUsePixelRatioInLimitBitrateByPortal,
        getConfidenceFor: getConfidenceFor,
        getQualityFor: getQualityFor,
        getAbandonmentStateFor: getAbandonmentStateFor,
        setAbandonmentStateFor: setAbandonmentStateFor,
        setPlaybackQuality: setPlaybackQuality,
        setAbrAlgorithm: setAbrAlgorithm,
        setTruthBandwidth: setTruthBandwidth,
        setStartTime: setStartTime,
        getPlaybackQuality: getPlaybackQuality,
        setAverageThroughput: setAverageThroughput,
        getTopQualityIndexFor: getTopQualityIndexFor,
        initialize: initialize,
        setConfig: setConfig,
        reset: reset
    };

    setup();

    return instance;
}

AbrController.__dashjs_factory_name = 'AbrController';
let factory = FactoryMaker.getSingletonFactory(AbrController);
factory.ABANDON_LOAD = ABANDON_LOAD;
factory.QUALITY_DEFAULT = QUALITY_DEFAULT;
export default factory;
