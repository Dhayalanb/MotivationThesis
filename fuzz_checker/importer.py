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

    def filterTraces(self, traces: list):
        found_conditions = set()
        for trace in traces:
            for condition in trace.conditions:
                uniqueId = condition.base.getLogId()
                if uniqueId in found_conditions:
                    condition.skipping = True
                else:
                    found_conditions.add(uniqueId)
        #print(json.dumps(traces, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else json.JSONEncoder.default(self,o) if not isinstance(o,bytes) else str(base64.encodebytes(o))))
        return traces

    def get_file_contents(self):
        files = self.get_files()
        response = []
        for (input_file, trace_file) in files:
            response.append(Trace(self.read_input_file(input_file), self.read_fuzz_file(trace_file)))
        return self.filterTraces(response)
