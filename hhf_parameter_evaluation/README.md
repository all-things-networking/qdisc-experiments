# HHF-parameter-experiment

## Experiment Setup

This experiment utilizes **Mininet** to simulate a simple network topology consisting of two hosts: `H1` and `H2`.  
- `H1` acts as the **sender**, transmitting packets to `H2`, the **receiver**.
- The **HHF qdisc** is applied to `H1`'s egress interface, with configuration parameters specified in the `qdisc-config.json` file.

During the experiment:
- `H1` continuously sends packets to `H2`.
- `H2` logs the received packets for analysis.

After the experiment, users can generate throughput graphs to visualize how the throughput evolves over time.

## To Run the Experiment

This experiment uses **HHF QDiscs**.  
To change the HHF qdisc configuration, modify `qdisc-config.json`.  
See the [Changing HHF QDisc Configuration](#changing-hhf-qdisc-configuration) section below for a brief explanation.

To run the experiment:
```bash
sudo python3 mn-main.py
```

To generate a throughput graph over time for all flows:
- `input_path = sys.argv[1]` – path to a JSON file  
- `output_path = sys.argv[2]` – path to output image file  
- `x_unit = int(sys.argv[3])` – in seconds, period between points

Example:
```bash
python3 getGraph.py log-receiver.json throughput_plot_sample.jpg 10
```

---

## Outputs

After each run, the program generates a pair of graphs.

The format of the output files is:
```
[number]_[s/r]_plot.jpg
```

Where:
- `[number]` – number of heavy hitters for that specific run  
  - Note: For small `hh_flows_limit`, this number could be a float.
- `[s/r]` – whether it's the plot at the sender’s (`s`) or receiver’s (`r`) end

---

## Changing HHF QDisc Configuration

Brief explanation of **HHF QDisc parameters**:

- **`hhf_reset_timeout`**  
  Period to reset counter values in the multi-stage filter (default: `40ms`)  
  > Counter values are increased by packet size, so periodic refresh is necessary.

- **`hhf_admit_bytes`**  
  Threshold to classify heavy hitters (default: `128KB`)  
  > Combined with `hhf_reset_timeout`, captures flows sending  
  > more than `128KB / 40ms = 25Mbps`.

- **`hhf_evict_timeout`**  
  Threshold to evict idle heavy hitters (default: `1s`)  
  > Should be large enough to avoid reordering during HH eviction.

- **`hhf_non_hh_weight`**  
  WDRR (Weighted Deficit Round Robin) weight for non-heavy-hitters (default: `2`)  
  > Weight ratio: Non-HH : HH = 2:1

- **`hh_flows_limit`**  
  Maximum number of heavy-hitter flow entries (default: `2048`)
