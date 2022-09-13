"""
Usage: 
    autoprov <action> <language> [argument 1] [argument 2] [argument 3] ...

Supported language:
    PHP 
        To provision PHP application 
            usage: autoprov prov php <doc root> <web server> <php version>
            example: autoprov prov php /var/www/html apache 7.3
        To clean-up PHP application 
            usage: autoprov clean php <doc root> <web server> <php version>
            example: autoprov clean php /var/www/html apache 7.3

    JAVA
        To provision java application
            usage: autoprov prov java <server-type> <startup-script-path> <app-context> <server-name>  <applicationType> <filterType> --instrumentationFilterClass <instrumentationFilterClass> <filterMethod> <filterPosition>
            example: autoprov prov java  "Tomcat" "/opt/tomcat/bin/setenv.sh" "webgoat" "" "" "" "" "" ""
        To  clean-up java application
            usage: autoprov prov java <server-type> <startup-script-path> <app-context> <server-name>  <applicationType> <filterType> --instrumentationFilterClass <instrumentationFilterClass> <filterMethod> <filterPosition>
            example: autoprov clean java  "Tomcat" "/opt/tomcat/bin/setenv.sh" "webgoat" "" "" "" "" "" ""

Usage:
    autoprov <action> <server-name>  <conf-path> <server-block> [argument 1] [argument 2] [argument 3] ...

Supported Servers:
    NGINX
        To prov nginx web server conf file
            usage: autoprov <action> nginx <conf-path> <server-block> <server-restart-command> <position-interger> <key:value>
            example: autoprov prov nginx /etc/nginx/conf.d http/server 'nginx -s reload' 0 'lua_package_path:"$prefix/?.lua;;"' 1 'lua_package_cpath:"$prefix/?.so;;"'
        To clean-up conf file
            usage: autoprov clean nginx /etc/nginx/conf.d http/server 'nginx -s reload' 0 'lua_package_path:"$prefix/?.lua;;"' 1 'lua_package_cpath:"$prefix/?.so;;"'
            example: autoprov clean php /var/www/html apache 7.3
        Note:- use find instead of conf-path to find the conf file at runtime using nginx specifig command
    HTTPD
        To prov httpd conf file
            usage: autoprov <action> httpd <conf-path> <server-restart-command> <lines-to-add> ...
            example: autoprov prov httpd /etc/httpd/conf.d 'service httpd restart' "LoadFile /usr/lib64/httpd/modules/libiae_encode.so' 'LoadFile /usr/lib64/httpd/modules/libIAE-Assist.so' 'LoadFile /usr/lib64/httpd/modules/libmutlipart.so'
        To cean-up conf file
            usage: autoprov <action> httpd <conf-path> <server-restart-command> <lines-to-add> ...
            example: autoprov clean httpd /etc/httpd/conf.d 'service httpd restart' "LoadFile /usr/lib64/httpd/modules/libiae_encode.so" "LoadFile /usr/lib64/httpd/modules/libIAE-Assist.so LoadFile" "/usr/lib64/httpd/modules/libmutlipart.so"
        Note:- use find instead of conf-path to find the conf file at runtime using http/apache specifig command
"""
def usage(msg):
    print(msg)
    print(__doc__)

