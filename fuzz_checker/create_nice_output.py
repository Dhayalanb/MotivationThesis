import sys, getopt
from collections import Counter
import scipy.stats
import matplotlib.pyplot as plt

STRATEGIES = ['GradientDescentStrategy', 'MagicByteStrategy' , 'OneByteStrategy', 'LengthTaintStrategy', 'ConcolicStrategy', 'RandomStrategy', 'RandomTaintStrategy']
VARIABLES_TO_TEST = ['oviedo', 'cyclomatic' , 'nrOfOffsets', 'cases', 'chain_size', 'depth2', 'trace_length']
VARIABLES_TO_PRINT = ['Ovie', 'Cycl' , 'Offs', 'Cases', 'Chain', 'AbsD', 'RelD']
LOCATION = '../results/matplots/'

def make_tests(header, data):
    test_results = {}
    for strategy in STRATEGIES:
        data_to_test = data[strategy]
        if strategy not in test_results:
            test_results[strategy] = {}
        for variable in VARIABLES_TO_TEST:
            #collect data
            collected_data = []
            for i in range(len(data_to_test[variable])):
                if data_to_test[variable][i] == '-':
                    continue
                if variable == 'trace_length':
                    collected_data.append((data_to_test['depth2'][i]/data_to_test['trace_length'][i], data_to_test['flipped'][i]))
                else:
                    collected_data.append((data_to_test[variable][i], data_to_test['flipped'][i]))
            #Split in 2 groups, 1 population with flipped, 1 without flipped an see if it comes from 2 different populations
            x = [x[0] for x in collected_data if x[1] == 0] #population which is not flipped
            y = [x[0] for x in collected_data if x[1] == 1] #population which is flipped
            print("testing %s" % (variable))
            test_results[strategy][variable] = scipy.stats.mannwhitneyu(x, y, use_continuity = (True if variable == 'relative_depth' else False))
    return test_results

def make_tables(test_results, name):
    csv = ","+",".join(VARIABLES_TO_TEST) + "\n"
    latex = '''
    \\begin{table}[H]
    \centering
    \\begin{tabular}{llllllll}
&  ''' + "&".join(VARIABLES_TO_PRINT) + "\\\\\n" 
    for strategy in STRATEGIES:
        csv += strategy + ","
        latex += strategy + "&"
        for variable in VARIABLES_TO_TEST:
            result = str(round(test_results[strategy][variable].pvalue, 2))
            csv += result + ','
            if test_results[strategy][variable].pvalue < 0.05:
                latex += "\cellcolor[HTML]{FFC7CE}{\color[HTML]{9C0006}" + result + '}&'
            else:
                latex += result + '&'
        csv = csv[:-1] + "\n"
        latex = latex[:-1] + "\\\\\n"
    latex += '''
    \end{tabular}
    \caption{Significant difference of several metrics \\texttt{%s} binary}
    \label{tab:%sWhitneyU}
    \end{table}
    ''' % (name, name)
    with open(LOCATION + name + '_tests.csv', 'w') as csv_file:
        csv_file.write(csv)
    with open(LOCATION + name + '_tests.tex', 'w') as latex_file:
        latex_file.write(latex)

    

def make_plots(header, data, name):
    #make total flip plot
    keys = {}
    for strategy in STRATEGIES:
        keys[strategy] = Counter(data[strategy]['status'])
    all_statuses = list(set([status for key in keys for status in keys[key]]))
    labels = STRATEGIES
    all_values = []
    for status in all_statuses:
        values = []
        for strategy in labels:
            if status in keys[strategy]:
                values.append(keys[strategy][status])
            else:
                values.append(0)
        all_values.append(values)
    bottom = [0 for _ in range(len(all_values[0]))]
    plt.figure(1)
    fig, ax = plt.subplots(figsize=(7, 7))
    for i in range(len(all_values)):
        ax.bar(labels, all_values[i], label=all_statuses[i], width = 0.5, bottom=bottom)
        bottom = [bottom[j] + all_values[i][j] for j in range(len(all_values[i]))]
    ax.legend()
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.4)
    plt.savefig(LOCATION + name + '_total_flips.svg')
    #make substrategy flip plot
    #TODO
    #make absolute depth plot
    plt.figure(3)
    fig, ax = plt.subplots(figsize=(7, 7))
    labels = ["%s-%s%%" % (i,i+10) for i in range(0,100,10)]
    for strategy in STRATEGIES:
        data_to_bucket = [(data[strategy]['depth2'][i], data[strategy]['flipped'][i]) for i in range(len(data[strategy]['depth2']))]
        max_value = float(max([value[0] for value in data_to_bucket]))
        x = [sum([value[1] for value in data_to_bucket if value[0] >= max_value*i/10 and (value[0] < (i+1)*max_value/10  or (i == 9 and value[0] <= (i+1)*max_value/10))]) for i in range(0,10)]
        ax.plot(labels, x, label=strategy)
    ax.legend()
    plt.savefig(LOCATION + name + '_absolute_depth.svg')
    #make relative depth plot
    plt.figure(4)
    fig, ax = plt.subplots(figsize=(7, 7))
    labels = ["%s-%s%%" % (i,i+10) for i in range(0,100,10)]
    for strategy in STRATEGIES:
        data_to_bucket = [(data[strategy]['depth2'][i]*100./data[strategy]['trace_length'][i], data[strategy]['flipped'][i]) for i in range(len(data[strategy]['depth2']))]
        x = [sum([value[1] for value in data_to_bucket if value[0] >= i and (value[0] < (i+10)  or (i == 90 and value[0] <= (i+10)))]) for i in range(0,100,10)]
        ax.plot(labels, x, label=strategy)
    ax.legend()
    plt.savefig(LOCATION + name + '_relative_depth.svg')
    #make offset plot
    plt.figure(5)
    fig, ax = plt.subplots(figsize=(7, 7))
    for strategy in STRATEGIES:
        data_to_show = [(data[strategy]['nrOfOffsets'][i], data[strategy]['flipped'][i]) for i in range(len(data[strategy]['nrOfOffsets']))]
        labels = list(set([value[0] for value in data_to_show]))
        labels.sort()
        x = [sum([value [1] for value in data_to_show if value[0] == label]) for label in labels]
        labels = [str(x) for x in labels]
        ax.plot(labels, x, label=strategy)
    ax.legend()
    plt.savefig(LOCATION + name + '_offsets.svg')

def process_file(raw_file):
    with open(raw_file, 'r') as input_file:
        data = input_file.read()
    processed_data = {}
    header = data.split('\n')[0].split(',')
    for row in data.split('\n')[1:]:
        columns = row.split(',')
        if len(columns) != len(header):
            continue
        strategy = columns[0]
        if strategy not in processed_data:
            processed_data[strategy] = {}
        for i in range(len(header)):
            column_name = header[i]
            if column_name not in processed_data[strategy]:
                processed_data[strategy][column_name] = []
            value = columns[i]
            try:
                value = int(value)
            except ValueError:
                pass
            processed_data[strategy][column_name].append(value)
    return (header, processed_data)

def main(argv):
    raw_file = ""
    name = ''
    try:
        opts, args = getopt.getopt(argv,"r:n:",["raw=", "name="])
    except getopt.GetoptError:
        print('create_nice_output.py -r <raw> -n <name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('create_nice_output.py -r <raw> -n <name>')
            sys.exit()
        elif opt in ("-r", "--raw"):
            raw_file = arg
        elif opt in ("-n", "--name"):
            name = arg
    print("Processing data...")
    header, processed_data = process_file(raw_file)
    print("Doing tests")
    test_result = make_tests(header, processed_data)
    print("Making plots")
    make_plots(header, processed_data, name)
    print("Making tables")
    make_tables(test_result, name)
    print("Done!")

if __name__ == "__main__":
   main(sys.argv[1:])