# qdisc-experiments

This repo contains a set of Qdisc experiments. Each experiments study the effect of parameters for different egress QDiscs on overall throughput behaviour. Each simulates different network scanrios, aiming to find out unexpected throughput behaviour. 

## HHF Parameter Evaluation

This experiment uses Mininet for the setup. The user can change the QDisc config file to understand the effect of each HHF parameter on the overall throughput. 

## HTB Priority Experiment

This experiment aims to reproduce a known issue discussed in the Linux mailing list:  
[LARTC Message #23403](https://www.spinics.net/lists/lartc/msg23403.html)

## HTB Hard Maximum Experiment

This experiment aims to reproduce a known issue discussed in the Linux mailing list:  
[Serverfault traffic shaping with HTB issue](https://serverfault.com/questions/254535/traffic-shaping-on-linux-with-htb-weird-results)