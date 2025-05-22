## HTB Hard Maximum Experiment

This experiment aims to reproduce a known issue discussed in the Linux mailing list:  
[Serverfault traffic shaping with HTB issue](https://serverfault.com/questions/254535/traffic-shaping-on-linux-with-htb-weird-results)

## How to Run

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

