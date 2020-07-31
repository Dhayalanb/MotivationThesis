import json
import os
from cond_stmt import CondStmt
from trace import Trace
import base64

class Importer:
    INPUT_NAME = "id_"

    def __init__(self, folder):
        self.folder = folder

    def get_files(self):
        files =  os.listdir(self.folder)
        response = []
        for input_file in files:
            if input_file[:len(self.INPUT_NAME)] == self.INPUT_NAME:
                input_id = input_file[len(self.INPUT_NAME):]
                response.append((input_file, "track_id_"+input_id+".json"))
        return response

    def read_input_file(self, fileLocation):
        content = None
        with open(self.folder+fileLocation, 'rb') as input_file:
            content = input_file.read()
        return content

    def read_fuzz_file(self, fileLocation):
        content = None
        with open(self.folder+fileLocation, 'r') as input_file:
            content = input_file.read()
        jsonData = json.loads(content)
        response = []
        for item in jsonData:
            response.append(CondStmt.fromJson(item))
        return response

    def filterTraces(self, trace: Trace, found_conditions: set):
        depth = 0
        for condition in trace.conditions:
            condition.depth = depth
            uniqueId = condition.base.getLogId()
            if uniqueId in found_conditions:
                condition.skipping = True
                del trace.conditions[depth]
            else:
                found_conditions.add(uniqueId)
            depth += 1
        #print(json.dumps(traces, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else json.JSONEncoder.default(self,o) if not isinstance(o,bytes) else str(base64.encodebytes(o))))
        return trace

    def get_file_contents(self):
        files = self.get_files()
        response = []
        total_files = len(files)
        number_of_files = 1
        found_conditions = set()
        for (input_file, trace_file) in files:
            trace = Trace(self.read_input_file(input_file), self.read_fuzz_file(trace_file))
            response.append(self.filterTraces(trace, found_conditions))
            print("Processed %d/%d files" % (number_of_files, total_files))
            number_of_files +=1
        print("Found %d unique conditions" % (len(found_conditions)))
        return response
