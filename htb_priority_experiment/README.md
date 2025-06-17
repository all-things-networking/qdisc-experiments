# HTB Priority Experiment

This experiment aims to reproduce a known issue discussed in the Linux mailing list:  
[LARTC Message #23403](https://www.spinics.net/lists/lartc/msg23403.html)

---

## Setup

- The experiment uses **two Blue machines** from the Syn Cluster as the **sender** and **receiver**.
- The **sender's qdisc** is modified using HTB.
- There are **two traffic flows**:
  - **TCP** and **UDP**, each assigned different priorities.
- The **rate of each flow** is varied.
- We measure:
  - **Egress traffic rate** at the sender
  - **Ingress traffic rate** at the receiver

### QDISC Command Used
```bash
sudo tc qdisc del dev enp130s0 root
sudo tc qdisc add dev enp130s0 handle 1: root htb default 15
sudo tc class add dev enp130s0 parent 1: classid 1:1 htb 1000kbit ceil 1000kbit
sudo tc class add dev enp130s0 parent 1:1 classid 1:14 htb rate 200kbit ceil 1000kbit prio 1
sudo tc class add dev enp130s0 parent 1:1 classid 1:15 htb rate 10kbit ceil 1000kbit prio 2
sudo tc filter add dev enp130s0 parent 1: protocol ip u32 match ip tos 0xb8 0xff flowid 1:14
sudo tc filter add dev enp130s0 parent 1: protocol ip u32 match ip tos 0x00 0xff flowid 1:15
sudo tc qdisc add dev enp130s0 parent 1:14 handle 20: sfq limit 40
sudo tc qdisc add dev enp130s0 parent 1:15 handle 50: pfifo limit 1000
tc qdisc show
```
TODO: the tos fields to filter tcp/udp flows from the above tc commands, which were directly copied from the mailing list threads, don't filter out the flows as expected. 

---

## How to Run

### Receiver

Start the receiver logger:
```bash
sudo -E python3 receiver.py
```

### TCP flow with iperf:

Start TCP server:
```bash
iperf -s -p 8890
```

Start TCP client (from sender)
```bash
iperf -c 10.30.0.1 -p 8890 -t 400
```

### UDP flow with udpsender.py
Launch five instances of the UDP sender, ideally spaced 10 seconds apart:
```bash
sudo -E python3 udpsender.py &
```
Run five UDP instances on different CPUS to avoid the threshold (TODO)

### Monitor Egress Traffic
In a separate terminal on the sender, run:
```bash
sudo -E python3 egress_track.py
```