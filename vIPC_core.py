import os
import logging
import threading
import traceback
from ctypes import *
from typing import Optional, Tuple


class vIPCCore:
    def __init__(
        self, vIPC_lib_path: str, max_msg_size: int, timeout: Optional[int] = 0
    ):
        logging.debug("Initializing vIPC core class")
        self._initialized = False

        self._timeout = timeout
        self._max_msg_sz = max_msg_size
        self._vIPC_client_lib_path = vIPC_lib_path
        self._config_lock = threading.Lock()

        self._vIPC_lib = None

        logging.debug(f"Max read-in msg size set to {self._max_msg_sz}")
        logging.info("vIPC core class initialized")

    def register(self, vIPC_id: int) -> int:
        if self._initialized:
            # Already initialized
            return 0

        self._initialized = False

        try:
            self._vIPC_lib = cdll.LoadLibrary(self._vIPC_client_lib_path)
        except Exception as e:
            logging.error(
                f"LoadLibrary for {self._vIPC_client_lib_path} raised exception: {e}"
            )
            return None

        if not self._vIPC_lib:
            logging.error(
                "Cannot initialize vIPC comms since vIPC client library was not loaded"
            )
            return -1

        try:
            rval = self._vIPC_lib.vIPC_init(c_uint(vIPC_id), c_uint(self._max_msg_sz))
        except Exception as e:
            logging.error(f"vIPC init({vIPC_id}, {self._max_msg_sz}) failed")
            logging.error(f"Exception info: {e}")
            return -1

        if rval:
            logging.error(f"Registration with the vIPC-server failed; rval = {rval}")
            return -1
        self._initialized = True
        logging.info("Successfully initialized comms with vIPC-server")
        return 0

    def get_msg(self, retry: Optional[bool] = False) -> Tuple[int, int, str]:

        if not self._initialized:
            return -1, -1, ""

        out_msg = create_string_buffer(self._max_msg_sz)
        out_msg_len = c_int(self._max_msg_sz)
        vIPC_src = c_uint(0)
        timeout_in_ms = c_uint(self._timeout)
        retry_flag = c_bool(retry)

        try:
            rval = self._vIPC_lib.vIPC_read(
                byref(vIPC_src),
                byref(out_msg),
                byref(out_msg_len),
                timeout_in_ms,
                retry_flag,
            )
        except:
            # Exception occurred -- just return error
            return -1, -1, ""

        if rval:
            return rval, -1, ""

        return rval, vIPC_src.value, out_msg.value.decode("utf-8")

    def send_hb(self, health_status: int) -> int:

        try:
            rval = self._vIPC_lib.vIPC_send_health_msg(c_uint(health_status))
        except:
            return -1

        return rval

    def send_msg(self, target_vIPC_id: int, msg: str) -> int:

        if not msg or not self._initialized:
            return -1

        ctarget = c_uint(target_vIPC_id)
        cmsg = create_string_buffer(msg.encode("utf-8"))
        cmsg_len = len(msg.encode("utf-8"))

        try:
            rval = self._vIPC_lib.vIPC_send(ctarget, byref(cmsg), cmsg_len)
        except:
            return -1

        return rval

    def close(self) -> None:
        try:
            self._vIPC_lib.close()
        except:
            # Failed to close comms
            pass
        else:
            self._initialized = False
