import logging
import os
import sys
import traceback
import argparse
from signal import signal, SIGINT
import logger_template

def main():
    logging.info("Starting test app")
    # Tell Python to run the handler() function when SIGINT is recieved
    signal(SIGINT, Signalhandler)

    parser = argparse.ArgumentParser()
    parser.add_argument("--one-arg", help="one")
    parser.add_argument("--two-arg", help="two")
    args = parser.parse_args()

    # args check
    if not len(sys.argv) > 1:
        parser.print_help()
        os._exit(0)
    
    # setup logging
    defaultPath = logger_template.LogCollector().GetDefaultAbsLogFileName()
    logger_template.LogCollector().setup_logging(log_file=defaultPath)
    
    
    
    if args.one_arg:
        print("")
    if args.two_arg:
        print("")
            
    # Do cleanup
    Cleanup()
    os._exit(0)

def Cleanup():
    print("")

def Signalhandler(signal_received, frame):
    # Handle any cleanup here
    Cleanup()
    logging.warning('SIGINT or CTRL-C detected. Exiting gracefully')
    os._exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical("Unhandled exception occurred")
        logging.critical("Exception info: {}".format(traceback.format_exc()))
        logging.critical("Please report this to Virsec")
        os._exit(1)