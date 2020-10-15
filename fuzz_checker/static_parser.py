import defs, os

class StaticMetric:

    #self.modid = self.basic_block = self.cmpid = self.cyclomatic = self.oviedo = self.chain_size = self.compare_size = self.compares_constant = self.compares_pointer = self.is_equality = self.is_contant = self.cases = None

    def __init__(self, modid, content):
        self.modid = modid
        items = content.split(",")
        self.basic_block = items[0]
        self.cmpid = items[1]
        self.cyclomatic = items[2]
        self.oviedo = items[3]
        self.chain_size = items[4]
        self.compare_size = items[5]
        self.compares_constant = items[6]
        self.compares_pointer = items[7]
        self.is_equality = items[8]
        self.is_contant = items[9]
        self.cases = items[10]

class StaticParser:
    
    @staticmethod
    def parse_analysis_files(folder):
        cmpids = {}
        for analysis_file in os.listdir(folder) :
            if analysis_file.startswith("static_analysis_results"):
                found_cmpids = StaticParser.parse_analysis_file(folder, analysis_file)
                cmpids = {**cmpids, **found_cmpids}
        return cmpids

    @staticmethod
    def parse_analysis_file(folder, filename):
        output = {}
        modid = filename.split(".")[1]
        with open(folder + filename, "r") as analysis_file:
            content = analysis_file.read()
            for line in content.split("\n")[1:]:
                if len(line) == 0:
                    continue
                static_metric = StaticMetric(modid, line)
                output[static_metric.cmpid] = static_metric
        return output

test = StaticParser.parse_analysis_files("../test/mini/")