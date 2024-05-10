import json
import matplotlib
import matplotlib.pyplot as plt
import sys

def generate_graph(input_path, output_path, x_unit):
    

    # Load throughput data from JSON file
    with open(input_path, 'r') as file:
        throughput_data = json.load(file)

    # Initialize lists to store x (time) and y (throughput) values for each flow
    x_values = []
    y_values = []

    plt.figure(figsize=(10, 6))

    for flowid, data_points in throughput_data.items():
        i = 1
        x_values = []
        y_values = []
        for pt in data_points:
            x_values.append(i)
            y_values.append(pt/x_unit) # y axis is byte/sec
            i += 1
        plt.plot(x_values, y_values, label=flowid)


    # Set plot labels and title
    plt.xlabel('Time (second)')
    plt.ylabel('Throughput (bytes)')
    plt.title('Throughput vs. Time')
    plt.legend()

    # # show the configuration as well
    # with open("qdisc-config.json") as qdisc_conf_fp:
    #     file_content = qdisc_conf_fp.read()[1:-1]
    # plt.annotate(file_content, xy=(0.6, -0.0), xycoords='axes fraction', ha='left', fontsize=10)
    # Display the plot
    # plt.show()
    plt.savefig(output_path)


if __name__ == '__main__':
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    x_unit = int(sys.argv[3]) # in sec, period between points
    generate_graph(input_path, output_path, x_unit)