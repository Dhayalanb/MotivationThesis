from strategies.strategy import Strategy
from trace import Trace
from cond_stmt import CondStmt
import os, subprocess, defs, logging

class ConcolicStrategy(Strategy):
    

    def run_concolic(self, cur_input: bytes, condition: CondStmt, id):
        new_env = os.environ.copy()
        new_env['SYMCC_INPUT_FILE'] = defs.CONCOLIC_TMP_FOLDER + 'input_' + id
        new_env['SYMCC_OUTPUT_DIR'] = defs.CONCOLIC_TMP_FOLDER + 'output_' + id + '/'
        if not os.path.exists(new_env['SYMCC_OUTPUT_DIR']):
            os.mkdir(new_env['SYMCC_OUTPUT_DIR'])
        with open(new_env['SYMCC_INPUT_FILE'], 'wb') as input_file:
            input_file.write(cur_input)
        if len(condition.offsets) > 0:
            symbolic_bytes = list(set([byte for o in condition.offsets for byte in range(o['begin'], o['end'])]))
            new_env['SYMCC_SYMBOLIC_BYTES'] = ",".join(map(str,symbolic_bytes))
            logging.info(new_env['SYMCC_SYMBOLIC_BYTES'])
        arguments = [defs.CONCOLIC_BINARY] + [new_env['SYMCC_INPUT_FILE'] if arg == '@@' else arg for arg in defs.ARGUMENTS ]
        client = subprocess.Popen(arguments, env=new_env, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            preexec_fn=limit_virtual_memory
        )
        try:
            result = client.wait(defs.MAXIMUM_CONCOLIC_EXECUTION_TIME)
        except subprocess.TimeoutExpired as e:
            client.kill()
            raise e

    def remove_old_files(self, id):
        for old_file in os.listdir(defs.CONCOLIC_TMP_FOLDER + 'output_'+id + '/'):
            if os.path.isfile(defs.CONCOLIC_TMP_FOLDER + 'output_'+id + '/' + old_file):
                os.remove(defs.CONCOLIC_TMP_FOLDER + 'output_'+id + '/' + old_file)
        if os.path.isfile(defs.CONCOLIC_TMP_FOLDER + 'input_' + id):
            os.remove(defs.CONCOLIC_TMP_FOLDER + 'input_' + id)


    def search(self, trace: Trace, index:int):
        cur_input = trace.getInput()
        condition = trace.getCondition(index)
        id = str(self.handler.id)
        try:
            self.run_concolic(cur_input, condition, id)
        except subprocess.TimeoutExpired:
            #executed for maximum time
            logging.info("Timeout")
            pass
        concolic_files = os.listdir(defs.CONCOLIC_TMP_FOLDER + 'output_'+id + '/')
        logging.info("Generated: %d new inputs" % len(concolic_files))
        concolic_files.reverse()
        try:
            for new_input_file in concolic_files:
                if os.path.isfile(defs.CONCOLIC_TMP_FOLDER + 'output_'+id + '/' + new_input_file):
                    with open(defs.CONCOLIC_TMP_FOLDER + 'output_'+id + '/' + new_input_file, 'rb') as new_input:
                        self.handler.run(condition, new_input.read())
            self.handler.wrong(defs.COMMENT_TRIED_EVERYTHING)
        finally:
            #perform cleanup when done
            self.remove_old_files(id)
        return None

def limit_virtual_memory():
    # The tuple below is of the form (soft limit, hard limit). Limit only
    # the soft part so that the limit can be increased later (setting also
    # the hard limit would prevent that).
    # When the limit cannot be changed, setrlimit() raises ValueError.
    resource.setrlimit(resource.RLIMIT_AS, (defs.MAX_VIRTUAL_MEMORY, defs.MAX_VIRTUAL_MEMORY))
