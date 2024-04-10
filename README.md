# qdisc-experiments

To change hhf qdisc configuration: qdisc-config.json 

To run the experiment: sudo python3 mn-main.py

To generate a throughput graph over time for all flows:
    input_path = sys.argv[1]   # path to a json file
    output_path = sys.argv[2]  # path to output image file
    x_unit = int(sys.argv[3])  # in sec, period between points
python3 getGraph.py log-receiver.json throughput_plot_sample.jpg 10 

