from concurrent.futures import thread
import time, logging, traceback, threading, messagebuilder, msgprocessor
from typing import Any, Dict
from collections import defaultdict
from vIPC import vIPC
from vsp_msg_enums import *
from vsp_defines import VSPComponent, VspKeys
import vsputils

class Manager:
    """  Manager starts the vipc comms threads to process messages sent by vsp-manager """

    def __init__(self, configs: Dict[(Any, Any)], vipc_inst: vIPC):
        logging.info('Initializing manager')
        self._vIPC = None
        self._stop = threading.Event()
        self._health = 0
        self._locks = {}
        self._handles = {}
        self.gobjects = {}
        self._msg_callbacks = defaultdict(list)
        self.configs = configs
        self._vIPC = vipc_inst
        self.retryCount = self.configs[VspKeys.CFG_VIPC_INIT_RETRY]
        self.sleepTimeout = self.configs[VspKeys.CFG_VIPC_INIT_RETRY_TIMEOUT]

    def _hb_thread(self):
        logging.info(f"Starting {VSPComponent.vweb_assist} HB thread")
        while not self._stop.is_set():
            try:
                with self._locks['_health']:
                    h = self._health
                self._vIPC.send_hb(h)
            except:
                pass
            else:
                time.sleep(self.configs[VspKeys.CFG_HB_FREQ] / 1000)

        logging.critical(f"{VSPComponent.vweb_assist} HB thread has exited")

    def _process_internal_msg(self, msg):
        msg_type = msg['msgType']
        feedback_required = msg['feedbackReq']
        vsp_src = msg['sourceVSPComp']
        vsp_ack = vmsg_enums['vspAck']['SUCCESSFUL']
        logging.info(f"Processing {msg}")
        count, feedBack = vsputils.ProcessInputJsonMessage(jsonDict=msg)
        if count < 0:
            vsp_ack = vmsg_enums['vspAck']['UNSUCCESSFUL']
        logging.info(f"Processed {count} messages")
        if feedback_required:
            self._vIPC.send_vsp_feedback(msg.get('sourceVSPComp'), msg.get('msgTxnID'), vsp_ack, feedBack)

    def _vIPC_rx_thread(self):
        logging.info(f"Starting {VSPComponent.vweb_assist} vIPC RX thread")
        while True: #not self._stop.is_set():
            try:
                msg = self._vIPC.get_msg()
            except:
                pass
            else:
                try:
                    if bool(msg) is not False:
                        self._process_internal_msg(msg)
                except:
                    logging.warning(f"Exception occured while processing vIPC msg: {traceback.format_exc()}")

        logging.critical(f"{VSPComponent.vweb_assist} vIPC RX thread has exited")

    def initialize_manager(self):
        for x in range(self.retryCount):
            try:
                rval = self._vIPC.register()
            except:
                logging.error(f"Exception occurred while registering with {VSPComponent.vIPC_server}: {traceback.format_exc()}")
            else:
                if rval:
                    logging.error(f"Registration with {VSPComponent.vIPC_server} failed with rval = {rval}")
                    if x == self.retryCount - 1:
                        return rval
                    time.sleep(self.sleepTimeout / 1000)
                else:
                    break
                
        # Initialize health
        self._health = vmsg_enums.get('healthStatus', {}).get('INITIALIZING', 6)
        self._locks['_health'] = threading.Lock()
        
         # Start the internal VSP heartbeats
        self._handles['hb'] = threading.Thread(target=(self._hb_thread))
        self._handles['hb'].start()
        
        # Initialize vIPC read thread
        #self._handles['vIPC_rx'] = threading.Thread(target=(self._vIPC_rx_thread))
        
        # Create reference to manager
        self.gobjects['manager'] = self

    def run(self):
        self._vIPC_rx_thread()
        #self._handles['vIPC_rx'].start()
        #self._handles['vIPC_rx'].join()

    def stop(self):
        self._stop.set()
        self.shutdown()

    def shutdown(self):
        logging.warning(f"Shutting down {VSPComponent.vweb_assist}")

    def update_health(self, health_status):
        with self._locks['_health']:
            self._health = health_status