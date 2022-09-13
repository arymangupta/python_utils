import os
import sys
import json
import time
import psutil
import socket
import hashlib
import logging
import datetime
import traceback

if sys.platform.lower() == "win32":
    from ctypes import windll
    import string
    #import win32file

    device_to_letter = {}

logger = logging.getLogger("")

gpid = 0

VSP_var_home = os.environ.get("VSP_VAR_HOME", None)
if not VSP_var_home:
    if sys.platform.lower() == "linux":
        VSP_var_home = os.path.join("/var", "virsec")
    elif sys.platform.lower() == "win32":
        VSP_var_home = os.path.join("C:" + os.sep, "Program Files (x86)", "virsec")


VSP_bin_home = os.environ.get("VSP_HOME", None)
if not VSP_bin_home:
    if sys.platform.lower() == "linux":
        VSP_bin_home = os.path.join("/opt", "virsec")
    elif sys.platform.lower() == "win32":
        VSP_bin_home = os.path.join("C:" + os.sep, "Program Files (x86)", "virsec")

# Setting path for hosts file
if sys.platform.lower() == "linux":
    VSP_etc_hosts = os.path.join("/etc", "hosts")
elif sys.platform.lower() == "win32":
    VSP_etc_hosts = os.path.join(
        "C:" + os.sep, "Windows", "System32", "drivers", "etc", "hosts"
    )

VSP_share_home = os.environ.get("VSP_VIRSEC_SHARE", None)
VSP_appcfg_path = os.environ.get("VSP_APPCONFIG_JSON", None)
VSP_cimg_names = os.environ.get("VSP_CIMG_NAMES_ENV", None)
VSP_depl_names = os.environ.get("VSP_DEPLY_NAMES_ENV", None)
VSP_host_tags = os.environ.get("VSP_HOST_SVC_TAGS_ENV", None)
VSP_pod_id = os.environ.get("VSP_POD_ID", None)
VSP_pod_name = os.environ.get("VSP_POD_NAME", None)
VSP_cimg_name = os.environ.get("VSP_CIMG_NAME_ENV", None)
VSP_cimg_hash = os.environ.get("VSP_CIMG_HASH_ENV", None)
VSP_kafka_hostname = os.environ.get("VSP_KAFKA_HOSTNAME_ENV", None)
VSP_kafka_port = os.environ.get("VSP_KAFKA_PORT_ENV", None)
VSP_CMS_url = os.environ.get("CMS_LB_URL", None)
VSP_app_host_os = os.environ.get("VSP_APP_HOST_OS", None)
VSP_app_host_version = os.environ.get("VSP_APP_HOST_VERSION", None)


class VSPInfo:
    VSP_VAR_HOME = VSP_var_home
    VSP_BIN_HOME = VSP_bin_home
    VSP_ETC_HOSTS = VSP_etc_hosts

    VSP_SHARE_ENV = "VSP_VIRSEC_SHARE"
    VSP_SHARE_HOME = VSP_share_home

    VSP_APPCFG_ENV = "VSP_APPCONFIG_JSON"
    VSP_APPCFG_PATH = VSP_appcfg_path

    VSP_CIMG_NAMES_ENV = "VSP_CIMG_NAMES_ENV"
    VSP_CIMG_NAMES = VSP_cimg_names

    VSP_CIMG_NAME_ENV = "VSP_CIMG_NAME_ENV"
    VSP_CIMG_NAME = VSP_cimg_name

    VSP_CIMG_HASH_ENV = "VSP_CIMG_HASH_ENV"
    VSP_CIMG_HASH = VSP_cimg_hash

    VSP_DEPL_NAMES_ENV = "VSP_DEPLY_NAMES_ENV"
    VSP_DEPL_NAMES = VSP_depl_names

    VSP_HOST_TAGS_ENV = "VSP_HOST_SVC_TAGS_ENV"
    VSP_HOST_TAGS = VSP_host_tags

    VSP_POD_ID_ENV = "VSP_POD_ID"
    VSP_POD_ID = VSP_pod_id

    VSP_POD_NAME_ENV = "VSP_POD_NAME"
    VSP_POD_NAME = VSP_pod_name

    VSP_KAFKA_HOSTNAME_ENV = "VSP_KAFKA_HOSTNAME_ENV"
    VSP_KAFKA_HOSTNAME = VSP_kafka_hostname

    VSP_KAFKA_PORT_ENV = "VSP_KAFKA_PORT_ENV"
    VSP_KAFKA_PORT = VSP_kafka_port

    VSP_CMS_URL_ENV = "CMS_LB_URL"
    VSP_CMS_URL = VSP_CMS_url

    VSP_APP_HOST_OS_ENV = "VSP_APP_HOST_OS"
    VSP_APP_HOST_OS = VSP_app_host_os

    VSP_APP_HOST_VERSION_ENV = "VSP_APP_HOST_VERSION"
    VSP_APP_HOST_VERSION = VSP_app_host_version

    CMS_DEFAULT_HOSTNAME = "int.cms.virsec.com"

    VSP_CONFIG_DIR = os.path.join(VSP_BIN_HOME, "config")
    VSP_CONFIG_FILE = "vsp_probe.cfg"

    VSP_BIN_DIR = os.path.join(VSP_BIN_HOME, "bin")
    VSP_LIB_DIR = os.path.join(VSP_BIN_HOME, "lib")
    VSP_LIB32_DIR = os.path.join(VSP_BIN_HOME, "lib32")

    VSP_SCRIPTS = os.path.join(VSP_BIN_HOME, "scripts")
    VSP_LOGS = os.path.join(VSP_VAR_HOME, "log")
    VSP_LOGS_ALL = [VSP_VAR_HOME, VSP_CONFIG_DIR, VSP_ETC_HOSTS]

    VIPC_STATE = os.path.join(VSP_VAR_HOME, "vIPC_state")

    VSP_TMPDIR = os.path.join(VSP_BIN_HOME, "tmp")
    VSP_HMM_IGNORE = "VSP_HMM_IGNORE_ENV"

    VSP_CONFIG_DIR = os.path.join(VSP_BIN_HOME, "config")

    VSP_STATE = os.path.join(VSP_VAR_HOME, "vsp_state")
    VSP_STATE_VPROCESS = os.path.join(VSP_STATE, "vsp_process.pkl")
    VSP_STATE_VSPCLI_CMD = os.path.join(VSP_STATE, "vsp_cli.cmd")
    VSP_STATE_VSPMGR_CMD = os.path.join(VSP_STATE, "vsp_mgr.cmd")
    VSP_STATE_LAST_ERR = os.path.join(VSP_STATE, "vsp_last_error.log")

    DL_FILE_PATH = os.path.join("data", "downloadfiles")
    VSP_PROV_PATH = os.path.join(VSP_VAR_HOME, DL_FILE_PATH)

    VSP_PROV_PATH_V2 = os.path.join(VSP_VAR_HOME, "appconfig")

    VSP_CERT_PATH = os.path.join(VSP_VAR_HOME, "certs")

    PLATFORM = "WINDOWS" if sys.platform.lower() == "win32" else "LINUX"
    VSP_REMOTE_CLI_PATH = (
        os.path.join(VSP_BIN_DIR, "vsp-cli.exe")
        if PLATFORM == "WINDOWS"
        else os.path.join(VSP_BIN_DIR, "vsp-cli")
    )

    VSP_PROBE_PASSWORD = os.path.join(VSP_CONFIG_DIR, ".vsp_misc.txt")
    VSP_WIN_SERVICE = os.path.join(VSP_BIN_DIR, 'VSPServiceHandler.exe')
    
    WEB_ASSIST_SAVED_CONFIG_PATH =  os.path.join(VSP_var_home, "data","savedconfig","web")
        
    if sys.platform.lower() == "linux":
        IAE_ASSIST_LIB_PATH = os.path.join(VSP_bin_home, "lib","libIAE-Assist.so")
    elif sys.platform.lower() == "win32":
        IAE_ASSIST_LIB_PATH =  os.path.join(VSP_bin_home, "lib", "IAE-Assist.dll")        


class VSPComponent:

    AE = "AE"
    AE_proxy = "AE-PROXY"
    vIPC_server = "VIPC-SERVER"
    FSM = "FSM"
    FSM_AGENT = "FSM-AGENT"
    HMM = "HMM"
    HMM_CLIENT = "HMM-CLIENT"
    RMP = "RMP"
    vmgr = "VSP-MANAGER"
    vmem_assist = "VSP-MEMORY-ASSIST"
    vmem = "VSP-MEMORY"
    vweb_assist = "VSP-WEB-ASSIST"
    vweb = "VSP-WEB"
    vapg = "VSP-APG"
    CMS = "CMS"
    vsp_cli = "VSP-CLI"
    vsp_remote_cli = "VSP-REMOTE-CLI"

    __d = {}
    __d[AE] = {"name": "AE", "vIPC_id": 10000}
    __d[AE_proxy] = {"name": "AE-PROXY", "vIPC_id": 10010}
    __d[vIPC_server] = {"name": "vIPC-server", "vIPC_id": 10001}
    __d[FSM] = {"name": "FSM", "vIPC_id": 10002}
    __d[FSM_AGENT] = {"name": "FSM-AGENT", "vIPC_id": 10012}
    __d[HMM] = {"name": "HMM", "vIPC_id": 10011}
    __d[HMM_CLIENT] = {"name": "HMM-CLIENT", "vIPC_id": 0}
    __d[RMP] = {"name": "RMP", "vIPC_id": 10013}
    __d[vmgr] = {"name": "VSP-manager", "vIPC_id": 10005}
    __d[vmem_assist] = {"name": "VSP-memory-assist", "vIPC_id": 10006}
    __d[vweb_assist] = {"name": "VSP-web-assist", "vIPC_id": 10007}
    __d[vapg] = {"name": "VSP-APG", "vIPC_id": 10008}
    __d[vweb] = {"name": "VSP-web", "vIPC_id": 0}
    __d[vmem] = {"name": "VSP-memory", "vIPC_id": 200000}
    __d[CMS] = {"name": "CMS", "vIPC_id": 0}
    __d[vsp_cli] = {"name": "VSP-cli", "vIPC_id": 10009}
    __d[vsp_remote_cli] = {"name": "VSP-remote-cli", "vIPC_id": 0}

    __valid_vIPC_ids = {}
    for k, v in __d.items():
        __valid_vIPC_ids[v["vIPC_id"]] = k

    @staticmethod
    def members():
        return VSPComponent.__d.keys()

    @staticmethod
    def members_proper():
        return [v["name"] for k, v in VSPComponent.__d.items()]

    @staticmethod
    def is_member(v_name):
        return v_name.upper() in VSPComponent.__d.keys()

    @staticmethod
    def is_valid_vIPC_id(v_id):
        return v_id in VSPComponent.__valid_vIPC_ids

    @staticmethod
    def get_vIPC_id(vsp_comp_name):
        return VSPComponent.__d.get(vsp_comp_name.upper())["vIPC_id"]

    @staticmethod
    def get_proper_name(vsp_comp_name):
        return VSPComponent.__d.get(vsp_comp_name.upper())["name"]

    @staticmethod
    def get_vsp_name(v_id):
        return VSPComponent.__valid_vIPC_ids.get(v_id, None)


def get_file_lock(filename, timeout, locked_files):
    file_lock = "{}{}".format(filename, ".lock")
    i = 0
    while os.path.exists(file_lock) and i in range(0, timeout):
        time.sleep(1)
        i += 1
    if i in range(0, timeout):
        open(file_lock, "a").close()
        locked_files[file_lock] = 0
        return True
    return False


def release_file_lock(filename, locked_files):
    file_lock = "{}{}".format(filename, ".lock")
    try:
        os.remove(file_lock)
    except:
        pass
    locked_files.pop(file_lock)


def get_child_pids(parent_pid):
    child_pids = []
    try:
        ps_proc = psutil.Process(parent_pid)
        for c in ps_proc.children(recursive=True):
            child_pids.append(c.pid)
    except:
        pass
    return child_pids


def get_gpid():
    return gpid


def set_gpid(igpid):
    global gpid
    gpid = igpid


def clear_last_error_file():
    with open(VSPInfo.VSP_STATE_LAST_ERR, "w") as f:
        f.write(
            "VSP manager error file from last boot time: {}".format(
                datetime.datetime.now()
            )
        )
        f.write("\n")


def log_last_error(err_msgs):
    # FIXME: This should be a global var...
    locked_files = {}
    lock = get_file_lock(VSPInfo.VSP_STATE_LAST_ERR, 5, locked_files)
    if not lock:
        logging.error(
            "Unable to obtain file lock for {}".format(VSPInfo.VSP_STATE_LAST_ERR)
        )
        return None
    with open(VSPInfo.VSP_STATE_LAST_ERR, "a+") as f:
        for err in err_msgs:
            f.write("{} | {}".format(datetime.datetime.now(), err))
            f.write("\n")
    release_file_lock(VSPInfo.VSP_STATE_LAST_ERR, locked_files)


# This function is used for HMM/host service tags to prevent issues with
# container names containing tags and/or '/'
def transform_cimg_name(cimg_name):
    # First replace colons with dashes
    _cimg_name = cimg_name.replace(":", "--")
    _cimg_name = _cimg_name.replace("/", "__")
    return _cimg_name


# This function does the opposite of the function above
def get_cimg_name(cimg_name):
    # Here we have to revert changes made to the original container image name
    _cimg_name = cimg_name.replace("--", ":")
    _cimg_name = _cimg_name.replace("__", "/")

    return _cimg_name


def get_ip(hostname):
    try:
        ip = socket.gethostbyname(hostname)
    except:
        # Error is handled by the caller...pass exception
        pass
        return None
    return ip


def get_cms_ip(config_cms_hostname, host_type, print_msg=False):
    cms_ip = ""
    cms_hostnames = []
    if VSPInfo.VSP_CMS_URL:
        # If this env var is set, try to resolve CMS IP; else fail
        if print_msg:
            logging.debug(
                "Found env var ({}) for CMS hostname. Attempting to resolve CMS IP based on {}".format(
                    VSPInfo.VSP_CMS_URL_ENV, VSPInfo.VSP_CMS_URL
                )
            )
        cms_ip = get_ip(VSPInfo.VSP_CMS_URL)
        cms_hostnames = [VSPInfo.VSP_CMS_URL]
        return cms_hostnames, cms_ip

    if not cms_ip:
        # If the env var was not set or it did not resolve, try using the configured hostname
        if print_msg:
            logging.debug(
                "Using local configuration for CMS hostname. Attempting to resolve CMS IP based on {}".format(
                    config_cms_hostname
                )
            )
        cms_ip = get_ip(config_cms_hostname)
        cms_hostnames += [str(config_cms_hostname)]

    if not cms_ip and host_type.lower() == "psi":
        # In containers, we try to resolve the cms_ip with the default CMS service name
        if print_msg:
            logging.debug(
                "Attempting to resolve CMS IP based on {}".format("vsp-cms.virsec")
            )
        cms_ip = get_ip("vsp-cms.virsec")
        cms_hostnames += ["vsp-cms.virsec"]

    # Return all tried cms_hostnames, cms_ip is only set on successful resolution
    return cms_hostnames, cms_ip


def get_vsp_remote_topic(service_instance_id):
    """Return kafka topic
    :return: topic (string)
    """
    topic = "VSP_" + service_instance_id
    return topic


def get_vserver_cfg_info(config_dir, locked_files={}, max_file_waittime=5):
    directory = os.fsencode(config_dir)

    vserver_cfg_info = {}

    for f in os.listdir(directory):
        filename = os.fsdecode(f)
        if filename.endswith(".cfg"):
            cfg_filename = os.path.join(config_dir, filename)
            lock = get_file_lock(cfg_filename, max_file_waittime, locked_files)
            if not lock:
                logging.error("Unable to obtain file lock for {}".format(cfg_filename))
                logging.debug(
                    "If no other instances of vsp-cli or VSP services are running, please delete {}.lock and retry".format(
                        cfg_filename
                    )
                )
                continue

            with open(cfg_filename) as cfg_file:
                try:
                    cfg = json.load(cfg_file)
                except json.JSONDecodeError as e:
                    release_file_lock(cfg_filename, locked_files)
                    continue
                else:
                    vsp_comp_name = cfg.get("targetVSPComp")
                    if (
                        vsp_comp_name
                        and vsp_comp_name.upper() == VSPComponent.vIPC_server
                    ):
                        vserver_cfg_info = cfg.get("configs")
            release_file_lock(cfg_filename, locked_files)

    return vserver_cfg_info


def get_md5sum_str(istring, print_log=False):

    if not isinstance(istring, str):
        return ""

    csum = ""
    # This flag needs to be off in the cases where FIPS is enabled
    used_for_security = True
    # Try a max of two times
    for x in range(2):
        try:
            if used_for_security:
                csum = hashlib.md5(istring.encode("utf-8")).hexdigest()
            else:
                csum = hashlib.md5(
                    istring.encode("utf-8"), usedforsecurity=used_for_security
                ).hexdigest()
        except ValueError:
            # Might be caused by FIPS
            used_for_security = False
            if print_log:
                logging.debug("Retrying with usedforsecurity set to False")
            csum = ""
            continue
        except:
            # Other error occurred
            if print_log:
                logging.error(
                    "Exception occurred while trying to calculate MD5sum of CMS response: {}".format(
                        traceback.format_exc()
                    )
                )
            csum = ""
            break
        else:
            break

    return csum


def get_md5sum_file(filename, blocksize=65536):

    if not os.path.exists(filename):
        return ""

    used_for_security = True
    h = None
    # Try a max of two times
    for x in range(2):
        try:
            if used_for_security:
                h = hashlib.md5()
            else:
                h = hashlib.md5(usedforsecurity=used_for_security)
        except ValueError:
            # Might be caused by FIPS
            used_for_security = False
            continue
        except:
            # Other error occurred
            h = None
            break
        else:
            break

    if not h:
        return ""

    try:
        with open(filename, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                h.update(block)
        return h.hexdigest()
    except Exception as e:
        return ""

def get_root_drives():
    drives = []
    if VSPInfo.PLATFORM == "WINDOWS":
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter + ":\\")
            bitmask >>= 1

        # Move C:\\ to the beginning of the list, since this is the default drive value
        if "C:\\" in drives:
            drives.insert(0, drives.pop(drives.index("C:\\")))
    elif VSPInfo.PLATFORM == "LINUX":
        drives = ["/"]
    return drives

def get_device_to_letter_drives(update=False):
    global device_to_letter
    if not update and device_to_letter:
        return device_to_letter
    else:
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                dos_dev_str = win32file.QueryDosDevice(letter + ":")
                # Returns something like this: '\\Device\\HarddiskVolume3\x00\x00'
                device_to_letter[dos_dev_str[:-2]] = letter + ":"
            bitmask >>= 1
        return device_to_letter


class VspKeys:
    CFG_LOG_LEVEL                   = "logLevel"
    CFG_LOG_MAX_FILES               = "logMaxFile"
    CFG_LOG_ROTATE_COUNT            = "logRotateCount"
    CFG_HB_FREQ                     = "HBFrequency"
    CFG_LOG_MAX_FILE_SIZE           = 'logMaxFileSize'
    CFG_IPC_READ_TIMEOUT            = 'IPC_ReadTimeout'
    CFG_VIPC_INIT_RETRY             = 'vipcInitRetry'
    CFG_VIPC_INIT_RETRY_TIMEOUT     = 'vipcInitRetryTimeout'    
    CFG_IPC_READ_TIMEOUT            = "IPC_ReadTimeout" 
    CFG_LOG_PATH                    = "logPath" 
    CFG_STATS_PATH                  = "statsPath"
    CFG_STATS_ROOT_DIR              = "statsRootDir"
    CFG_STATS_REFRESH_RATE          = 'statsRefreshRate'
    CFG_STATS_FILE_NAME             = "statsFileName"    
    CFG_STATE_ID                    = "stateID"
    CFG_SUBSTATES                   = "subStates"
    CFG_STATE                       = "state"
    CFG_STATE_ID_APPCTX             = "appContext"
    CFG_STATE_ID_TYPES              = "types"
    CFG_STATE_ID_CONF               = "config"
    CFG_STATE_ID_LOG_LEVEL          = "logLevel"
    CFG_VIPC_LIB_PATH               = 'vIPCLibPath'
    CFG_VIPC_MAX_MSG_SIZE           = 'vIPCMaxMsgSize'
    CFG_VIPC_READ_TIMEOUT           = 'vIPCTimeout'
    CFG_VSP_MSG_ENUM_PATH           = 'vspMsgTypesEnumsPath'
    PD_KEY_AUTOPROV_FLAG			= "autoprovFlag"
    PD_VERSION						= "v1.0"

    PD_KEY_VERSION                  = "version"
    PD_KEY_ASI_ID                   = "asiID"
    PD_KEY_OBJECT                   = "ivObject"
    PD_KEY_APP_CONFIG               = "appCfg"

    PD_KEY_APP_COLLECTIVE_ID        = "processCollectiveId"
    PD_KEY_NAMESPACE                = "namespace"
    PD_KEY_REQUEST_ID               = "requestID"
    PD_KEY_SOURCE_VSP_COMP          = "sourceVSPComp"
    PD_KEY_APP_NAME                 = "appName"
    PD_KEY_APP_PATH                 = "appDeploymentFolder"
    PD_KEY_CONTEXT_PATH             = "contextPath"
    PD_KEY_INLINE_PROTECTION_MODE   = "inlineProtectMode"
    PD_KEY_SQLI                     = "SQLi"
    PD_KEY_FSM                      = "FSM"
    PD_KEY_RXSS                     = "ReflectedXSS"
    PD_KEY_IP                       = "AA"
    PD_KEY_CSRF                     = "CSRF"
    PD_KEY_URL_SQLLOG               = "USL"
    PD_KEY_SXSS                     = "StoredXSS"
    PD_KEY_CRLFI                    = "CRLFi"
    PD_KEY_CMDI                     = "CMDi"
    PD_KEY_PT                       = "PATH_TRAVERSALi"
    PD_KEY_CLASS_LOAD_LOG           = "CLL"
    PD_KEY_SW_EXCE_LOG              = "SWL"
    PD_KEY_LFI                      = "LFI"
    PD_KEY_RFI                      = "RFI"
    PD_KEY_DOMXSS                   = "DOMXSS"
    PD_KEY_TARGET_VSP_COMP			= "targetVSPComp"
    PD_KEY_FINAL_PROV_STATUS		= "response"
    PD_KEY_ERROR_BLOCK				= "responseMsgs"
    PD_KEY_ERROR_MESSAGE			= "error"
    PD_KEY_CONFIG_FILE_PATH			= "configurationPath"
    PD_KEY_DEPLOYMENT_TYPE			= "deploymentType"
    PD_VAL_DEPLOYMENT_TYPE_K8POD	= "K8POD"
    PD_VAL_DEPLOYMENT_TYPE_VM		= "VM"
    PD_VAL_DEPLOYMENT_TYPE_CONTAINER= "DOCKERCONTAINER"
    PD_KEY_FEEDBACK_REQ				= "feedbackReq"
    PD_KEY_LFI_DIRECTORIES			= "directories"
    PD_KEY_LFI_EXTENSIONS			= "extensions"
    PD_KEY_RFI_URLS					= "urls"
    PD_KEY_SERVER_TYPE				= "serverType"
    PD_KEY_SERVER_NAME				= "serverName"
    PD_KEY_MSG_TYPE					= "msgType"
    PD_KEY_MSG_TXNID				= "msgTxnID"
    PD_KEY_CONFIGS					= "configs"
    PD_KEY_PROCESS_TYPE				= "type"
    PD_KEY_METADATA					= "metadata"
    PD_KEY_APPTYPE					= "applicationType"
    PD_KEY_FILTERTYPE				= "filterType"
    PD_KEY_INSTRUMENTFILTERCLASS	= "instrumentationFilterClass"
    PD_KEY_FILTERMETHOD				= "filterMethod"
    PD_KEY_FILTERPOSITION			= "filterPosition"
    PD_KEY_SERVICE_TYPE				= "serviceType"
    PD_KEY_WEB_SERVER_NAME			= "webServerName"
    PD_KEY_WEB_SERVER_TYPE			= "webServerType"
    PD_KEY_WEB_SERVER_VERSION		= "webServerVersion" 
    PD_KEY_WEB_SERVER_CFG_PATH		= "webServerCfgPath" 
    PD_KEY_WEB_SERVER_APP_HOST_NAME = "applicationHostName"
    PD_KEY_WEB_SERVER_BIN_PATH		= "webServerBinPath"
    PD_KEY_WEB_SERVER_LOG_PATH		= "webServerLogPath"
    PD_KEY_WEB_SERVER_CMD			= "webServerCMD"
    PD_KEY_CONTAINTER_INFO			= "containerInfo"
    PD_KEY_SERVICE_TYPE				= "serviceType"
    PD_KEY_CUSTOM					= "Custom"
    PD_KEY_BE						= "BE"
    PD_KEY_PROTO_ATTACK				= "ProtocolAttack"
    PD_KEY_PROTO_ENFORCE			= "ProtocolEnforcement"
    PD_KEY_XMLI						= "XMLInjection"
    PD_KEY_METHOD_ENFORCE			= "MethodEnforcement"
    PD_KEY_CONTAINTER_IMG_NAME		= "imageName"
    PD_KEY_SEGMENTED_RESPONSE       = "segmentedResponse"
    SERVICE_TYPE_WEB                = 'webService'
    SERVICE_TYPE_APP                = 'appService'
    
    APPLICATION_JAVA                = 'Java'
    APPLICATION_DNET                = '.Net'
    APPLICATION_DNET_CORE           = '.Net Core'
    APPLICATION_PHP                 = 'Php'
    APPLICATION_NODEJS              = 'Node.js'
    APPLICATION_RUBY                = 'Ruby'
    SERVER_TYPE_NGINX               = 'Nginx'
    SERVER_TYPE_APACHE              = 'Apache Httpd'
    SERVICE_TYPE_WEB                = 'webService'
    SERVICE_TYPE_APP                = 'appService'
    
    CFG_LANG_UPDATE_LOG_PATH        = PD_KEY_PROCESS_TYPE + ":" + PD_KEY_CONTEXT_PATH + ":" + CFG_LOG_PATH
    CFG_LANG_UPDATE_LOG_LEVEL       = PD_KEY_PROCESS_TYPE + ":" + PD_KEY_CONTEXT_PATH + ":" + CFG_LOG_LEVEL
    
    
class VspVulMask:   
    SQLI_VULNERABILITY_MASK                 = (1)
    REFLECTIVE_XSS_VULNERABILITY_MASK       = (2)
    STORED_XSS_VULNERABILITY_MASK           = (4)
    CRLFI_VULNERABILITY_MASK                = (8)
    CMDI_VULNERABILITY_MASK                 = (16)
    PATH_TRAVERSALI_VULNERABILITY_MASK      = (32)
    CLASS_LOAD_VULNERABILITY_MASK           = (128)
    SW_EXCEPTION_VULNERABILITY_MASK         = (256)
    LFI_VULNERABILITY_MASK                  = (512)
    RFI_VULNERABILITY_MASK                  = (1024)
    DOMXSS_VULNERABILITY_MASK               = (2048)
    XMLI_VULNERABILITY_MASK                 = (4096)
    CUSTOM_VULNERABILITY_MASK               = (8192)
    PROTO_ENFORCE_VULNERABILITY_MASK        = (16384)
    CSRF_VULNERABILITY_MASK                 = (32768)