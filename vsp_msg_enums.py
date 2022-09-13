import os
import json
import logging
from collections import defaultdict


vmsg_enums = defaultdict(dict)
CONFIG_MSG_TYPE = 1
PROV_START_JOB = 6
vmsg_types = {'VSP-WEB-ASSIST': {'RESERVED0':0,  'CONFIG':1, 
                    'PROCESS_CONTROL':2, 
                    'ACKNOWLEDGE':3, 
                    'CLEAR_STATS':4, 
                    'INTERNAL_STATE':5, 
                    'PROV_START_JOB':6, 
                    'PROV_STOP_JOB':7, 
                    'KAFKA_INFO':8, 
                    'CUSTOM_RESPONSE':9}}


def init_vsp_msg_enums(vsp_msg_enum_path):
    if not os.path.exists(vsp_msg_enum_path):
        return -1

    with open(vsp_msg_enum_path) as f:
        try:
            vsp_msg_enums = json.load(f)
        except Exception as e:
            logging.debug("Failed to load {} as a json".format(vsp_msg_enum_path))
            logging.debug("Exception info: {}".format(e))
            return -1

    success = True
    for k,v in vsp_msg_enums.items():
        msg_enum = 0
        for i,mtype in enumerate(v):
            if "INHERIT_" in mtype:
                sub_mtype = mtype[len("INHERIT_"):]
                if sub_mtype not in vsp_msg_enums:
                    logging.debug("Failed to find msgType {} in {}".format(sub_mtype, vsp_msg_enum_path))
                    success = False
                    break
                for i2,mtype2 in enumerate(vsp_msg_enums[sub_mtype], 0):
                    vmsg_enums[k][mtype2] = i2
                    msg_enum = i2
            else:
                vmsg_enums[k][mtype] = i+msg_enum

    if not success:
        return -1

    return 0


