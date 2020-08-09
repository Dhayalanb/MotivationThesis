from forksrv import ForkSrv
from importer import Importer
import logging, os, sys, getopt, defs



def main(argv):
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    try:
        opts, args = getopt.getopt(argv,"hb:c:j:o:t:a:",["help", "binary=","concolic=","threads=","output=", "traces=", "arguments="])
    except getopt.GetoptError:
        print('test.py -b <binary> -c <concolic> -j <threads> -o <output> -t <traces> -a <arguments>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -b <binary> -c <concolic> -j <threads> -o <output> -t <traces> -a <arguments>')
            sys.exit()
        elif opt in ("-b", "--binary"):
            defs.BINARY = arg
        elif opt in ("-c", "--concolic"):
            defs.CONCOLIC_BINARY = arg
        elif opt in ("-j", "--threads"):
            defs.NUMBER_OF_THREADS = int(arg)
        elif opt in ("-o", "--output"):
            defs.OUTPUT_DIR = arg
        elif opt in ("-t", "--traces"):
            defs.TRACES_FOLDER = arg
        elif opt in ("-a", "--arguments"):
            with open(arg, 'r') as arg_file:
                defs.ARGUMENTS = arg_file.read().strip().split(' ')
    print('Binary is ', defs.BINARY)
    print('Concolic binary is ', defs.CONCOLIC_BINARY)
    print('Getting traces from ', defs.TRACES_FOLDER)
    print('Outputting results to ', defs.OUTPUT_DIR)
    print('Running with threads: ', defs.NUMBER_OF_THREADS)
    print('Running with arguments: ', defs.ARGUMENTS)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    importer = Importer(defs.TRACES_FOLDER)
    traces = importer.get_traces_iterator()
    server = ForkSrv()
    server.listen(0)
    for trace in traces:
        (status, result) = server.run_with_condition(trace.getCondition(0).base,trace.getInput())
        print("%d" % result.lb1)
        if result.lb1 == 2**32-1:
            print("First condition not reached!")
        (status, result) = server.run_with_condition(trace.getCondition(trace.getConditionLength()-1).base,trace.getInput())
        print("%d" % result.lb1)
        if result.lb1 == 2**32-1:
            print("Last not reached!")
        break
    server.close()

if __name__ == "__main__":
   main(sys.argv[1:])
