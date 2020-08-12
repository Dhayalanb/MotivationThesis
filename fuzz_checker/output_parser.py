import os, json, defs, sys, getopt

class Parser:

    output_dir = '../results/'

    flipped_condition_ids = set()
    all_condition_ids = set()
    depth_buckets = 10

    def parse_file(self, file_name):
        with open(file_name, 'r') as input_file:
            data = input_file.read()
        return json.loads(data)


    def parse_folder(self, folder):
        results = {}
        for strategy_name in os.listdir(folder):
            if os.path.isdir(folder+'/'+ strategy_name):
                results[strategy_name] = {}
                for file_name in os.listdir(folder+'/'+ strategy_name):
                    results[strategy_name][file_name] = self.parse_file(folder+'/'+ strategy_name + '/'+ file_name)
        return results


    def make_csv_status(self, all_results):
        all_statuses = [defs.FLIPPED_STRING, defs.NOT_TRIED_STRING, defs.MISSED_ALL_STRING, defs.WRONG_STATUS_STRING, defs.MAXIMUM_INPUT_STRING, defs.MAXIMUM_EXECUTION_TIME_STRING]
        csv = "Strategy," + ",".join(all_statuses) + "\n"
        for strategy in all_results:
            status_results = all_results[strategy]['status']
            csv += strategy + ","
            for status in all_statuses:
                if status in status_results:
                    number_of_results = status_results[status]
                else:
                    number_of_results = 0
                csv += str(number_of_results)+","
            csv = csv[:-1] #remove trailing ,
            csv += "\n"
            comment_results = all_results[strategy]['comments']
            for substrategy in comment_results:
                csv += substrategy + ',' +str(comment_results[substrategy]) +','
                csv += "0,"*(len(all_statuses)-1)
                csv = csv[:-1] #remove trailing ,
                csv += "\n"
        with open(self.output_dir + 'status.csv', 'w') as output:
            output.write(csv)




    def make_csv_depth(self, all_results, max_depth):
        bucket_size = max_depth/self.depth_buckets
        csv = "Strategy,"+ ",".join([str(i*bucket_size)+ '-' + str((i+1)*bucket_size) for i in range(self.depth_buckets)])  + "\n"
        for strategy in all_results:
            csv += strategy +","
            for bucket in range(self.depth_buckets):
                if bucket in all_results[strategy]['depth']:
                    number_of_flips = all_results[strategy]['depth'][bucket]
                else:
                    number_of_flips = 0
                csv += str(number_of_flips) + ","
            csv = csv[:-1]
            csv += "\n"
        with open(self.output_dir + 'depth.csv', 'w') as output:
            output.write(csv)
                


    def make_csv_offsets(self, all_results, total_offsets):
        csv = "Strategy,"+ ",".join([str(i) for i in total_offsets])  + "\n"
        csv += "Total," + ",".join([str(total_offsets[i]) for i in total_offsets]) + "\n"
        for strategy in all_results:
            offsets = all_results[strategy]['offsets']
            csv += strategy + ',' + ",".join([str(offsets[i]) for i in total_offsets])
            csv += "\n"
        with open(self.output_dir + 'offsets.csv', 'w') as output:
            output.write(csv)
            

    def make_csv(self, all_results, max_depth, total_offsets):
        self.make_csv_status(all_results)
        self.make_csv_depth(all_results, max_depth)
        self.make_csv_offsets(all_results, total_offsets)

    def process_results(self, results: dict):
        first_time = True
        total_offsets = {}
        total_results = {}
        max_depth = 0

        #Make sure we start with the magic byte strategy, we added the offset parameter later, but this is a global statistic
        strategy_names = list(results.keys())
        offset_logged_for_strategy = 'OneByteStrategy'
        if offset_logged_for_strategy in strategy_names:
            strategy_names.insert(0,strategy_names.pop(strategy_names.index(offset_logged_for_strategy)))
        for strategy_name in strategy_names:
            status_results = {}
            status_results_comment = {}
            status_results_depth = {}
            if first_time:
                #max depth should be the same for every strategy, since they have the same conditions
                max_depth = float(max([results[strategy_name][cmp_id]['depth'] for cmp_id in results[strategy_name]]))
            depth_bucket_size = 100./self.depth_buckets
            status_results_offsets = {}
            for cmp_id in results[strategy_name]:   
                self.all_condition_ids.add(cmp_id)
                #add substrategy
                status = results[strategy_name][cmp_id]['status']
                if 'comment' in results[strategy_name][cmp_id] and status == defs.FLIPPED_STRING:
                    comment = results[strategy_name][cmp_id]['comment']
                    if comment not in status_results_comment:
                        status_results_comment[comment] = 0
                    status_results_comment[comment] += 1
                
                #add status
                if results[strategy_name][cmp_id]['nrOfInputs'] == 0:
                    status = defs.NOT_TRIED_STRING
                elif results[strategy_name][cmp_id]['nrOfInputs'] == results[strategy_name][cmp_id]['nrOfMisses']:
                    status = defs.MISSED_ALL_STRING
                if status not in status_results:
                    status_results[status] = 0
                status_results[status] +=1
                if status == defs.FLIPPED_STRING:
                    self.flipped_condition_ids.add(cmp_id)


                #add depth where we flipped the condition
                if max_depth != 0:
                    percentage = results[offset_logged_for_strategy][cmp_id]['depth']*100/max_depth
                    bucket_index = int(percentage/depth_bucket_size)
                    if bucket_index == self.depth_buckets:
                        #this was the max depth
                        bucket_index -= 1
                    if bucket_index not in status_results_depth:
                        status_results_depth[bucket_index] = 0
                    if status == defs.FLIPPED_STRING:
                        status_results_depth[bucket_index] += 1
                
                #add number of offsets where we flipped the conditions
                nr_of_offsets = len(results[offset_logged_for_strategy][cmp_id]['offsets'])
                if nr_of_offsets not in status_results_offsets:
                    status_results_offsets[nr_of_offsets] = 0
                    if first_time:
                        total_offsets[nr_of_offsets] = 0

                if first_time:
                    #collect the total offsets in the trace, should be the same for all strategies
                    total_offsets[nr_of_offsets] += 1
                if status == defs.FLIPPED_STRING:
                    status_results_offsets[nr_of_offsets] += 1
            
            total_results[strategy_name] = {
                'status' : status_results,
                'comments': status_results_comment,
                'depth': status_results_depth,
                'offsets': status_results_offsets
            }
            print("Status for strategy %s:" % strategy_name)
            total_status_results = sum(status_results.values())
            for status in status_results:
                print("%s\t %d\t %d %%" % (status.ljust(40), status_results[status], status_results[status]/total_status_results*100))
            total_comments = sum(status_results_comment.values())
            if total_comments > 0:
                print("\nSubstrategies:")
                for comment in status_results_comment:
                    print("%s\t %d\t %d %%" % (comment.ljust(40), status_results_comment[comment], status_results_comment[comment]/total_comments*100))
            print("\n")
            first_time = False
        print("Unique conditions:\t%d\nFlipped conditions:\t%d" % (len(self.all_condition_ids), len(self.flipped_condition_ids)))
        self.make_csv(total_results, max_depth, total_offsets)

    def parse(self, input_folder, output_folder):
        if output_folder:
            self.output_dir
        result = self.parse_folder(input_folder)
        self.process_results(result)

def main(argv):
    input_dir = None
    output_dir= None
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","input=", "output="])
    except getopt.GetoptError:
        print('output_parser.py -i <input_folder> -o <output_folder>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('output_parser.py -i <input_folder>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input_dir = arg
        elif opt in ("-o", "--output"):
            output_dir = arg
    if not input_dir:
        print('output_parser.py -i <input_folder>')
        sys.exit()
    p = Parser()
    p.parse(input_dir, output_dir)

if __name__ == "__main__":
   main(sys.argv[1:])
