alter session set container=cdb\$root;
alter user system identified by ${vncpwd} CONTAINER=ALL;
alter user sys identified by ${vncpwd} CONTAINER=ALL;
exit;