from static_parser import StaticParser
from output_parser import Parser
from importer import Importer
import defs
import getopt, sys

def combine_results(dynamic_files, static_files, relative_depth):
    results = []
    strategies = list(dynamic_files.keys())
    strategies.sort()
    del strategies[strategies.index("GradientDescentStrategy")]
    strategies.insert(0, "GradientDescentStrategy")
    offset_map = {}
    for strategy in strategies:
        for file_name in dynamic_files[strategy]:
            print(file_name)
            result = dynamic_files[strategy][file_name].copy()
            if file_name not in offset_map:
                offset_map[file_name] = len(result['offsets'])
            cmpid = file_name.split('_')[0]
            result['flipped'] = 1 if result['status'] == defs.FLIPPED_STRING else 0
            result['id'] = file_name[:-5]
            result['cmpid'] = cmpid
            result['strategy'] = strategy
            result['nrOfOffsets'] = offset_map[file_name]
            should_fill_in = True if cmpid in static_files else False
            result['cyclomatic'] = static_files[cmpid].cyclomatic if should_fill_in else "-"
            result['oviedo'] =  static_files[cmpid].oviedo  if should_fill_in else "-"
            result['chain_size'] =  static_files[cmpid].chain_size  if should_fill_in else "-"
            result['cases'] =  static_files[cmpid].cases  if should_fill_in else "-"
            if file_name[:-5] in relative_depth:
                result['trace_length'] = relative_depth[file_name[:-5]]
                result['reachableness'] = relative_depth[file_name[:-5]][2]
            else:
                result['trace_length'] = (-1,-1)
                result['reachableness'] = 0
            results.append(result)
    return results


def write_results(results, output_name):
    csv = "Strategy,id,cmpid,nrOfMisses,nrOfInputs,depth,status,totalTime,nrOfOffsets,cyclomatic,oviedo,chain_size,cases,depth2,trace_length,flipped,reachableness,combined\n"
    for result in results:
        for key in result:
            if key != 'trace_length':
                result[key] = str(result[key])
        csv += result['strategy'] + "," + result['id'] + "," + result['cmpid'] + "," + result['nrOfMisses'] + "," + result['nrOfInputs'] + "," + result['depth'] + "," + result['status'] + "," + result['totalTime'] + "," + result['nrOfOffsets'] + "," + result['cyclomatic'] + "," + result['oviedo'] + "," + result['chain_size'] + ","+ result['cases']+ ","+ str(result['trace_length'][0]) + ","+ str(result['trace_length'][1]) + ","+ result['flipped'] + "," + result['reachableness'] + "," + result['combined']
        csv += "\n"
    with open(output_name, 'w') as output_file:
        output_file.write(csv)

def get_depth_from_traces(traces):
    relative_depth = {}
    for trace in traces:
        trace_length = trace.getConditionLength()
        for i in range(trace_length):
            condition = trace.getCondition(i)
            condition_base = condition.base
            cmpid = condition_base.getLogId()
            if cmpid not in relative_depth:
                relative_depth[cmpid] = (i, trace_length, condition.reachableness)
    return relative_depth

def average_dynamic_files(dynamic_files):
    dynamic_results = {}
    for dynamic_file in dynamic_files:
        for strategy in dynamic_file:
            if strategy not in dynamic_results:
                dynamic_results[strategy] = {}
            for file_name in dynamic_file[strategy]:
                if file_name in dynamic_results:
                    #Take average of time, if it was flipped, set status to flipped
                    combined = dynamic_results[strategy][file_name]['combined']
                    old_total_time = dynamic_results[strategy][file_name]['totalTime']
                    new_total_time = (dynamic_file[strategy][file_name]['totalTime'] + old_total_time*combined)/(combined+1)
                    dynamic_results[strategy][file_name]['combined'] += 1
                    dynamic_results[strategy][file_name]['totalTime'] = new_total_time
                    if (dynamic_file[strategy][file_name]['status'] == defs.FLIPPED_STRING):
                        dynamic_results[strategy][file_name]['status'] = defs.FLIPPED_STRING
                else:
                    dynamic_results[strategy][file_name] = dynamic_file[strategy][file_name]
                    dynamic_results[strategy][file_name]['combined'] = 1
def main(argv):
    dynamic_folders = []
    static_folder = ""
    output_name = ""
    traces_folder = ""
    try:
        opts, args = getopt.getopt(argv,"d:s:o:t:",["dynamic=", "static=", "output=", "traces="])
    except getopt.GetoptError:
        print('create_raw_output.py -d <dynamic> -s <static> -t <traces>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('create_raw_output.py -d <dynamic> -s <static> -t <traces>')
            sys.exit()
        elif opt in ("-d", "--dynamic"):
            dynamic_folders.append(arg)
        elif opt in ("-s", "--static"):
            static_folder = arg
        elif opt in ("-o", "--output"):
            output_name = arg
        elif opt in ("-t", "--traces"):
            traces_folder = arg
    print("Reading files...")
    static_files = StaticParser.parse_analysis_files(static_folder)
    print("Parsed static files")
    dynamic_files = []
    for dynamic_folder in dynamic_folders:
        dynamic_files.append(Parser.parse_folder(dynamic_folder))
    print("Parsed dynamic files")
    i = Importer(traces_folder)
    traces = i.get_traces_iterator()
    relative_depth = get_depth_from_traces(traces)
    print("Parsed trace files")
    dynamic_results = average_dynamic_files(dynamic_files)
    results = combine_results(dynamic_results, static_files, relative_depth)
    print("Created results")
    write_results(results, output_name)
    print("Done! Results written to" + output_name)


if __name__ == "__main__":
   main(sys.argv[1:])
