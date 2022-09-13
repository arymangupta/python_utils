from array import array
from ast import parse
from asyncore import read
from ctypes import windll
from distutils.log import info
import sys
import winreg
import logging
import os
import shutil
import json
from xml.dom.minidom import Element
import xml.etree.ElementTree as ET
import re

# class CommentedTreeBuilder(ET.TreeBuilder):
#     def comment(self, data):
#         self.start(ET.Comment, {})
#         self.data(data)
#         self.end(ET.Comment)

vspHome="VSP_HOME"

corProfilerPath64          =  os.path.join(os.environ[vspHome], "iae-dnet", "bin", "dotnetprofiler.dll")
corProfilerPath32          =  os.path.join(os.environ[vspHome], "iae-dnet", "bin", "x86", "dotnetprofiler.dll")
corProfilerClsId           = '{8E2B38F2-7355-4C61-A54F-434B7AC266C0}'
corProfilerFlag            = '1'

DOTNET_PROFILER = [
                    f"COR_ENABLE_PROFILING={corProfilerFlag}", 
                    f"COR_PROFILER={corProfilerClsId}",
                    f"COR_PROFILER_PATH_64={corProfilerPath64}",
                    f"COR_PROFILER_PATH_32={corProfilerPath32}",
                  ]

DOTNET_CORE_PROFILER = [
                        f"CORECLR_ENABLE_PROFILING={corProfilerFlag}",
                        f"CORECLR_PROFILER={corProfilerClsId}",
                        f"CORECLR_PROFILER_PATH_64={corProfilerPath64}",
                        f"CORECLR_PROFILER_PATH_32={corProfilerPath32}",
                       ]
    
def setVspEntries(applicationDepFolder, provisionFlag):
    isProvision = provisionFlag.lower() == "true"
    provData = os.path.join(os.environ[vspHome], "iae-dnet", "provData.json")
    data = json.loads('{ "apps": [] }')
    isFirstApp = False;

    if(os.path.exists(provData)):
        with open(provData, "r") as file:
            data = json.loads(file.read())

    isFirstApp = len(data['apps']) == 0;

    if(isProvision):
        if(applicationDepFolder not in data['apps']):
            data["apps"].append(applicationDepFolder)
    else:
        if(applicationDepFolder in data['apps']):
            data["apps"].remove(applicationDepFolder)

    isLastApp  = len(data['apps']) == 0;

    with open(provData, "w") as file:
        json.dump(data, file)

    if(isProvision and isFirstApp):
        addRegistryEntries()

    if(not isProvision and isLastApp):
        removeRegistryEntries()

def addRegistryEntries():
    logging.info(f"Adding registry entries is started...");
    isEnvironmentAlreadyExists = False;
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        with winreg.OpenKey(reg, 'SYSTEM\CurrentControlSet\Services\WAS', 0, winreg.KEY_ALL_ACCESS) as regkey:
            for i in range(1024):
                try:
                    value = winreg.EnumValue(regkey, i)
                except:
                    #logging.info(f"");
                    status = False
                else:
                    key = value[0]
                    exceptVsp = []
                    if(key.lower() == "environment"):
                        isEnvironmentAlreadyExists = True
                        value = value[1]
                        for item in value:
                            if( item.upper() != f"COR_ENABLE_PROFILING={corProfilerFlag}".upper() and 
                                item.upper() != f"COR_PROFILER={corProfilerClsId}".upper() and 
                                item.upper() != f"COR_PROFILER_PATH_64={corProfilerPath64}".upper() and
                                item.upper() != f"COR_PROFILER_PATH_32={corProfilerPath32}".upper()):
                                exceptVsp.append(item)
                        
                        if(not exceptVsp):
                            winreg.SetValueEx(regkey, 'Environment', 0, winreg.REG_MULTI_SZ, DOTNET_PROFILER)
                        else:
                            exceptVsp.extend(DOTNET_PROFILER)
                            winreg.SetValueEx(regkey, 'Environment', 0, winreg.REG_MULTI_SZ, exceptVsp)
                        break;
            
            if(isEnvironmentAlreadyExists == False):
                winreg.SetValueEx(regkey, 'Environment', 0, winreg.REG_MULTI_SZ, DOTNET_PROFILER)
        logging.info(f"Adding registry entries are done")
    except:
        logging.error(f"Adding registry entries is failed with error, Exception:  {sys.exc_info()[0]}");

def removeRegistryEntries():
    logging.info(f"Removing registry entries is started");
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        with winreg.OpenKey(reg, 'SYSTEM\CurrentControlSet\Services\WAS', 0, winreg.KEY_ALL_ACCESS) as regkey:
            for i in range(1024):
                try:
                    value = winreg.EnumValue(regkey, i)
                except:
                    #logging.info(f"")
                    status = False
                else:
                    key = value[0]
                    exceptVsp = []
                    if(key.lower() =="environment"):
                        value = value[1]
                        for item in value:
                            if( item.upper() != f"COR_ENABLE_PROFILING={corProfilerFlag}".upper() and 
                                item.upper() != f"COR_PROFILER={corProfilerClsId}".upper() and 
                                item.upper() != f"COR_PROFILER_PATH_64={corProfilerPath64}".upper() and
                                item.upper() != f"COR_PROFILER_PATH_32={corProfilerPath32}".upper()):
                                exceptVsp.append(item)
                        
                        if(not exceptVsp):
                            winreg.DeleteValue(regkey, 'Environment')
                        else:
                            winreg.SetValueEx(regkey, 'Environment', 0, winreg.REG_MULTI_SZ, exceptVsp)
                            
                        logging.info(f"Removing registry entries is done")
                        break
    except:
        logging.error(f"Removing registry entries is failed with error, Exception:  {sys.exc_info()[0]}");

def copyFiles(applicationDepFolder, applicationContext, isX86):

    logging.info(f'Copying necessary files started, applicationDepFolder: {applicationDepFolder}, applicationContext: {applicationContext}, isX86: {isX86}')
    home_dir =os.environ[vspHome]
    if(isX86):
        virsecDnetFrameDllPath = os.path.join(home_dir,  "iae-dnet", "bin", "x86", "Virsec.DNet.Frame.dll")
    else:
        virsecDnetFrameDllPath = os.path.join(home_dir,  "iae-dnet", "bin", "Virsec.DNet.Frame.dll")

    applicationBinFolder = os.path.join(applicationDepFolder, "bin")
    if not os.path.exists(applicationBinFolder):
        os.mkdir(applicationBinFolder)
    copy(virsecDnetFrameDllPath, applicationBinFolder)
    logging.info(f'Copying {virsecDnetFrameDllPath} into {applicationBinFolder} is done')
    microsoftWebInfraDllOnAppPath = os.path.join(applicationBinFolder, "Microsoft.Web.Infrastructure.dll")

    if not os.path.exists(microsoftWebInfraDllOnAppPath):
        if(isX86):
            microsoftWebInfraDllOnAppPath = os.path.join(home_dir,  "iae-dnet", "bin", "x86", "Microsoft.Web.Infrastructure.dll")
        else:
            microsoftWebInfraDllOnAppPath = os.path.join(home_dir,  "iae-dnet", "bin", "Microsoft.Web.Infrastructure.dll")

        copy(microsoftWebInfraDllOnAppPath, applicationBinFolder)
        logging.info(f'Copying {microsoftWebInfraDllOnAppPath} into {applicationBinFolder} is done')
    else:
        logging.info(f'Copying Microsoft.Web.Infrastructure.dll into {applicationBinFolder} is skipped as it is already present')

    copyVspFile(applicationContext, applicationDepFolder)
    
def copyVspFile(applicationContext, applicationDepFolder):
    vspConfigData =  {
                        "AppContext": applicationContext,
                        "LogLevel": "",
                        "LogPath": ""
                     }

    vspConfigDataAsString = json.dumps(vspConfigData, indent = 2)
    vspConfigFile =os.path.join(applicationDepFolder, "vsp.cfg")
    jsonFile = open(vspConfigFile, "w+")
    jsonFile.write(vspConfigDataAsString)
    jsonFile.close()
    logging.info(f'Copying vsp.cfg into {applicationDepFolder} is done')

def deleteFiles(applicationDepFolder):
    home_dir =os.environ[vspHome]
    virsecDnetFrameDllPath = os.path.join(applicationDepFolder, "bin", "Virsec.DNet.Frame.dll")
    if os.path.exists(virsecDnetFrameDllPath):
        os.remove(virsecDnetFrameDllPath)
        logging.info(f'Deleting {virsecDnetFrameDllPath} from {applicationDepFolder} is done')
    else:
        logging.info(f'Seems {virsecDnetFrameDllPath} is already deleted from {applicationDepFolder}')
    
    deleteVspFile(applicationDepFolder);

def deleteVspFile(applicationDepFolder):
    vspConfigFile =os.path.join(applicationDepFolder, "vsp.cfg")
    if os.path.exists(vspConfigFile):
        os.remove(vspConfigFile)
        logging.info(f'Deleting {vspConfigFile} from {applicationDepFolder} is done')

# <remove name="IaeModule" />
# <add name="IaeModule" type="IaeModule.VirsecModule, Virsec.DNet.Frame" preCondition="" />
def updateWebConfig(applicationDepFolder):
    try:
        logging.info("Updating web.config file...")
        webConfigFile = os.path.join(applicationDepFolder, "web.config")
        logging.info(f"web.config found in {webConfigFile}")
        webConfigBackupFile = os.path.join(applicationDepFolder, "web.config.virsec")
        logging.info(f"Creating backup for web.config in {webConfigBackupFile}...")
        copy(webConfigFile, webConfigBackupFile)
        logging.info(f"Creating backup for web.config in {webConfigBackupFile} is done.")
        logging.info(f"Parsing {webConfigFile} is started...")
        file = ET.parse(webConfigFile) 
        #file = ET.parse(webConfigFile, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))) 
        #file = ET.parse(webConfigFile, parser=ET.XMLParser(target=CommentedTreeBuilder())) 
        logging.info(f"Parsing {webConfigFile} is done, {file}")
        logging.info(f"Searching modules section...")
        module = file.findall('.//modules')
        if (module):
            remove = ET.SubElement(module[0], 'remove')
            remove.attrib['name'] = 'IaeModule'
            module.append(remove)

            add = ET.SubElement(module[0], 'add')
            add.attrib['name'] = 'IaeModule'
            add.attrib['type'] = 'IaeModule.VirsecModule, Virsec.DNet.Frame'
            add.attrib['preCondition'] = ''
            module.append(add)
            file.write(webConfigFile)
            logging.info(f"Updating web.config file is done...")
        else:
            logging.info(f"finding system.webserver section...")
            configuration = file.getroot()
            webservers = configuration.findall('.//system.webServer')
            
            if not webservers:
                webServer = ET.SubElement(configuration, 'system.webServer')
            else:
                webServer = webservers[0]

            webServer.attrib['runAllManagedModulesForAllRequests']='true'
            module = ET.SubElement(webServer, 'module')
            
            add = ET.SubElement(module, 'add')
            add.attrib['name'] = 'IaeModule'
            add.attrib['type'] = 'IaeModule.VirsecModule, Virsec.DNet.Frame'
            add.attrib['preCondition'] = ''
            file.write(webConfigFile)
            logging.info(f"Updating web.config file is done...")
    except:
            logging.error(f"Updating web.config file is ended up with error, Exception:  {sys.exc_info()[0]}")

def readIISVersion():
    try:
        logging.info('Opening Registry Key SOFTWARE\Microsoft\InetStp')
        aKey = r"SOFTWARE\Microsoft\InetStp"
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        
        with winreg.OpenKey(aReg, aKey, 0, winreg.KEY_ALL_ACCESS) as regkey:
            logging.info('Opened the registry key')
            for i in range(1024):
                value = winreg.EnumValue(regkey, i)
                key = value[0];
                value = value[1]
                logging.info(f'Key: {key}, Value: {value}')
                if(key == "VersionString"):
                    version = re.findall("\d+\.\d+", value)
                    if(type(version) is list):
                        logging.info(f'Found the IIS version, {version}')
                        return version[0];
    except:
        logging.error(f"Error in reading IIS Version, Exception:  {sys.exc_info()[0]}")

def updateEnvVariables(pool, file, applicationHostFile, provisionFlag):
    # <environmentVariables>
    #   <add name="COR_ENABLE_PROFILING" value="1" />
    #   <add name="COR_PROFILER" value="{8E2B38F2-7355-4C61-A54F-434B7AC266C0}" />
    #   <add name="COR_PROFILER_PATH_64" value="C:\Program Files (x86)\Virsec\iae-dnet\bin\dotnetprofiler.dll" />
    #   <add name="COR_PROFILER_PATH_32" value="C:\Program Files (x86)\Virsec\iae-dnet\bin\x86\dotnetprofiler.dll" />
    # </environmentVariables>
        isProvisioned = provisionFlag.lower() == "true"
        logging.info('Environment variables will be updated in the ApplicationHost.config file as IIS version is 10.0 or Above')
        existingEnvVars = pool.find(".//environmentVariables")
        if(existingEnvVars):
            logging.info(f'Environment variables are already present ({len(existingEnvVars)}), overwriting the settings')
            isCOR_ENABLE_PROFILINGFound = False;
            isCOR_PROFILERFound = False;
            isCOR_PROFILER_PATH_64Found = False;
            isCOR_PROFILER_PATH_32Found = False;
            removedItems = []
            for add in existingEnvVars:
                name = add.get('name')
                logging.info(f'Environment Variable: {name}')
                if(name.endswith('_vsp_renamed')):
                    if(not isProvisioned):
                        add.set('name', name.removesuffix('_vsp_renamed'))
                elif(name.upper() == 'COR_ENABLE_PROFILING'):
                    isCOR_ENABLE_PROFILINGFound = True;
                    if(isProvisioned):
                        value = add.get('value')
                        if (value and value.lower() != corProfilerFlag.lower()):
                            name = name + "_vsp_renamed"
                            add.set('name', name)
                            add = ET.SubElement(existingEnvVars, 'add')
                            add.set('name', 'COR_ENABLE_PROFILING')
                        add.set('value', corProfilerFlag)
                    else:
                        removedItems.append(add)
                elif(name.upper() == 'COR_PROFILER'):
                    isCOR_PROFILERFound = True
                    if(isProvisioned):
                        value = add.get('value')
                        if (value and value.lower() != corProfilerClsId.lower()):
                            name = name + "_vsp_renamed"
                            add.set('name', name)
                            add = ET.SubElement(existingEnvVars, 'add')
                            add.set('name', 'COR_PROFILER')
                        add.set('value', corProfilerClsId)
                    else:
                        removedItems.append(add)
                elif(name.upper() == 'COR_PROFILER_PATH_64'):
                    isCOR_PROFILER_PATH_64Found = True
                    if(isProvisioned):
                        value = add.get('value')
                        if (value and value.lower() != corProfilerPath64.lower()):
                            name = name + "_vsp_renamed"
                            add.set('name', name)
                            add = ET.SubElement(existingEnvVars, 'add')
                            add.set('name', 'COR_PROFILER_PATH_64')
                        add.set('value', corProfilerPath64)
                    else:
                        removedItems.append(add)
                elif(name.upper() == 'COR_PROFILER_PATH_32'):
                    isCOR_PROFILER_PATH_32Found = True
                    if(isProvisioned):
                        value = add.get('value')
                        if (value and value.lower() != corProfilerPath32.lower()):
                            name = name + "_vsp_renamed"
                            add.set('name', name)
                            add = ET.SubElement(existingEnvVars, 'add')
                            add.set('name', 'COR_PROFILER_PATH_32')
                        add.set('value', corProfilerPath32)
                    else:
                        removedItems.append(add)
            
            if(not isProvisioned and removedItems):
                for add in removedItems:    
                    existingEnvVars.remove(add)

            if(isProvisioned):
                if(isCOR_ENABLE_PROFILINGFound == False):
                    coreProfilerFlag = ET.SubElement(existingEnvVars, 'add')
                    coreProfilerFlag.attrib['name'] = 'COR_ENABLE_PROFILING'
                    coreProfilerFlag.attrib['value'] = corProfilerFlag
                
                if(isCOR_PROFILERFound == False):
                    corProfiler = ET.SubElement(existingEnvVars, 'add')
                    corProfiler.attrib['name'] = 'COR_PROFILER'
                    corProfiler.attrib['value'] = corProfilerClsId

                if(isCOR_PROFILER_PATH_64Found == False):
                    corProfilerX64 = ET.SubElement(existingEnvVars, 'add')
                    corProfilerX64.attrib['name'] = 'COR_PROFILER_PATH_64'
                    corProfilerX64.attrib['value'] = corProfilerPath64

                if(isCOR_PROFILER_PATH_32Found == False):
                    corProfilerx86 = ET.SubElement(existingEnvVars, 'add')
                    corProfilerx86.attrib['name'] = 'COR_PROFILER_PATH_32'
                    corProfilerx86.attrib['value'] = corProfilerPath32
        else:
            if(isProvisioned):
                if(existingEnvVars is not None):
                    pool.remove(existingEnvVars)
                envVars = ET.SubElement(pool, 'environmentVariables')
                coreProfilerFlag = ET.SubElement(envVars, 'add')
                coreProfilerFlag.attrib['name'] = 'COR_ENABLE_PROFILING'
                coreProfilerFlag.attrib['value'] = corProfilerFlag
                corProfiler = ET.SubElement(envVars, 'add')
                corProfiler.attrib['name'] = 'COR_PROFILER'
                corProfiler.attrib['value'] = corProfilerClsId
                corProfilerX64 = ET.SubElement(envVars, 'add')
                corProfilerX64.attrib['name'] = 'COR_PROFILER_PATH_64'
                corProfilerX64.attrib['value'] = corProfilerPath64
                corProfilerx86 = ET.SubElement(envVars, 'add')
                corProfilerx86.attrib['name'] = 'COR_PROFILER_PATH_32'
                corProfilerx86.attrib['value'] = corProfilerPath32

        file.write(applicationHostFile, encoding='utf-8', xml_declaration=True)
        logging.info(f"Updating {applicationHostFile} file is done...")

def setupDotnetEnvironmentVariables(applicationDepFolder, provisionFlag):
    logging.info('Setting up environment variables for dotnet started....');
    IsX86 = False
    logging.info("Getting appPool configuration...")
    winDir =os.path.expandvars("%windir%");
    winDir = f'{winDir}\system32\inetsrv\config'
    applicationHostFile = os.path.join(winDir, "applicationHost.config")
    backupFile = applicationHostFile + ".virsec"
    if(not os.path.exists(backupFile)):
         copy(applicationHostFile, backupFile)
    logging.info(f"applicationHostFile.config found in {applicationHostFile}")
    try:    
        file = ET.parse(applicationHostFile) 
        #file = ET.parse(applicationHostFile, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))) 
        #file = ET.parse(applicationHostFile, parser=ET.XMLParser(target=CommentedTreeBuilder())) 
        logging.info(f"Searching applications... ")

        siteTag = file.find(".//sites")
        sitesTag = siteTag.findall(".//site")
        isMatched = False;

        for site in sitesTag:
            apps = site.findall(".//application")
            logging.info(f"site: {site.get('name')}")
            for app in apps:
                virDir = app.find("virtualDirectory")
                physicalPath = os.path.expandvars(virDir.get('physicalPath'))
                logging.info(f"physicalPath {physicalPath}")
                isMatched = physicalPath.lower().strip('\/') == applicationDepFolder.lower().strip('\/') 
                logging.info(f"physicalPath: {physicalPath.lower()}, applicationDepFolder: {applicationDepFolder.lower()}, IsMatched: {isMatched}")
                if(isMatched == True):
                    appPool = app.get('applicationPool')

                    if(appPool == None):
                        defaultPool = site.find('.//applicationDefaults')
                        logging.info(f"applicationDefaults: {defaultPool}")
                        if(defaultPool != None):
                            appPool = defaultPool.get('applicationPool')
                            logging.info(f"AppPool is not seen in application level, reading from site default, appPool: {appPool}")

                    if(appPool == None):
                        defaultPool = siteTag.find('.//applicationDefaults')
                        logging.info(f"applicationDefaults: {defaultPool}")
                        if(defaultPool != None):
                            appPool = defaultPool.get('applicationPool')
                            logging.info(f"AppPool is not seen in site level, reading from sites default, appPool: {appPool}")

                    logging.info(f"Deployment Folder '{applicationDepFolder}' is matched with the application Pool: {appPool}")

                    appPools = file.find(".//applicationPools")

                    for pool in appPools:
                        name = pool.get('name');
                        if (name):
                            if(name.lower() == appPool.lower()):
                                iisVersion =  readIISVersion()
                                if(float(iisVersion) >= 10):
                                    updateEnvVariables(pool, file, applicationHostFile, provisionFlag)
                                else:
                                    setVspEntries(applicationDepFolder, provisionFlag)
                               
                                IsX86 = pool.get('enable32BitAppOnWin64') == "true"
                                if(IsX86):
                                    logging.info(f"{appPool} is configured in x86 architecture")
                                    break
                                else:
                                    logging.info(f"{appPool} is configured in x64 architecture")
                                    break

                        if(IsX86):
                            break
                        
                if(isMatched == True):
                    break

            if(isMatched == True):
                break
    except:
        logging.error(f"Error in setupDotnetEnvironmentVariables, Exception:  {sys.exc_info()[0]}")
        return IsX86, -1

    return IsX86, 0       

def setupDotnetCoreEnvironmentVariables(applicationDepFolder, provisionFlag):
    #  <environmentVariables>
    #     <environmentVariable name="ASPNETCORE_ENVIRONMENT" value="Development" />
    #     <environmentVariable name="COMPLUS_ForceENC" value="1" />
    #   </environmentVariables>
    try:
        isProvisioned = provisionFlag.lower() == "true"
        logging.info('Setting up environment variables for dotnet core application started....');
        webconfigFile = os.path.join(applicationDepFolder, "web.config")
        if(not os.path.exists(webconfigFile)):
            logging.error(f'web.config file does not exist in the {applicationDepFolder}, Please check');
            return;

        backupFile = webconfigFile + ".virsec"
        if(not os.path.exists(backupFile)):
            copy(webconfigFile, backupFile)
        
        file = ET.parse(webconfigFile)
        #file = ET.parse(webconfigFile, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
        #file = ET.parse(webconfigFile, parser=ET.XMLParser(target=CommentedTreeBuilder())) 
        aspNetCore = file.find(".//aspNetCore")
        logging.info('aspNetCore section is found');
        if(aspNetCore is not None):
            logging.info('Searching environmentVariables section');
            existingEnvVars = aspNetCore.find(".//environmentVariables")
                
            if(existingEnvVars):
                logging.info('Environment variables is already present, overwriting the settings')
                isCORECLR_ENABLE_PROFILINGFound = False;
                isCORECLR_PROFILERFound = False;
                isCORECLR_PROFILER_PATH_64Found = False;
                isCORECLR_PROFILER_PATH_32Found = False;
                removedItems=[]
                for add in existingEnvVars:
                    name = add.get('name')
                    if(name.endswith('_vsp_renamed')):
                        if(not isProvisioned):
                            add.set('name', name.removesuffix('_vsp_renamed'))
                    elif(name.upper() == 'CORECLR_ENABLE_PROFILING'):
                        isCORECLR_ENABLE_PROFILINGFound = True;
                        if(isProvisioned):
                            value = add.get('value')
                            if (value and value.lower() != corProfilerFlag.lower()):
                                name = name + "_vsp_renamed"
                                add.set('name', name)
                                add = ET.SubElement(existingEnvVars, 'environmentVariable')
                                add.set('name', 'CORECLR_ENABLE_PROFILING')
                            add.set('value', corProfilerFlag)
                        else:
                            removedItems.append(add)
                    elif(name.upper() == 'CORECLR_PROFILER'):
                            isCORECLR_PROFILERFound = True
                            if(isProvisioned):
                                value = add.get('value')
                                if (value and value.lower() != corProfilerClsId.lower()):
                                    name = name + "_vsp_renamed"
                                    add.set('name', name)
                                    add = ET.SubElement(existingEnvVars, 'environmentVariable')
                                    add.set('name', 'CORECLR_PROFILER')
                                add.set('value', corProfilerClsId)
                            else:
                                removedItems.append(add)
                    elif(name.upper() == 'CORECLR_PROFILER_PATH_64'):
                            isCORECLR_PROFILER_PATH_64Found = True
                            if(isProvisioned):
                                value = add.get('value')
                                if (value and value.lower() != corProfilerPath64.lower()):
                                    name = name + "_vsp_renamed"
                                    add.set('name', name)
                                    add = ET.SubElement(existingEnvVars, 'environmentVariable')
                                    add.set('name', 'CORECLR_PROFILER_PATH_64')
                                add.set('value', corProfilerPath64)
                            else:
                                removedItems.append(add)
                    elif(name.upper() == 'CORECLR_PROFILER_PATH_32'):
                            isCORECLR_PROFILER_PATH_32Found = True
                            if(isProvisioned):
                                value = add.get('value')
                                if (value and value.lower() != corProfilerPath32.lower()):
                                    name = name + "_vsp_renamed"
                                    add.set('name', name)
                                    add = ET.SubElement(existingEnvVars, 'environmentVariable')
                                    add.set('name', 'CORECLR_PROFILER_PATH_32')
                                add.set('value', corProfilerPath32)
                            else:
                                removedItems.append(add)

                if(not isProvisioned):
                    for add in removedItems:    
                        existingEnvVars.remove(add)
                
                if(isProvisioned):
                    if(isCORECLR_ENABLE_PROFILINGFound == False):
                        coreProfilerFlag = ET.SubElement(existingEnvVars, 'environmentVariable')
                        coreProfilerFlag.attrib['name'] = 'CORECLR_ENABLE_PROFILING'
                        coreProfilerFlag.attrib['value'] = corProfilerFlag
                        
                    if(isCORECLR_PROFILERFound == False):
                        corProfiler = ET.SubElement(existingEnvVars, 'environmentVariable')
                        corProfiler.attrib['name'] = 'CORECLR_PROFILER'
                        corProfiler.attrib['value'] = corProfilerClsId

                    if(isCORECLR_PROFILER_PATH_64Found == False):
                        corProfilerX64 = ET.SubElement(existingEnvVars, 'environmentVariable')
                        corProfilerX64.attrib['name'] = 'CORECLR_PROFILER_PATH_64'
                        corProfilerX64.attrib['value'] = corProfilerPath64

                    if(isCORECLR_PROFILER_PATH_32Found == False):
                        corProfilerx86 = ET.SubElement(existingEnvVars, 'environmentVariable')
                        corProfilerx86.attrib['name'] = 'CORECLR_PROFILER_PATH_32'
                        corProfilerx86.attrib['value'] = corProfilerPath32
            else:
                if(isProvisioned):
                    if(existingEnvVars is not None):
                        aspNetCore.remove(existingEnvVars)
                    envVars = ET.SubElement(aspNetCore, 'environmentVariables')
                    coreProfilerFlag = ET.SubElement(envVars, 'environmentVariable')
                    coreProfilerFlag.attrib['name'] = 'CORECLR_ENABLE_PROFILING'
                    coreProfilerFlag.attrib['value'] = corProfilerFlag
                    corProfiler = ET.SubElement(envVars, 'environmentVariable')
                    corProfiler.attrib['name'] = 'CORECLR_PROFILER'
                    corProfiler.attrib['value'] = corProfilerClsId
                    corProfilerX64 = ET.SubElement(envVars, 'environmentVariable')
                    corProfilerX64.attrib['name'] = 'CORECLR_PROFILER_PATH_64'
                    corProfilerX64.attrib['value'] = corProfilerPath64
                    corProfilerx86 = ET.SubElement(envVars, 'environmentVariable')
                    corProfilerx86.attrib['name'] = 'CORECLR_PROFILER_PATH_32'
                    corProfilerx86.attrib['value'] = corProfilerPath32
            
            file.write(webconfigFile, encoding='utf-8', xml_declaration=True)
    except:
         logging.info(f'Setting up environment variables for dotnet core application failed. {sys.exc_info()[0]}');
         return False
    return True

def provDotnet(applicationType: str, applicationContext: str, applicationDepFolder: str, provisionFlag: int):
    status = True
    logging.info('-----------------------------------------------------------------------------------------------------------')
    logging.info('Provisioning started...')
    logging.info(f"applicationType      : {applicationType}")
    logging.info(f"applicationContext   : {applicationContext}")
    logging.info(f"applicationDepFolder : {applicationDepFolder}")
    logging.info(f"provisionFlag        : {provisionFlag}")
    if applicationType.lower() == '.net':
        isX86, ret = setupDotnetEnvironmentVariables(applicationDepFolder, provisionFlag)
        if ret == -1:
            status = False
        if provisionFlag.lower() == 'true':
            logging.info(f"IsX86: {isX86}")
            copyFiles(applicationDepFolder, applicationContext, isX86)
            logging.info('Provisioning is completed.')
        else:
            deleteFiles(applicationDepFolder)
            logging.info('Un-Provisioning is completed.')
    else:
        status = setupDotnetCoreEnvironmentVariables(applicationDepFolder, provisionFlag)
        if provisionFlag.lower() == 'true':
            copyVspFile(applicationContext, applicationDepFolder)
            logging.info('Provisioning is completed.')
        else:
            deleteVspFile(applicationDepFolder)
            logging.info('Un-Provisioning is completed.')
    logging.info('-----------------------------------------------------------------------------------------------------------')
    return status

def getContents(fileLoc):
     contents = []
     try:
        with open(fileLoc, "r") as f:
           contents = f.readlines()
           f.close()
     except EnvironmentError:
         logging.warning("failed reading conf file %s" % fileLoc)
     return contents

def putDeletedLines(webConfigFile , OrigContents, rootTag):
    newContents = getContents(webConfigFile)
    rootStartTag = "<"+ rootTag + ">"
    rootEndTag = "</"+ rootTag + ">"
    orgStartIndex = -1
    orgEndIndex = -1
    for i in range(0,len(OrigContents)):
        if rootStartTag in OrigContents[i]:
            orgStartIndex = i
        if rootEndTag in OrigContents[i]:
            orgEndIndex = i

    logging.debug("%s start index is %d"%(rootStartTag , orgStartIndex))
    logging.debug("%s end index is %d"%(rootEndTag , orgEndIndex))

    skipWriting = True
    # add contents from 0 to start index in new content
    if orgStartIndex != 0:
        for i in  range(0,orgStartIndex):
            newContents.insert(i, OrigContents[i])
            logging.debug("added contents %s at %d" % (OrigContents[i] , i))
            skipWriting = False

    if orgEndIndex + 1 != len(OrigContents) -1:
        newContents.append("\n")
        for i in  range(orgEndIndex + 1, len(OrigContents)):
            newContents.insert(len(newContents), OrigContents[i])
            logging.debug("added contents %s at %d " %(OrigContents[i], len(newContents)))
            skipWriting = False
        
    # Write back the updated contents
    if skipWriting is False:
        with open(webConfigFile, "w") as f:
           newContents = "".join(newContents)
           f.write(newContents)
           logging.debug("added deleted lines for %s" % webConfigFile)
           f.close()

def copy(src:str, dest:str):
    try:
        shutil.copy(src, dest)
    except shutil.Error as err:
        logging.critical(f'Copying {src} into {dest} is failed reason {err.strerror}')
    logging.info(f'Copying {src} into {dest} is done')
