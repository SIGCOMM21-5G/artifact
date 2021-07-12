## A Variegated Look at 5G in the Wild

In this repository, we release the dataset and tools in SIGCOMM '21 paper, *A Variegated Look at 5G in the Wild: Performance, Power, and QoE Implications*. 

This is a measurement paper with several types of experiments conducted for different purposes having different methodologies. To help you quickly navigate and have the ability to understand the different pieces, we have created different folders for different experiments. There are README files within each folder that provide instructions on validating the experiment-specific artifacts. At the very top of the README instructions, we also specify which results/plots (e.g. Figure 2 in the paper) the folder is responsible. Lastly, to make it easy here are some generic principles we followed for releasing the artifacts:

#### Dataset size
- If the dataset is small enough, we included the dataset file in this repository itself. 
- If the dataset files are huge, we use a small sample of the dataset in the repository to demonstrate the functionality/correctness. You can replace the small subset with the full dataset (provided using a link to a Shared Google Drive folder) to further validate. In either case, we provide full processed results as well. See next part for details. 


#### Data Analysis, Model/Plot Generation

- If data analysis is involved, our instructions will contain information on how to process the data. 
- No matter what the dataset size is, we provide the fully generated results and/or plots. If you decide to run the analysis and/or plotting scripts, the outcome of processing will simply replace the existing files in the repository.
- For the artifacts involved in section 5 (ABR video streaming), a lot of computing resources are required. We have therefore provided:
    1. a screencast to show how the results were generated
    2. output logs
    3. if one has their own compute resources, we provide instructions on how to evaluate.

#### User-side Measurement tools

- <b>5G Tracker</b>: is available for free of cost to academic research groups and non-profit organizations. If you qualify, please [click here](https://license.umn.edu/product/5g-tracker-android-application-for-collecting-and-visualizing-5g-performance-data) to apply and get access to 5G Tracker. Note, in addition to this tool, you will need to arrange for 5G data services/sim cards. 5G Tracker features:
   - Record passive measurements using Android APIs
   - Record active measurements using iPerf3 and Ping
   - RRC-Probe
   - Packet dumps using TCPDUMP
   
- Monsoon Power Monitor

---

#### Paper Structure to Folder Structure
 
  

|                Content in Paper                     |      Folder in Repo.     | Description                                                                               |
|:---------------------------------------------------:|:------------------------:|-------------------------------------------------------------------------------------------|
|            Figures 1 to 7  (Section 3)              |     [NW-Perf-Speedtest](NW-Perf-Speedtest)    | Network performance measurements and analysis.                                            |
|               Figure 8  (Section 3)                 |   [TCP-Single-Conn-Perf](TCP-Single-Conn-Perf)   | Single conn. downlink throughput performance under different transport layer settings.    |
|               Figure 9  (Section 3)                 |       [Driving-Wild](Driving-Wild)       | Handoff frequency while driving across different Low-Band frequency settings.             |
|              Figure 10  (Section 4.2)               |         [RRC-Probe](RRC-Probe)        | Inferring RRC states for different carrier/frequency band setting.                        |
|               Table 2 (Section 4.2)                 |         [RRC-Power](RRC-Power)        | Use RRC-Probe + Power Monitor to measure power during RRC state transitions.              |
| Figures 11, 12 (Section 4.3), 26, 27 (Appendix A.4) |    [Data-Transfer-Power](Data-Transfer-Power)   | Conduct controlled to measure power during data transfers in multiple settings.           |
|           Figures 13 and 14 (Section 4.4)           |  [Power-SignalStrength](Power-SignalStrength)    | Orangized data to study the relationship between power/energy efficiency and signal strength  |
|          Figures 15 and 16 (Section 4.5)            |        [Power-Model](Power-Model)       | Power Model Construction and Evaluation                                                   |
|   Table 3 (Section 4.6),  Table 9 (Appendix A.5)     | [Benchmark-Software-Power](Benchmark-Software-Power) | Benchmarking software-based power monitor.                                                |
|           Figures 17 and 18 (Section 5)             |      [Video-Streaming](Video-Streaming)     | Evaluate ABR algorithms for video streaming using real-world 5G and 4G throughput traces. |
|        Figures 19 to 22, Table 6 (Section 6)         |       [Web-Browsing](Web-Browsing)       | QoE implications (performance v/s energy efficiency) of using 4G v/s 5G for web-browsing. |

---

As always, if there are any questions, feel free to reach out to us (<arvind@cs.umn.edu>, <xumiao@umich.edu>)! 
