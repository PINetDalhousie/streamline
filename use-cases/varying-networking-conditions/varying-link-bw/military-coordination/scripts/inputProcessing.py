# sample command to run: python3 use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/inputProcessing.py --link-bw 20 --msg-rate 75

#!/usr/bin/python3

import argparse

def configureInput(linkBW):
    inputFile = open("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/input-10Mbps.graphml", "r")
    inputProperties = inputFile.read()

    inputProperties = inputProperties.replace('<data key=\"bw\">10</data>', '<data key=\"bw\">'+str(linkBW)+'</data>')
    
    # write to a new file
    outputFile = open("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/input.graphml", "w")
    outputFile.write(inputProperties)
    outputFile.close()

    inputFile.close()

def configureProducerInput(mRate):
    prodInFile = open("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/military-data-producer-original.py", "r")
    prodProperties = prodInFile.read()
    
    # update producer file with new message rate
    prodProperties = prodProperties.replace('mRate = 30', 'mRate = '+str(mRate))
    prodOutFile = open("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/military-data-producer.py", "w")
    prodOutFile.write(prodProperties)
    prodOutFile.close()

    prodInFile.close()

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Script for plotting varying msg-rate.')
    parser.add_argument('--link-bw', dest='linkBW', type=int, help='link bandwidth')
    parser.add_argument('--msg-rate', dest='mRate', type=int, help='message rate')
    args = parser.parse_args()
    linkBW = args.linkBW
    mRate = args.mRate

    configureInput(linkBW)
    configureProducerInput(mRate)

