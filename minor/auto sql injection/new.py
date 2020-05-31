import urllib2
import time
import re
#	error types	errors

SQLeD ={ 'MySQL' : 'error in your SQL syntax',
	'SQLi_err' : 'access shop category information',
	'MySQL_Valid_Argument' : 'supplied argument is not a valid MySQL result resource in',
	'MySQL_fetch' : 'mysql_fetch_assoc()',
	'MySQL_array' : 'mysql_free_result()',
	'MySQL_fetch_array' : 'mysql_fetch_array()',
	'MySQL_result' : 'mysql_free_result()',
	'MySQL_start' : 'session_start()',
	'MySQL' : 'getimagesize()',
	'MySQL_call' : 'Call to a member function',
	'Oracle' : 'Microsoft OLE DB Provider for Oracle',
	'Mysql_re' : 'Warning:require()',
	'MySQL_11' : 'array_merge()',
	'MySQL' : 'mySQl_query()',
	'Oracle' : 'ORA-01756',
	'MiscError' : 'SQL Error',
	'MiscError' : 'mysql_fetch_row',
	'MiscError' : 'num-rows',
	'JDBC_CFM' : 'Error Executing Database Query',
	'JDBC_CFM2' : 'SQLServer JDBC Driver',
	'MSSQL_OLEdb' : 'Microsoft OLE Db Provider for SQL Server',
	'MSSQL_Uqm' : 'Unclosed quotation mark',
	'MS-Access_ODBC' : 'ODBC Microsoft Access Driver',
	'Postgrey_error' : 'an error occured',
	'SQL_error' : 'Unknown Column',
	'MS-Access_JETdb' : 'Microsoft JET Database'}

print"\nI.E. www.xyz.com/top10/index.php?id="
u=raw_input("\n Enter website (with http://):")
p="'"
host=u+p
print "\n(+)URL WITH PAYLOAD :",host

for type,eMSG in SQLeD.items():
    try:
        r=urllib2.urlopen(host.read())
        if r.search(eMSG,r):
            print "\n[+]SQL INJECTION BUG FOUND ERROR TYPE IS:", type
            break
        else:
            print"\ntrying",type
    except:
        "PLEASE START INTERNET"
