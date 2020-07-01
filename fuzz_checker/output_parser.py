import os, json

class Parser:

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
                    
    def process_results(self,results):
        for strategy_name in results:
            status_results = {}
            for cmp_id in results[strategy_name]:
                status = results[strategy_name][cmp_id]['status']
                if status not in status_results:
                    status_results[status] = 1
                else:
                    status_results[status] +=1
            print("Status for strategy %s:" % strategy_name)
            total_results = sum(status_results.values())
            for status in status_results:
                print("%s\t %d\t %d %%" % (status.ljust(40), status_results[status], status_results[status]/total_results*100))
            print("\n")

    def parse(self, output_folder):
        result = self.parse_folder(output_folder)
        self.process_results(result)

p = Parser()
p.parse('../output')