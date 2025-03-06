create user admin identified by "Welcome23ai";

grant dba to admin;

grant apex_administrator_role to admin;

grant pdb_dba to admin;

grant cdb_dba to admin;


begin
   ords_admin.enable_schema(
      p_enabled             => true,
      p_schema              => 'admin',
      p_url_mapping_type    => 'BASE_PATH',
      p_url_mapping_pattern => 'admin',
      p_auto_rest_auth      => null
   );
   commit;
end;
/

commit;

exit;