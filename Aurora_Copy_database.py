# -*- coding: utf-8 -*-
import json
from pprint import pprint
import sys,os
import pymysql
from sshtunnel import SSHTunnelForwarder 
import time,datetime
import codecs
from base64 import b64encode,b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import blake2b
import json

def encrypt_mytext(mytext,input_key):
    h = blake2b(digest_size=16)
    h.update(input_key.encode())
    key=h.hexdigest()
    #print(key)
    data=str(mytext)+" "
    cipher = AES.new(b64decode(key), AES.MODE_CBC, iv=b'0123456789abcdef')
    padded_data = pad(data.encode("utf-8"), cipher.block_size)
    encrypt_text = cipher.encrypt(padded_data)
    #print(encrypt_text)    
    return b64encode(encrypt_text).decode("utf-8")


def decrypt_mytext(encrypt_text,input_key):
    #print(ciphertext)    
    h = blake2b(digest_size=16)
    h.update(input_key.encode())
    key=h.hexdigest()
    #print(key)
    ciphertext = b64decode(encrypt_text.encode("utf-8"))
    cipher= AES.new(b64decode(key), AES.MODE_CBC, iv=b'0123456789abcdef')
    decrypt_text=str(cipher.decrypt(ciphertext).decode("utf-8")).split(' ')[0]
    return decrypt_text

def read_conn_info(file_name):
    f = open(file_name, 'r')
    line = f.readline()
    encrypt_json=json.loads(line)
    input_enc_key=input("enc key: ")
    server_infos_dec={}
    for key,value1 in encrypt_json.items():    
        dec_key=decrypt_mytext(key,input_enc_key)
        server_infos_dec[dec_key]={}
        for key2,value2 in value1.items():
            dec_key2=decrypt_mytext(key2,input_enc_key)
            dec_value2=decrypt_mytext(value2,input_enc_key)
            server_infos_dec[dec_key][dec_key2]=dec_value2    
    return server_infos_dec

def get_input_val(input_type):
    while True:
        input_val=input(input_type+" 입력하세요: ")
        if(input_val != ''):
            return input_val
        print("공백입력은 안됩니다. 다시 입력해주세요.")

def InputNumber(min_number,max_number):
    while True:
        try:
            number = int(input("숫자를 입력하세요: "))
            if(number >=min_number and number <= max_number):
                return number
            
            print(str(min_number)+"~"+str(max_number)+"까지 입력")
        except Exception as ex:
            continue


def get_server_info(server_infos):
    '''
    print("다시 입력은 AGAIN_")
    input_list=["source_bastion_ip",
                "source_bastion_user",
                "source_bastion_pwd",
                "source_endpoint",
                "source_db_user",
                "source_db_pwd",
                "target_bastion_ip",
                "target_bastion_user",
                "target_bastion_pwd",
                "target_endpoint",
                "target_db_user",
                "target_db_pwd"]
    i=0
    server_info={}
    while i < len(input_list) :
        input_val=get_input_val(input_list[i])
        if(input_val=="AGAIN_"):
            i=0
            continue
        server_info[input_list[i]] = input_val
        i=i+1
    '''
    for key,value in server_infos.items():
        print(key)
    
    source_server = get_input_val("source_server")
    target_server = get_input_val("target_server")
    server_info={}
    server_info["source_bastion_ip"]=server_infos[source_server]["source_bastion_ip"]
    server_info["source_bastion_user"]=server_infos[source_server]["source_bastion_user"]
    server_info["source_bastion_pwd"]=server_infos[source_server]["source_bastion_pwd"]
    server_info["source_endpoint"]=server_infos[source_server]["source_endpoint"]
    server_info["source_db_user"]=server_infos[source_server]["source_db_user"]
    server_info["source_db_pwd"]=server_infos[source_server]["source_db_pwd"]
    server_info["target_bastion_ip"]=server_infos[target_server]["source_bastion_ip"]
    server_info["target_bastion_user"]=server_infos[target_server]["source_bastion_user"]
    server_info["target_bastion_pwd"]=server_infos[target_server]["source_bastion_pwd"]
    server_info["target_endpoint"]=server_infos[target_server]["source_endpoint"]
    server_info["target_db_user"]=server_infos[target_server]["source_db_user"]
    server_info["target_db_pwd"]=server_infos[target_server]["source_db_pwd"]
    return server_info

def get_connect_info(server_infos):
    '''
    print("다시 입력은 AGAIN_")
    input_list=["source_endpoint",
                "source_db_user",
                "source_db_pwd",
                "target_endpoint",
                "target_db_user",
                "target_db_pwd"]
    i=0
    server_info={}
    while i < len(input_list) :
        input_val=get_input_val(input_list[i])
        if(input_val=="AGAIN_"):
            i=0
            continue
        server_info[input_list[i]] = input_val
        i=i+1
    '''
    for key,value in server_infos.items():
        print(key)
    source_server = get_input_val("source_server")
    target_server = get_input_val("target_server")
    server_info={}
    server_info["source_endpoint"]=server_infos[source_server]["source_endpoint"]
    server_info["source_db_user"]=server_infos[source_server]["source_db_user"]
    server_info["source_db_pwd"]=server_infos[source_server]["source_db_pwd"]
    server_info["target_endpoint"]=server_infos[target_server]["source_endpoint"]
    server_info["target_db_user"]=server_infos[target_server]["source_db_user"]
    server_info["target_db_pwd"]=server_infos[target_server]["source_db_pwd"]

    return server_info

def MainMenu():
    print("###################################################################")
    print("  1. DB SCHEMA COPY")
    print("  2. TABLE COPY")
    print("  3. USER COPY")
    print("  4. EXIT")

    input_val = InputNumber(1,4)
    print("###################################################################")

    return input_val
def IsChangeWord():
    print("###################################################################")
    print("  1. 스키마 스크립트 변경")
    print("  2. 스크립트 전체 변경")
    print("  3. 변경없음")
    print("  4. 초기메뉴")
    input_val = InputNumber(1,4)
    print("###################################################################")

    return input_val

def IsGrantChangeWord():
    print("###################################################################")
    print("  1. GRANT 변경")
    print("  2. 변경없음")
    input_val = InputNumber(1,2)
    print("###################################################################")
    return input_val

def IsAllSchema():
    print("###################################################################")
    print("  1. 스키마 전체")
    print("  2. 스키마 선택")
    input_val = InputNumber(1,2)
    print("###################################################################")
    return input_val
def IsDataMig(menu_number):
    print("###################################################################")
    print("  1. DDL 및 DATA")
    print("  2. DDL")
    print("  3. DATA")
    input_val = InputNumber(1,3)
    print("###################################################################")
    if(input_val == 1 and menu_number==1):
        return " --routines --max_allowed_packet=500M "
    elif(input_val == 2 and menu_number==1):
        return "--no-data --routines  --max_allowed_packet=500M "
    elif(input_val == 2 and menu_number==2):
        return "--no-data  --max_allowed_packet=500M "
    elif(input_val==3):
        return "--no-create-info --max_allowed_packet=500M "
    else:
        return " --max_allowed_packet=500M "

def IsAllTable():
    print("###################################################################")
    print("  1. 테이블 전체")
    print("  2. 테이블 선택")
    input_val = InputNumber(1,2)
    print("###################################################################")

    return input_val

def IsAllUser():
    print("###################################################################")
    print("  1. USER 전체")
    print("  2. USER 선택")
    input_val = InputNumber(1,2)
    print("###################################################################")
    return input_val    

def IsUseTunnel():
    print("###################################################################")
    print("  1. 터널링사용")
    print("  2. 터널링사용 안함")
    input_val = InputNumber(1,2)
    print("###################################################################")
    return input_val       

def getChangeWord():

    change_word_list=[]

    while True:
        print("변경전값과 변경될값을 입력해주세요. ")
        print("종료를 원하시면 변경전값에 QUIT_ 입력")
        print("변경 초기화를 원하시면 변경전값에 AGAIN_ 입력")
        while True:
            old_str=str(get_input_val("변경전값:"))
            if(old_str == "QUIT_"):
                #print(change_word_list)
                #print(len(change_word_list))
                return change_word_list
            elif(old_str == "AGAIN_"):
                print("이전 입력값은 모두 삭제 됩니다.")
                change_word_list.clear()
                change_word_list = []
                continue
            new_str=str(get_input_val("변경될값:"))
            print("###################################################################")
            change_word_list.extend([[old_str,new_str]])
            #print(len(change_word_list))

def InputSchemaList(source_schema_list):

    schema_list=[]
    check_list=""
    for schema in source_schema_list:
        check_list=check_list + " " + schema[0]

    while True:
        print("스키마입력")
        print("종료를 원하시면 입력값에 QUIT_ 입력")
        print("변경 초기화를 원하시면 입력값에 AGAIN_ 입력")
        while True:
            schema=str(get_input_val("입력값:"))
            
            if(schema == "QUIT_"):
                return schema_list
            elif(schema == "AGAIN_"):
                print("이전 입력값은 모두 삭제 됩니다.")
                schema_list.clear()
                schema_list = []
                continue
            
            if(schema in check_list):
                schema_list.extend([schema])
            else:
                print("스키마목록에 없는 스키마입니다.")
def InputUserList(user_list):

    input_user_list=[]
    check_list=""
    for user in user_list:
        check_list=check_list + " " + user[0]

    while True:
        print("USER입력")
        print("종료를 원하시면 입력값에 QUIT_ 입력")
        print("변경 초기화를 원하시면 입력값에 AGAIN_ 입력")
        while True:
            user=str(get_input_val("입력값:"))
            
            if(user == "QUIT_"):
                return input_user_list
            elif(user == "AGAIN_"):
                print("이전 입력값은 모두 삭제 됩니다.")
                input_user_list.clear()
                input_user_list = []
                continue
            
            if(user in check_list):
                input_user_list.extend([user])
            else:
                print("USER목록에 없습니다.")

def InputTableList(source_table_list):

    table_list=[]
    check_list=""
    for table in source_table_list:
        check_list=check_list + " " + table[0]

    while True:
        print("테이블입력")
        print("종료를 원하시면 입력값에 QUIT_ 입력")
        print("변경 초기화를 원하시면 입력값에 AGAIN_ 입력")
        while True:
            table=str(get_input_val("입력값:"))
            
            if(table == "QUIT_"):
                return table_list
            elif(table == "AGAIN_"):
                print("이전 입력값은 모두 삭제 됩니다.")
                table_list.clear()
                table_list = []
                continue
            
            if(table in check_list):
                table_list.extend([table])
            else:
                print("스키마목록에 없는 스키마입니다.")
            

def MakeTunnel(bastion_ip,bastion_user,bastion_pwd,endpoint):
    tunnel=SSHTunnelForwarder(
        (bastion_ip, 22),
        ssh_username=bastion_user,
        ssh_password=bastion_pwd,
        remote_bind_address=(endpoint, 3306)
    )
    return tunnel

def get_change_schemalist(change_word_list,source_schema_list):
    change_schemalist=[]
    for schema in source_schema_list:
        old_schema=schema[0]
        new_schema=old_schema
        for change_word in change_word_list:
            new_schema=new_schema.replace(change_word[0].lower(), change_word[1].lower())
            new_schema=new_schema.replace(change_word[0].upper(), change_word[1].upper())
        if(old_schema != new_schema):
            change_schemalist.extend([[old_schema,new_schema]])
    return change_schemalist

def schema_dump(end_point,dump_option,mig_schema_list,local_bind_port,db_user,db_pwd):   
    now=datetime.datetime.now()
    file_name = now.strftime('%Y%m%d%H%M%S') + '_schema.sql'
    command = 'mysqldump -h '+end_point+' -P ' + str(local_bind_port) + ' -u ' + str(db_user) + ' -p' + str(db_pwd)
    command = command + ' --databases ' + mig_schema_list + ' ' + dump_option + ' --default-character-set=utf8 --single-transaction --result-file='+file_name
    print(command)
    os.system(command)
    return file_name

def table_dump(end_point,dump_option,mig_schema,mig_table_list,local_bind_port,db_user,db_pwd):    
    now=datetime.datetime.now()
    file_name = now.strftime('%Y%m%d%H%M%S') + '_table.sql'
    command = 'mysqldump -h '+end_point+' -P ' + str(local_bind_port) + ' -u ' + str(db_user) + ' -p' + str(db_pwd)
    command = command + ' '+ mig_schema + ' ' + mig_table_list + ' ' + dump_option +  ' --default-character-set=utf8 --single-transaction --result-file='+file_name
    print(command)
    os.system(command)
    return file_name

def import_dump(end_point,dump_file,local_bind_port,db_user,db_pwd,input_schema):
    command='mysql  --max_allowed_packet=500M -h '+end_point+' -P ' + str(local_bind_port) + ' -u ' + str(db_user) + ' -p' + str(db_pwd) + ' ' + input_schema + '  <' + dump_file
    print(command)
    os.system(command)

def replaceInFile(file_name, change_word_list,change_scripts):
    f = codecs.open(file_name, 'r', encoding='utf8')
    read_file = f.read()
    f.close()
    new_file_name = 'new_'+file_name
    new_file = codecs.open(new_file_name,'w', encoding='utf8')
    for line in read_file.split("\n"):
        new_line=line
        if("INSERT INTO " in line and change_scripts==1):
            for(old, newstr) in change_word_list:
                if old in line:
                    old="INSERT INTO `" + old + "` VALUES ("
                    newstr="INSERT INTO `" + newstr + "` VALUES ("
                    new_line=new_line.replace(old.lower(), newstr.lower())
                    new_line=new_line.replace(old.upper(), newstr.upper())
        
        elif("USE `" in line or
             "DROP " in line or
             "LOCK " in line or
             "CREATE" in line or
             "/*!40000 ALTER" in line or
             "INSERT INTO " in line
             ):
        
            for(old, newstr) in change_word_list:
                if old in line:
                    old="`" + old + "`"
                    newstr="`" + newstr + "`"
                    new_line=new_line.replace(old.lower(), newstr.lower())
                    new_line=new_line.replace(old.upper(), newstr.upper())
        elif("KEY `" in line):
            for(old, newstr) in change_word_list:
                if old in line:
                    old="`ix_" + old + "0"
                    newstr="`ix_" + newstr + "0"
                    new_line=new_line.replace(old.lower(), newstr.lower())
                    new_line=new_line.replace(old.upper(), newstr.upper())
            for(old, newstr) in change_word_list:
                if old in line:
                    old="`ix_" + old + "1"
                    newstr="`ix_" + newstr + "1"
                    new_line=new_line.replace(old.lower(), newstr.lower())
                    new_line=new_line.replace(old.upper(), newstr.upper())
        elif(") ENGINE" in line or "-- Host:" in line):
            for(old, newstr) in change_word_list:
                if old in line:
                    new_line=new_line.replace(old.lower(), newstr.lower())
                    new_line=new_line.replace(old.upper(), newstr.upper())    
        
        elif("--" in line ):
            for(old, newstr) in change_word_list:
                if old in line:
                    old="`" + old + "`"
                    newstr="`" + newstr + "`"
                    new_line=new_line.replace("'","`").replace(old.lower(), newstr.lower())
                    new_line=new_line.replace("'","`").replace(old.upper(), newstr.upper())
        
        new_file.write(new_line)
        new_file.write("\n")#close file new_file.close()
        '''
        if(line != new_line):
            print('###################################')
            print(line)
            print(new_line)
            print('###################################')
        '''
    new_file.close()
    return new_file_name

if __name__=='__main__':
    try:

        TUNNEL_FLAG=0
        CONNECT_FLAG=0
        schema_list_query = "SELECT sc.SCHEMA_NAME,\n"
        schema_list_query = schema_list_query+"floor(sum(tb.data_length + tb.index_length)/1024/1024) as MB\n"
        schema_list_query = schema_list_query+"FROM information_schema.SCHEMATA sc\n"
        schema_list_query = schema_list_query+"left join information_schema.TABLES tb on sc.SCHEMA_NAME = tb.TABLE_SCHEMA\n"
        schema_list_query = schema_list_query+"where sc.schema_name not in ('mysql','performance_schema','sys','awsdms_control','information_schema')\n"
        schema_list_query = schema_list_query+"group by sc.schema_name\n"
        schema_list_query = schema_list_query+"ORDER BY MB DESC\n"

        table_list_query = "SELECT table_name,floor((data_length + index_length)/1024/1024) from information_Schema.tables where table_schema='%s'"

        user_list_query="select user from mysql.user where user not in ('rdsadmin','mysql.sys','mysql','sys')"
        create_user_query="show create user %s"
        grant_user_query="show grants for %s"

        while True:
            #메인메뉴 입력
            menu_number = MainMenu()
            input_schema=""
            #메인메뉴 EXIT
            if(menu_number == 4):
                if(TUNNEL_FLAG==1):
                    source_tunnel.stop()
                    target_tunnel.stop()
                break

            file_name = "conn_info.json"
            server_infos=read_conn_info(file_name)
            #터널링 및 DB커넥션
            if(TUNNEL_FLAG==0 and CONNECT_FLAG==0):
                use_tunnel_flag = IsUseTunnel()
                if(use_tunnel_flag == 1):
                    
                    server_info=get_server_info(server_infos)

                    source_tunnel = MakeTunnel(server_info["source_bastion_ip"],server_info["source_bastion_user"],server_info["source_bastion_pwd"],server_info["source_endpoint"])
                    target_tunnel = MakeTunnel(server_info["target_bastion_ip"],server_info["target_bastion_user"],server_info["target_bastion_pwd"],server_info["target_endpoint"])
                    source_tunnel.start()
                    TUNNEL_FLAG=1
                    target_tunnel.start()
                    server_info["source_connect_ip"]='127.0.0.1'
                    server_info["target_connect_ip"]='127.0.0.1'
                    server_info["source_connect_port"]=source_tunnel.local_bind_port
                    server_info["target_connect_port"]=target_tunnel.local_bind_port
                    print("ASIS 터널링포트: "+str(source_tunnel.local_bind_port)+" ,TOBE 터널링포트: " + str(target_tunnel.local_bind_port))
                    #터널링 커넥션
                    source_conn = pymysql.connect(host='127.0.0.1', port=server_info["source_connect_port"], user=server_info["source_db_user"], password=server_info['source_db_pwd'], charset='UTF8')
                    target_conn = pymysql.connect(host='127.0.0.1', port=server_info["target_connect_port"], user=server_info["target_db_user"], password=server_info['target_db_pwd'], charset='UTF8')
                    #Source 스키마 리스트 저장
                    source_cursor = source_conn.cursor()
                    target_cursor = target_conn.cursor()
                    CONNECT_FLAG=1
                    source_cursor.execute(schema_list_query)
                    source_schema_list=source_cursor.fetchall()
                elif(use_tunnel_flag == 2):
                    server_info=get_connect_info(server_infos)
                    server_info["source_connect_ip"]=server_info["source_endpoint"]
                    server_info["target_connect_ip"]=server_info["target_endpoint"]
                    server_info["source_connect_port"]=3306
                    server_info["target_connect_port"]=3306
                    source_conn = pymysql.connect(host=server_info["source_endpoint"], port=3306, user=server_info["source_db_user"], password=server_info['source_db_pwd'], charset='UTF8')
                    target_conn = pymysql.connect(host=server_info["target_endpoint"], port=3306, user=server_info["target_db_user"], password=server_info['target_db_pwd'], charset='UTF8')
                    #Source 스키마 리스트 저장
                    source_cursor = source_conn.cursor()
                    target_cursor = target_conn.cursor()
                    CONNECT_FLAG=1
                    source_cursor.execute(schema_list_query)
                    source_schema_list=source_cursor.fetchall()

            if(menu_number in [1,2]):
                #DDL, DATA, 둘다 선택    
                dump_option=IsDataMig(menu_number)                  
                #스크립트 변경여부 입력
                change_scripts = IsChangeWord()
            
                if(change_scripts == 4):#초기화면
                    continue
                elif(change_scripts == 1 or change_scripts == 2):#스크립트변경
                    change_word_list=getChangeWord()
                    if(change_scripts == 1):#스키마 변경
                        change_word_list=get_change_schemalist(change_word_list,source_schema_list)
                    print(change_word_list)

            ################################덤프파일########################################
            if(menu_number==1):###############스키마COPY#####################################################
                for source_schema in source_schema_list:#대상스키마 리스트 출력
                    print("스키마:" + source_schema[0] + ", 용량: " + str(source_schema[1]) + "MB")
                is_all_schema=IsAllSchema()
                #전체스키마
                mig_schema_list=""
                
                if(is_all_schema == 1):#전체스키마
                    #input_schema=source_schema_list[0][0]
                    for schema in source_schema_list:
                        mig_schema_list = mig_schema_list + schema[0] + " "
                    pass
                elif(is_all_schema == 2):#스키마선택
                    input_schema_list = InputSchemaList(source_schema_list)
                    #input_schema=input_schema_list[0]
                    for schema in input_schema_list:
                        mig_schema_list = mig_schema_list + schema + " "
                for source_schema in source_schema_list:#대상스키마 리스트 출력
                    if(source_schema[0] in mig_schema_list):
                        print("이관 대상 스키마:" + source_schema[0] + ", 용량: " + str(source_schema[1]) + "MB")
                Starttime = int((time.time()))#덤프시작시간
                dump_file_name=schema_dump(server_info["source_connect_ip"],dump_option,mig_schema_list,server_info["source_connect_port"],server_info["source_db_user"],server_info["source_db_pwd"])
                Endtime = int(time.time())#덤프종료시간
                print("time:" + str(Endtime - Starttime) + "초, 파일명: " + dump_file_name)
            elif(menu_number==2):##############테이블 COPY#####################################################
                for source_schema in source_schema_list:#대상스키마 리스트 출력
                    print("스키마:" + source_schema[0] + ", 용량: " + str(source_schema[1]) + "MB")
                print("스키마를 선택하세요.")
                while True:
                    break_flag=0
                    input_schema=get_input_val("스키마")
                    for source_schema in source_schema_list:
                        if(source_schema[0] == input_schema):
                            break_flag=1
                            break
                    if(break_flag==1):
                        break
                    print("스키마항목에 없습니다.")
                #선택한 스키마 테이블리스트 출력
                source_cursor.execute(table_list_query%(input_schema))
                source_table_list=source_cursor.fetchall()
                for source_table in source_table_list:
                    print("테이블:"+source_table[0]+", 용량:" + str(source_table[1]) + "MB")
                #테이블전체인지 선택인지    
                is_all_table=IsAllTable()
                mig_table_list=""
                if(is_all_table==1):#전체테이블
                    for table in source_table_list:
                        #print(table[0])
                        mig_table_list=mig_table_list + " " + table[0]
                elif(is_all_table==2):#특정테이블
                    input_table_list = InputTableList(source_table_list)
                    for table in input_table_list:
                        mig_table_list=mig_table_list + " " + table
                #print(mig_table_list)
                Starttime = int((time.time()))#덤프시작시간
                dump_file_name=table_dump(server_info["source_connect_ip"],dump_option,input_schema,mig_table_list,server_info["source_connect_port"],server_info["source_db_user"],server_info["source_db_pwd"])
                Endtime = int(time.time())#덤프종료시간
                print("time:" + str(Endtime - Starttime) + "초, 파일명: " + dump_file_name)


            if(menu_number in [1,2]):
                #################### 파일변경 ######################################################
                if not os.path.exists(dump_file_name):
                    print("파일없음")
                    continue
                
                if(change_scripts in [1,2]): 
                    dump_file_name=replaceInFile(dump_file_name, change_word_list,change_scripts)
                    for(old, newstr) in change_word_list:
                        print(input_schema)
                        input_schema=input_schema.replace(old.lower(), newstr.lower())
                        input_schema=input_schema.replace(old.upper(), newstr.upper())
                        print(input_schema)
                    del change_word_list
          
                ##########덤프넣기###############################3
                Starttime = int((time.time()))#덤프시작시간
                import_dump(server_info["target_connect_ip"],dump_file_name,server_info["target_connect_port"],server_info["target_db_user"],server_info["target_db_pwd"],input_schema)
                Endtime = int(time.time())#덤프종료시간
                print("time:" + str(Endtime - Starttime) + "초")
            
            ####### 사용자copy #############################
            if(menu_number==3):
                source_cursor.execute(user_list_query)
                source_user_list=source_cursor.fetchall()
                for source_user in source_user_list:
                    print(source_user[0])
                user_menu=IsAllUser()
                grant_change_flag=IsGrantChangeWord()
                grant_old_word=""
                grant_new_word=""

                if(grant_change_flag==1):
                    print("###################################################################")
                    grant_old_word=get_input_val("변경전단어:")
                    grant_new_word=get_input_val("변경후단어:")
                    print("###################################################################")

                if(user_menu==1):
                    for source_user in source_user_list:
                        #유저생성쿼리
                        print(create_user_query%(source_user[0]))
                        source_cursor.execute(create_user_query%(source_user[0]))
                        create_user_query_list=source_cursor.fetchall()
                        print(create_user_query_list[0][0].replace(grant_old_word,grant_new_word))
                        target_cursor.execute(create_user_query_list[0][0].replace(grant_old_word,grant_new_word))
                        #유저권한쿼리
                        print(grant_user_query%(source_user[0]))
                        source_cursor.execute(grant_user_query%(source_user[0]))
                        grant_user_query_list=source_cursor.fetchall()
                        for grant_query in grant_user_query_list:
                            print(grant_query[0].replace(grant_old_word,grant_new_word))
                            target_cursor.execute(grant_query[0].replace(grant_old_word,grant_new_word))
                elif(user_menu==2):
                    input_user_list=InputUserList(source_user_list)
                    for source_user in input_user_list:
                        try:
                            #유저생성쿼리
                            print(create_user_query%(source_user))
                            source_cursor.execute(create_user_query%(source_user))
                            create_user_query_list=source_cursor.fetchall()
                            print(create_user_query_list[0][0].replace(grant_old_word,grant_new_word))
                            target_cursor.execute(create_user_query_list[0][0].replace(grant_old_word,grant_new_word))
                            #유저권한쿼리
                            print(grant_user_query%(source_user))
                            source_cursor.execute(grant_user_query%(source_user))
                            grant_user_query_list=source_cursor.fetchall()
                            for grant_query in grant_user_query_list:
                                print(grant_query[0].replace(grant_old_word,grant_new_word))
                                target_cursor.execute(grant_query[0].replace(grant_old_word,grant_new_word))   
                        except Exception as ex:
                            print(ex)



    except Exception as ex:
        if(TUNNEL_FLAG==1):
            source_tunnel.stop()
            target_tunnel.stop()
        print(ex)
        sys.exit()




