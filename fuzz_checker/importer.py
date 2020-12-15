import json
import os
from cond_stmt import CondStmt
from trace import Trace
import base64

class Importer:
    INPUT_NAME = "id_"
    found_conditions = set()
    files = None

    def __init__(self, folder):
        self.folder = folder
        self.files = self.get_files()

    def get_files(self):
        files =  os.listdir(self.folder)
        files.sort()
        response = []
        for input_file in files:
            if input_file[:len(self.INPUT_NAME)] == self.INPUT_NAME:
                input_id = input_file[len(self.INPUT_NAME):]
                response.append((input_file, "track_id_"+input_id+".json"))
        return response


    def get_reachableness(self, offsets, reachableness):
        temp = []
        for offset in offsets:
            begin_index = offset['begin']
            end_index = offset['end']
            temp += reachableness[begin_index:end_index]
        return sum(temp)

    def update_reachableness(self, offsets, reachableness):
        for offset in offsets:
            begin_index = offset['begin']
            end_index = offset['end']
            if len(reachableness) < end_index:
                reachableness += [0 for i in range(end_index-len(reachableness))]
            for i in range(begin_index, end_index):
                reachableness[i] += 1
        return reachableness

    def read_input_file(self, fileLocation):
        content = None
        with open(self.folder+fileLocation, 'rb') as input_file:
            content = input_file.read()
        return content

    def read_fuzz_file(self, fileLocation):
        content = None
        reachableness = []
        with open(self.folder+fileLocation, 'r') as input_file:
            content = input_file.read()
        jsonData = json.loads(content)
        response = []
        depth = 0
        for item in jsonData:
            item['depth'] = depth
            depth += 1
            condition = CondStmt.fromJson(item)
            reachableness = self.update_reachableness(condition.offsets, reachableness)
            condition.reachableness = self.get_reachableness(condition.offsets, reachableness)
            response.append(condition)
        return response

    def get_traces_iterator(self):
        #Processing hangs can take up to a week per trace, skip those
        hang_files = os.listdir(self.folder+'/../hangs')
        hangs = list()
        print("Collecting hangs")
        for hang_file in hang_files:
            with open(self.folder+'/../hangs/'+hang_file,'rb') as hang:
                hangs.append(hang.read())
        print("Collected hangs")
        number_of_files = 1
        total_files = len(self.files)
        for (input_file, trace_file) in self.files:
            try:
                trace_content = self.read_fuzz_file(trace_file)
            except:
                pass
            if not trace_content or not len(trace_content):
                print("Skipped %d/%d files due to empty trace" % (number_of_files, total_files))
                number_of_files +=1
                continue
            trace = Trace(self.read_input_file(input_file), trace_content)
            if trace.getInput() in hangs:
                print("Skipped %d/%d files" % (number_of_files, total_files))
                number_of_files +=1
                continue
            print("Processed %d/%d files" % (number_of_files, total_files))
            number_of_files +=1
            yield trace

    def get_traces_length(self):
        return len(self.files)
