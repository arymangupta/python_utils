import os
import json
import logging
import threading
import traceback
from typing import Any, Dict, List, Optional, Tuple

from vIPC_core import vIPCCore
from vsp_msg_enums import vmsg_enums
from vsp_defines import VSPComponent, VspKeys

req_msg_header_keys = ["sourceVSPComp", "msgType", "msgTxnID", "feedbackReq"]


class vIPC(vIPCCore):

    # vIPC stats
    __stats = {
        "rx_msg": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of messages received",
        },
        "rx_msg_fail": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of vIPC_read() errors",
        },
        "rx_msg_inv": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of invalid JSON messages received",
        },
        "rx_msg_succ": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of messages processed successfully",
        },
        "tx_hb_succ": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of heartbeat messages sent successfully to {}".format(
                VSPComponent.vmgr
            ),
        },
        "tx_hb_fail": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of heartbeat messages that were not sent successfully to {}".format(
                VSPComponent.vmgr
            ),
        },
        "tx_msg_succ": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of messages sent successfully",
        },
        "tx_msg_fail": {
            "vs_enum": -1,
            "protected": False,
            "desc": "Number of messages that were not sent successfully",
        },
    }

    def __init__(self, configs: dict, vsp_stats_inst):
        logging.debug("Initializing vIPC class")

        self._stop = threading.Event()
        self._msg_txn_id = 1
        self._msg_txn_id_lock = threading.Lock()

        self.configs = configs
        self.vsp_stats = vsp_stats_inst

        self._init_stats()

        try:
            super(vIPC, self).__init__(
                self.configs[VspKeys.CFG_VIPC_LIB_PATH],
                self.configs[VspKeys.CFG_VIPC_MAX_MSG_SIZE],
                self.configs[VspKeys.CFG_VIPC_READ_TIMEOUT],
            )
        except:
            logging.error(
                f"Failed to initialize vIPCCore class with exception: {traceback.format_exc()}"
            )
            return None

        logging.info("Initialized vIPC class")

    def _get_msg_txn_id(self) -> int:
        with self._msg_txn_id_lock:
            t = self._msg_txn_id
            self._msg_txn_id += 1
        return t

    def _init_stats(self):
        for k, v in self.__stats.items():
            if v["vs_enum"] == -1:
                v["vs_enum"] = self.vsp_stats.register_stat(
                    "vIPC_comms", v["desc"], v["protected"]
                )

    def _verify_msg(
        self, msg: Dict[str, Any], ack_msgs: List[Any]
    ) -> Tuple[int, str, int]:
        rval = 0
        src_comp = ""
        txn_id = -1
        if not all(k in msg for k in req_msg_header_keys):
            rval = -1
            self.vsp_stats.inc_stat(self.__stats["rx_msg_inv"]["vs_enum"])
            logging.debug(
                f"Incoming message {msg} does not have required msg headers; Missing keys: {[k for k in req_msg_header_keys if k not in msg]}"
            )
            ack_msgs.append(
                {
                    "error": f"message is missing required msg header fields: {[k for k in req_msg_header_keys if k not in msg]}"
                }
            )
        elif msg.get("msgType", -1) not in [
            v for k, v in vmsg_enums[VSPComponent.vweb_assist].items()
        ]:
            rval = -1
            self.vsp_stats.inc_stat(self.__stats["rx_msg_inv"]["vs_enum"])
            logging.debug(
                f"Incoming message {msg} has an unsupported {VSPComponent.vweb_assist} msg type"
            )
            ack_msgs.append(
                {"error": f"Invalid message type {msg.get('msgType', None)}"}
            )

        if msg.get("feedbackReq", 0) and all(
            k in msg for k in ["sourceVSPComp", "msgTxnID", "feedbackReq"]
        ):
            src_comp = msg["sourceVSPComp"]
            txn_id = msg["msgTxnID"]
        return rval, src_comp, txn_id

    def get_msg(self) -> Dict[str, Any]:
        msg = None
        while msg is None and not self._stop.is_set():
            try:
                rval, vIPC_src_id, msg = super().get_msg()
            except Exception as e:
                self.vsp_stats.inc_stat(self.__stats["rx_msg_fail"]["vs_enum"])
                logging.debug(
                    f"Exception occurred while getting vIPC message: {traceback.format_exc()}"
                )
                continue

            if msg:
                self.vsp_stats.inc_stat(self.__stats["rx_msg"]["vs_enum"])
                if not VSPComponent.is_valid_vIPC_id(vIPC_src_id):
                    msg = None
                    self.vsp_stats.inc_stat(self.__stats["rx_msg_inv"]["vs_enum"])
                    logging.warning(
                        f"{VSPComponent.vweb_assist} received msg from unknown VSP component (vIPC id {vIPC_src_id}); ignoring"
                    )
                    continue

                src = VSPComponent.get_vsp_name(vIPC_src_id)
                try:
                    msg = json.loads(msg)
                except json.JSONDecodeError as err_msg:
                    msg = None
                    self.vsp_stats.inc_stat(self.__stats["rx_msg_inv"]["vs_enum"])
                    logging.warning(
                        f"{VSPComponent.vweb_assist} received malformed json from {src}; ignoring"
                    )
                    logging.debug(f"Malformed json msg: {msg}")
                    continue

                # Do some message verification
                ack_msgs = []
                rval, src_comp, txn_id = self._verify_msg(msg, ack_msgs)
                if rval:
                    if src_comp:
                        self.send_vsp_feedback(
                            src_comp, txn_id, vmsg_enums["vspAck"]["INVALID"], ack_msgs
                        )
                    continue
                else:
                    # Return message
                    break
            elif rval != 1:
                self.vsp_stats.inc_stat(self.__stats["rx_msg_fail"]["vs_enum"])

        return msg

    def register(self) -> int:
        try:
            rval = super().register(VSPComponent.get_vIPC_id(VSPComponent.vweb_assist))
        except:
            logging.error(
                f"{VSPComponent.vweb_assist} failed to register with {VSPComponent.vIPC_server}"
            )
            logging.debug(f"Exception info: {traceback.format_exc()}")
            rval = -1

        if not rval:
            logging.info(
                f"{VSPComponent.vweb_assist} successfully registered with {VSPComponent.vIPC_server}"
            )
        return rval

    def send_hb(self, health_status: int) -> int:
        rval = super().send_hb(health_status)
        if rval == 0:
            self.vsp_stats.inc_stat(self.__stats["tx_hb_succ"]["vs_enum"])
        else:
            self.vsp_stats.inc_stat(self.__stats["tx_hb_fail"]["vs_enum"])

        return rval

    def send_msg(self, target_comp: str, msg: Dict[str, Any]) -> int:

        target_comp = target_comp.upper()
        if not VSPComponent.is_member(target_comp):
            self.vsp_stats.inc_stat(self.__stats["tx_msg_fail"]["vs_enum"])
            return -1

        rval = -1
        target_vIPC_id = VSPComponent.get_vIPC_id(target_comp)
        if msg.get("msgTxnID", None) is None:
            msg["msgTxnID"] = self._get_msg_txn_id()

        try:
            rval = super().send_msg(target_vIPC_id, json.dumps(msg))
        except:
            self.vsp_stats.inc_stat(self.__stats["tx_msg_fail"]["vs_enum"])

        return rval

    def send_vsp_feedback(
        self,
        target_comp: str,
        msg_txn_id: int,
        ack_status: int,
        ack_msgs: dict = {},
    ) -> int:
        resp_msg = dict({
            "version": "v1.0",
            "sourceVSPComp": VSPComponent.vweb_assist,
            "targetVSPComp": target_comp,
            "msgType": vmsg_enums["coreMsgType"]["ACKNOWLEDGE"],
            "msgTxnID": msg_txn_id,
            "feedbackReq": 0,
            "response": ack_status,
        })

        if ack_msgs is not None:
            resp_msg = {** resp_msg, **ack_msgs}
            logging.debug("final feedback message is %s" % resp_msg)

        rval = self.send_msg(target_comp, resp_msg)
        if not rval:
            logging.info("Feedback msg sent to {}".format(target_comp))
        else:
            logging.error("Failed to send feedback msg to {}".format(target_comp))

        return rval