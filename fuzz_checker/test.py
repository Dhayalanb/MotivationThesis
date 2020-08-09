from forksrv import ForkSrv
from cond_stmt_base import CondStmtBase
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
    condition = CondStmtBase.fromJson({"cmpid":3021181229,"context":257903,"order":65538,"belong":0,"condition":0,"level":0,"op":32771,"size":8,"lb1":0,"lb2":1,"arg1":93990559884295,"arg2":93990559884295})
    server = ForkSrv()
    server.listen(0)
    server.run_with_condition(condition, bytes('''<definitions name = "HelloService"
   targetNamespace = "http://www.examples.com/wsdl/HelloService.wsdl"
   xmlns = "http://schemas.xmlsoap.org/wsdl/"
   xmlns:soap = "http://schemas.xmlsoap.org/wsdl/soap/"
   xmlns:tns = "http://www.examples.com/wsdl/HelloService.wsdl"
   xmlns:xsd = "http://www.w3.org/2001/XMLSchema">
 
   <message name = "SayHelloRequest">
      <part name = "firstName" type = "xsd:string"/>
   </message>
	
   <message name = "SayHelloResponse">
      <part name = "greeting" type = "xsd:string"/>
   </message>

   <portType name = "Hello_PortType">
      <operation name = "sayHello">
         <input message = "tns:SayHelloRequest"/>
         <output message = "tns:SayHelloResponse"/>
      </operation>
   </portType>

   <binding name = "Hello_Binding" type = "tns:Hello_PortType">
      <soap:binding style = "rpc"
         transport = "http://schemas.xmlsoap.org/soap/http"/>
      <operation name = "sayHello">
         <soap:operation soapAction = "sayHello"/>
         <input>
            <soap:body
               encodingStyle = "http://schemas.xmlsoap.org/soap/encoding/"
               namespace = "urn:examples:helloservice"
               use = "encoded"/>
         </input>
		
         <output>
            <soap:body
               encodingStyle = "http://schemas.xmlsoap.org/soap/encoding/"
               namespace = "urn:examples:helloservice"
               use = "encoded"/>
         </output>
      </operation>
   </binding>

   <service name = "Hello_Service">
      <documentation>WSDL File for HelloService</documentation>
      <port binding = "tns:Hello_Binding" name = "Hello_Port">
         <soap:address
            location = "http://www.examples.com/SayHello/" />
      </port>
   </service>
</definitions>
'''))
    server.close()

if __name__ == "__main__":
   main(sys.argv[1:])