## HTB Hard Maximum Experiment

This experiment aims to reproduce a known issue discussed in the Linux mailing list:  
[Serverfault traffic shaping with HTB issue](https://serverfault.com/questions/254535/traffic-shaping-on-linux-with-htb-weird-results)

## How to Run

### QDISC Command Used
```bash
sudo tc qdisc del dev enp130s0 root
sudo tc qdisc add dev enp130s0 root handle 1: htb default 1 r2q 1
sudo tc class add dev enp130s0 parent 1: classid 1:1 htb rate 75kbit
sudo tc class add dev enp130s0 parent 1:1 classid 1:10 htb rate 75kbit
sudo tc filter add dev enp130s0 parent 1:0 protocol ip prio 1 u32 match ip dst 10.40.0.1 flowid 1:10
tc qdisc show dev enp130s0
```

### Receiver

Start the receiver logger and observe the rate split:
```bash
sudo -E python3 recv.py
```

### 2 sender programs:

Start 2 server programs:
```bash
sudo -E python3 client1.py
sudo -E python3 client2.py
```

