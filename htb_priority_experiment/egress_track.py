import subprocess
import time
import re

# this file tracks the egress traffic at the sender
def get_udp_egress_bytes(iface='enp130s0', qdisc_id='20'):
    out = subprocess.check_output(['tc', '-s', 'qdisc', 'show', 'dev', iface]).decode()
    blocks = out.split('\n\n')  # split per qdisc
    for block in blocks:
        print(block)
        if f'qdisc sfq {qdisc_id}:' in block:
            lines = block.splitlines()
            for line in lines:
                if 'Sent' in line:
                    match = re.search(r'Sent (\d+) bytes (\d+) pkt', line)
                    if match:
                        bytes_sent = int(match.group(1))
                        pkts_sent = int(match.group(2))
                        return bytes_sent, pkts_sent
    return 0, 0


while True:
    bytes_sent, pkts_sent = get_udp_egress_bytes()
    print(f"UDP Egress: {bytes_sent} bytes, {pkts_sent} packets")
    time.sleep(1)