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

### Monitor Egress Traffic
In a separate terminal on the sender, run:
```bash
sudo -E python3 egress_track.py
```