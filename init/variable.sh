#!/bin/bash


public_ip=$(curl -s ifconfig.me)
if [[ ${#public_ip} -le 5 || ${public_ip} =~ '<html>' ]]; then
  public_ip="127.0.0.1"
fi


vncpwd=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/vncpwd)

if [[ ${#vncpwd} -ne 10 ]]; then
  vncpwd="Welcome23ai"
fi

#workshopfiles must be a URL pointing to a zip file
dbconnection=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/dbconnection|tr -d ' ')

if [[ ${#dbconnection} -le 5 || ${dbconnection} =~ '<html>' ]]; then
  dbconnection="localhost:1521/freepdb1"
fi

#workshopfiles must be a URL pointing to a zip file
mongodbapi=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/mongodbapi|tr -d ' ')

if [[ ${#mongodbapi} -le 5 || ${mongodbapi} =~ '<html>' ]]; then
  mongodbapi="localhost:1521/freepdb1"
fi

#workshopfiles must be a URL pointing to a zip file
graphurl=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/graphurl|tr -d ' ')

if [[ ${#graphurl} -le 5 || ${graphurl} =~ '<html>' ]]; then
  graphurl="localhost:1521/freepdb1"
fi

#workshopfiles must be a URL pointing to a zip file
dbpassword=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/dbpassword)

if [[ ${#dbpassword} -le 5 || ${dbpassword} =~ '<html>' ]]; then
  dbpassword="Thisisapassword33##"
fi

pem_key=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/pem_key)

if [[ ${#pem_key} -le 5 || ${pem_key} =~ '<html>' ]]; then
  pem_key="-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDOaaqcdrLy0Bf8
kRVBSAv5tUhOUNOVg6NmGC6rCFcZuR/LhLz/Aa0Oz/NIn97vO411p0EctxfVhkds
GtWOkZLq1givQjbIxkagwOocRxrBXhKBh8s9d2zs01rSfVoshv7b0xQUB3k5CPDG
6+xweIDgbrVye2TBC925M6e0ZkB4US11lYg2nsb7+zupN2nMHDdD8L1Bg7qEay90
XahL5v8wfGFeNBDjCACqwSuiIC1MvyXNkyFfOeFbFIc9gj0McIFFwvL0hLIHgAdV
QfdSQwAkuVENZg0acWFFBuZmEGK+2Mhs5+KC0FhTL3+JwyS+fJ1eXMEANc+8UAxa
PFB1cyBJAgMBAAECggEAEOhAlnWWEZPIPTLElQ7x1Su7TxfphtgMIq0VKIMDwGqE
n1LheLlSS7HunWqj9ABSpVoUeCXKrN2lfMZDaxzDNhtfRXzE2EP+bcUzf+q2lzNt
jGDbPc8KE+l5iV+FavuJRWgIH15f2HNCJqcVPD6wnsGOuQCAt5vRVu3TXTBZdElb
PDMN3rVkfUSSNIMh8LN9/y0LVRhcVpkKbKYwLSeNma2V+DQ7HQ/K+gvVyUFs2cgJ
/Yn+d7vku7pzr3EBTYKcLno/6AIedgKOmUukiQdcsicpJ3C7Wcq5UHhPq0lvC1Gw
aFc9CuEmMB4XhzqNipS9S4j6zw28frgi2PiysidMAQKBgQDyQ0QXrY0ddVvwrxQG
tRor+mIUr8u1QZ3e60GNv99N368kEBaHxTfd6DttQtKdGP/dv7kMboxQAWkVsYpV
7nbiEDL1d2XVXhC7y/dYadaRaIxHPgz3nvHVG/Chip0cO/3ZEx/9i3DS346Ad/Vb
Kq3psIoOdxgipjK7FcbkiT3sAQKBgQDaHf6sFJOKGmhC3CxqGiQK9RknEb4Obl2a
LppQkvhCU5m8ADAnp/vyuJB+Wf/a6KwXcw3v7DUz2bGTYAy7MF0CJEK4yVskZ1ZJ
+b4JNEoiLoXbLuqA2M3RXBonqry03n2AaDGdRbeEGonj3Zk4qxJ6zADCqi+faejb
QY81E1rUSQKBgQDmZoLD4hJrCco+xMNO/b2+RYoyEl6yK41xDFxz6x78eNegfIxw
42eWa97YssyLC9OLmWLsJ9bZ3/2I3CisQPZfWPid6se2fJd9gyXhuAaQk9WVi7XZ
ahikjMX1XFa/G274m++4uny6kFJ+a5e09Iohzfv+ddVGXrmwo61cfAmgAQKBgQDB
/Bc5l/s3whCkFgjyPFl93UoHc0Iit4lLzNK1gmCFLLD3gPtS6ZWr4vWvSf/BA1m6
aTsl/F+8w4mo1q279WFivDkS+xGyKK2XkSOwL+8Ww2WM8AbjnO4/mrgwOysleRMJ
FqG5i/2Q4cFtBPJ2cb83syOh/ZXpI1pTVdU1kQcg8QKBgQCKPKYXyu3WHEXzNy31
Rue5JHve2KcumGHO1L7f3h/kLAW9O4+2H6HJ+wVar1PcgB5+iBsxuuS8KK6MJnVK
x2lNc6iHzyOlAAKm2IALwWBvM4aaPFQfdAcgcrBd/wrW6CG7icIiag3NJz75GVs8
5o7Bul/qetmK0Q1Od2tS6xdsyA==
-----END PRIVATE KEY-----
OCI_API_KEY"
fi

pem_key_fingerprint=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/pem_key_fingerprint)

if [[ ${#pem_key_fingerprint} -le 5 || ${pem_key_fingerprint} =~ '<html>' ]]; then
  pem_key_fingerprint="df:9e:5a:17:e2:9b:d1:77:82:e2:56:13:e7:68:f3:fc"
fi

user_ocid=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/user_ocid)

if [[ ${#user_ocid} -le 5 || ${user_ocid} =~ '<html>' ]]; then
  user_ocid="ocid1.user.oc1..aaaaaaaacmu46j3hpsaa7hejhpunvsdv4b4bbljxcte2g4btazpilgaouibq"
fi

tenancy_ocid=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/tenancy_ocid)

if [[ ${#tenancy_ocid} -le 5 || ${tenancy_ocid} =~ '<html>' ]]; then
  tenancy_ocid="ocid1.tenancy.oc1..aaaaaaaadakrcgscm652scrcup2kyze3ahrwstffmmcovlfbepsmdvjsnkxq"
fi

region_identifier=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/region_identifier)

if [[ ${#region_identifier} -le 5 || ${region_identifier} =~ '<html>' ]]; then
  region_identifier="us-chicago-1"
fi

compartment_ocid=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/compartment_ocid)

if [[ ${#compartment_ocid} -le 5 || ${compartment_ocid} =~ '<html>' ]]; then
  compartment_ocid="ocid1.compartment.oc1..aaaaaaaapbmmkxib5ugzymobtx2hhiblbv3inme22o6njkg6ngno4rqaacxq"
fi

#workshopfiles must be a URL pointing to a zip file
workshopfiles=$(curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/workshopfiles)

if [[ ${#workshopfiles} -ne 10 ]]; then
  workshopfiles="https://c4u04.objectstorage.us-ashburn-1.oci.customer-oci.com/p/EcTjWk2IuZPZeNnD_fYMcgUhdNDIDA6rt9gaFj_WZMiL7VvxPBNMY60837hu5hga/n/c4u04/b/livelabsfiles/o/labfiles/vec_chunk.zip"
fi
