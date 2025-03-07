#!/bin/bash

echo $vncpwd | tee /home/opc/compose2cloud/composescript/envvar/.vncpwd > /dev/null
echo vncpwd=$(cat /home/opc/compose2cloud/composescript/envvar/.vncpwd) > /home/opc/compose2cloud/composescript/envvar/.vncpwd.env


# Load environment variables
source /home/opc/compose2cloud/composescript/envvar/.vncpwd.env

# Run SQL script to update passwords
sqlplus -s "sys/${vncpwd}@localhost:1521/freepdb1 as sysdba" <<EOF
ALTER SESSION SET CONTAINER=CDB\$ROOT;
ALTER USER SYSTEM IDENTIFIED BY '${vncpwd}' CONTAINER=ALL;
ALTER USER SYS IDENTIFIED BY '${vncpwd}' CONTAINER=ALL;
EXIT;
EOF
