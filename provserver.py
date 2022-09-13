import sys
import autoprov.ProcessUtil as ProcessUtil
import os
import autoprov.nginx as nginx
import autoprov.autoprov as autoprov
import logging

NGINX_MODULE_COMMON_LOC  = "/opt/virsec/ewaf/nginx/nginx-lua-module/"
NGINX_LOAD_MODULE_HDR    = "load_module "
NGINX_NDK_MODULE_NAME    = "ndk_http_module.so"
NGINX_LUA_MODULE_NAME    = "ngx_http_lua_module.so"
APACHE_DEFALTE_STR       = "SetOutputFilter VS_RESPONSE"
APACHE_DEFLATE_CONF_LOC  = "/etc/apache2/mods-enabled/deflate.conf"
APACHE_VS_RESPONSE_STR   = "VS_RESPONSE;"
APACHE_VS_RESPONSE       = "VS_RESPONSE"

apacheSupportedResponseTypes = ["application/xhtml+xml",
"application/json",
"application/xml",
"application/x-www-form-urlencoded",
"text/html",
"text/xml",
"text/plain"]

def getArgs(isNginx , *argv):
    argc = len(argv)
    arguments = list()

    for arg in argv:
       arguments.append(arg)

    if isNginx == True:
        if len(arguments) % 2 != 0:
            logging.warning("arguments given are invalid")
            return list()

    return arguments

def updateBlock(action, blockInstance, keys, values, index):
    skip = True
    for x in range(0, len(values)): 
        i = x
        if action == "clean":
              i = len(index) - x - 1

        inputKey = keys[i]
        inputValue = values[i]

        # it means we need to update/clean the file from bottom
        # need to check the negetive index logic
        negIndex = False
        if index[i] < 0:
            blockSize = len(blockInstance.children)
            i = blockSize - 1
            negIndex = True

        savedKey = blockInstance.children[i].name
        savedValue = blockInstance.children[i].value

        if savedKey in keys and savedValue in values:
            print("Fount already saved entry with key %s and value %s" % (savedKey , savedValue))
            if action == "prov":
                continue
        elif action == "clean":
            print("Fount mismatch with saved entry with key %s and value %s" % (savedKey , savedValue))
            continue

        if action == "prov":
            if negIndex:
                blockInstance.children.append(nginx.Key(inputKey, inputValue))
            else:
                blockInstance.children.insert(i, nginx.Key(inputKey, inputValue))
            print("Success: Added to entry key %s and vlaue %s" % (inputKey , inputValue))
            skip = False

        elif action == "clean":
            del blockInstance.children[i]
            print("Success: Deleted entry having key %s and value %s" % (savedKey, savedValue))
            skip = False

    return skip

def provNginx(action, confLocation, restartCmd, serverBlock, *argv):
    isNginx = True
    arguments = getArgs(isNginx, *argv)
    logging.debug("got arguments %s" % str(argv))
    if confLocation != "find" and not os.path.isfile(confLocation):
        logging.info("Configuration file %s is not present" % confLocation)
        return False

    if confLocation == "find":
       confLocation = ProcessUtil.findConfLocation("Nginx", restartCmd)
    
    if confLocation == "None":
        logging.warning("conf file not found")
        return False

    logging.info("Success : Conf file found at location %s" % confLocation)

    # try installing lua pks for debian and alpine plarforms
    ProcessUtil.installPkgs()

    # update nginx for loading lua module for few platforms
    updateConfNginx(action, confLocation, restartCmd)

    c = nginx.loadf(confLocation)

    index = list()
    keys = list()
    values = list()
    # create the key value pairs from the arguments
    for i in range(0, len(arguments), 2):
        index.append(int(arguments[i]))
        keyValPair = arguments[i + 1].split(':')
        
        if len(keyValPair) != 2:
            logging.warning("key:value are not given in correct manner")
            return False
        
        keys.append(keyValPair[0])
        values.append(keyValPair[1])

    if len(keys) != len(values) and len(values) != len(index):
        logging.warning("index key:value are not given in correct manner")
        return False

    skipWriting = True
    # http:server:<serverNumber>
    if ':' in serverBlock:
        tree = serverBlock.split(':')
        if len(tree) != 3:
             logging.warning("key:value are not given in correct manner")
             return False
        if tree[0] == "http" and tree[1] == "server" and tree[2] >= 0:
            i = 0
            toSkip = 1
            for entry in c.http.children:
                if entry.name == tree[1]:
                    if toSkip == int(tree[2]):
                        # found the required server block in http context
                        # update that server block
                        skipWriting = updateBlock(action, c.http.children[i], keys, values, index)
                    else:
                        toSkip = toSkip + 1
                i = i + 1
        else:
            logging.warning("block paramter is not given in correct manner")
            return False

    elif serverBlock == "http":
        skipWriting = updateBlock(action, c.http, keys, values, index)
                
    elif serverBlock == "server":
        skipWriting = updateBlock(action, c.server, keys, values, index)
        
    # save the updated file
    if skipWriting == False:
        nginx.dumpf(c, confLocation)
        print("Saved file at location %s" % confLocation)
        # check if the config is updated properly or not, testConfFile will error out if any error in config file
        if action == "prov":
           if ProcessUtil.testConfFile("Nginx"):
               print("Updated conf file %s is fine" % confLocation)
           else:
               # we already know the confLocation
               provNginx("clean", confLocation, serverBlock, *argv)
               logging.critical("Provision failed, reverted back the changes made at %s" % confLocation)
               return False
    else:
        logging.debug("Skipped updating file at location %s" % confLocation)

    return True

def provHttpd(action, confLocation, restartCmd, *argv):
    isNginx = False
    arguments = getArgs(isNginx, *argv)
    logging.debug("got arguments %s" % str(argv))

    if confLocation == "find":
       confLocation = ProcessUtil.findConfLocation("Apache", restartCmd)

    if confLocation == "None":
        logging.critical("confLocation not found file at location %s" % confLocation)
        return False

    skipWriting = True    

    try:
        with open(confLocation, "r") as f:
           contents = f.readlines()
    except EnvironmentError:
        logging.critical("failed reading conf file %s" % confLocation)
        return False

    for index in range(0, len(arguments)):
        # Just appending at the begning of the conf file
        if action == "prov":
            savedContent = contents[index]
            inputContent = arguments[index]
            if inputContent in savedContent:
                logging.debug("Content Already present %s at index %d" % (savedContent, index))
                continue
            else:
                contents.insert(index, inputContent + '\n')
                logging.info("success: Added content %s at index %d" % (inputContent, index))
                skipWriting = False
        
        # Removing form the begning of the conf fil
        elif action == "clean":
           reverseIndex = len(arguments) - index - 1
           savedContent = contents[reverseIndex] # has extra '\n' character
           inputContent = arguments[reverseIndex]
           if inputContent in savedContent:
               contents.pop(reverseIndex)
               logging.info("Success: Removed content %s" % inputContent)
               skipWriting = False
           else:
               logging.critical("Failed: deleting, content %s is not matching with saved content %s" % (inputContent, savedContent))

    if skipWriting:
        logging.debug("Skipped updating file at location %s" % confLocation)
    else:
        if action == "prov":
            if ProcessUtil.testConfFile("Apache"):
                logging.info("Updated conf file %s is fine" % confLocation)
            else:
                # we already know the confLocation
                provHttpd("clean" , True)
                logging.critical("Provision failed, reverted back the changes made at %s" % confLocation)
                return
            
            # Before writing check if deflate needs to be added               
            # Add defalte if not present
            if "ubuntu" in ProcessUtil.getDistributionName():
                if ProcessUtil.checkDeflate(restartCmd) == False:
                    if APACHE_DEFALTE_STR in contents[len(arguments)]:
                        logging.info("Content Already present %s" % APACHE_DEFALTE_STR)
                    elif APACHE_DEFALTE_STR not in contents[len(arguments)]:
                        contents.insert(len(arguments), APACHE_DEFALTE_STR + '\n')
                        logging.info("Success: Added content %s" %  APACHE_DEFALTE_STR)
                else:
                    # Update the deflate conf file
                    logging.debug("defalte is present")
                    updateDeflateConf(action)

        elif action == "clean":
            if "ubuntu" in ProcessUtil.getDistributionName():
                # Remove defalte if not present
                if ProcessUtil.checkDeflate(restartCmd) == False:
                    if APACHE_DEFALTE_STR in contents[0]:
                        logging.info("Success: Removed content %s at index 0" % APACHE_DEFALTE_STR)
                        contents.pop(0)
                    else:
                        logging.warning("%s is not present at index 0" % APACHE_DEFALTE_STR)
                else:
                    # revert back the deflate conf
                    updateDeflateConf(action)

        # Write back the updated contents
        with open(confLocation, "w") as f:
           contents = "".join(contents)
           f.write(contents)
           f.close()
           print("Success: update file at location %s" % confLocation)
           # check if the config is updated properly or not, testConfFile will error out if any error in config file
           if action == "prov":
               if ProcessUtil.testConfFile("Apache"):
                   print("Updated conf file %s is fine" % confLocation)
               else:
                   # we already know the confLocation
                   provHttpd("clean" , True)
                   logging.critical("Provision failed, reverted back the changes made at %s" % confLocation)
                   return False

def updateConfNginx(action, confLocation, restartCmd):
    if checkSkipUdatingNginxConf(restartCmd) == True:
        print("Info: skipping lua module addition for conf file %s" % confLocation)
        return

    skipWriting = True    
    # Need only 2 line to be added/deleted
    len = 2
    try:
        with open(confLocation, "r") as f:
           contents = f.readlines()
    except EnvironmentError:
        err = "Error: reading " + confLocation
        logging.warning(err)
        return False

    # lines to add/delete inside conf file 
    lines = list()
    path = NGINX_MODULE_COMMON_LOC
    # get the distribution name
    osName = ProcessUtil.getDistributionName();
    # get distribution version
    osVersion = ProcessUtil.getDistributionVersion();
    # get the nginx version
    nginxVersion = ProcessUtil.getNginxVersion();

    if "ubuntu" in osName and "16" in osVersion:
        path = "/opt/virsec/ewaf/nginx/"
    else:
        if osName == "None":
            logging.warning("Error: distribution name not found")
            return False
        path += osName 

        if osVersion == "None":
            logging.warning("Error: distribution version not found")
            return False
        path += osVersion + "/"

        if nginxVersion == "None":
            logging.warning("Error: nginx version not found")
            return False

        path += nginxVersion + "/"
    
    print("Success: Built path is %s" % path);

    # check if location of .so file are present or not
    ndkLoc = path + NGINX_NDK_MODULE_NAME
    luaLoc = path + NGINX_LUA_MODULE_NAME
    if os.path.isfile(ndkLoc) and os.path.isfile(luaLoc):
        print("Success: ndk and lua modules are present " 
              "at path %s OR %s" % (ndkLoc, luaLoc))
    else:
        error = "Error: path " + ndkLoc + " and " + luaLoc + " are not present"
        logging.warning(error)
        return False

    lines.append(NGINX_LOAD_MODULE_HDR + ndkLoc + ";")
    lines.append(NGINX_LOAD_MODULE_HDR + luaLoc + ";")
    print("lines to add %s , %s" % (lines[0], lines[1]))

    for index in range(0, len):
        # appending at the begning of the conf file
        if action == "prov":
            savedContent = contents[index]
            inputContent = lines[index]
            if inputContent in savedContent:
                logging.info("Content Already present %s at index %d" % (savedContent, index))
                continue
            else:
                contents.insert(index, inputContent + '\n')
                logging.info("Success: Added content %s at index %d" % (inputContent, index))
                skipWriting = False
        
        # removing form the begning of the conf file
        elif action == "clean":
           reverseIndex = len - index - 1
           savedContent = contents[reverseIndex] # has extra '\n' character
           inputContent = lines[reverseIndex]
           if inputContent in savedContent:
               contents.pop(reverseIndex)
               print("Success: Removed content %s" % inputContent)
               skipWriting = False
           else:
               logging.critical("Failed: deleting, content %s is not matching with saved content %s" % (inputContent, savedContent))

    if skipWriting:
        print("Skipped updating file at location %s" % confLocation)
    else:
        # write back the updated contents
        with open(confLocation, "w") as f:
           contents = "".join(contents)
           f.write(contents)
           f.close()
           logging.info("Success: update file at location %s" % confLocation)
           if action == "prov":
               ProcessUtil.loadLdConfigEwaf(path)
           elif action == "clean":
               ProcessUtil.removeLdConfigEwaf()

def checkSkipUdatingNginxConf(restartCmd):
    osName = ProcessUtil.getDistributionName();
    if "openresty" in restartCmd:
        logging.info("skipped lua module addition, reason: openresty command is in use")
        return True
    if "alpine" in osName or "debian" in osName:
        logging.info("skipped lua module addition, reason: osName is %s" % osName)
        return True
    return False

def updateDeflateConf(action):
    logging.debug("Trying updating deflate conf file %s" % APACHE_DEFLATE_CONF_LOC)
    skipWriting = True 
    try:
        with open(APACHE_DEFLATE_CONF_LOC, "r") as f:
           contents = f.readlines()
    except EnvironmentError:
        err = "Error: reading " + APACHE_DEFLATE_CONF_LOC
        logging.critical(err)
        return False
    
    if action == "prov":
        # add missing apache supported response types
        visitedLineNo = []
        temp = apacheSupportedResponseTypes
        for child in apacheSupportedResponseTypes:
            for index, line in enumerate(contents):
                if child in line:
                    if index not in visitedLineNo:
                        visitedLineNo.append(index)
                        temp.remove(child)
                    else:
                        temp.remove(child)

        # add the remaining supported response types
        for child in temp:
            if len(visitedLineNo) != 0:
                contents.insert(visitedLineNo[0], "AddOutputFilterByType VS_RESPONSE " + child + "\n")
                print("Success: added new content %s" % contents[visitedLineNo[0]])

    for index in reversed(range(len(contents))):
        foundLoc = contents[index].find("DEFLATE")
        if foundLoc >= 0:
             print("Trying Updating deflate conf line %s" % contents[index])
             if "prov" in action:
                 # add APACHE_VS_RESPONSE_STR for this line
                 contents[index] = ProcessUtil.insertStr(contents[index], APACHE_VS_RESPONSE_STR, foundLoc)
                 print("Success: Added %s updated line is %s" % (APACHE_VS_RESPONSE_STR, contents[index]))
                 skipWriting = False
        if "clean" in action:
             # revert APACHE_VS_RESPONSE_STR for this line
             if APACHE_VS_RESPONSE_STR in contents[index]:
                 contents[index] = contents[index].replace(APACHE_VS_RESPONSE_STR, '')
             elif APACHE_VS_RESPONSE in contents[index]:
                 print("Success: Removed %s updated line is %s" % (APACHE_VS_RESPONSE, contents[index]))
                 contents.pop(index)
                 skipWriting = False
        

    if skipWriting:
        print("Skipped updating file at location %s" % APACHE_DEFLATE_CONF_LOC)
    else:
        # write back the updated contents
        with open(APACHE_DEFLATE_CONF_LOC, "w") as f:
           contents = "".join(contents)
           f.write(contents)
           f.close()
           print("Success: update file at location %s" % APACHE_DEFLATE_CONF_LOC)

    return True