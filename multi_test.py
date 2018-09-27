import json
from pprint import pprint
import sys,os
import pymysql
from sshtunnel import SSHTunnelForwarder 
import time

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
def MainMenu():
    print("###################################################################")
    print("  1. DB SCHEMA COPY")
    print("  2. TABLE COPY")
    print("  3. USER COPY")
    print("  4. EXIT")

    input_val = InputNumber(1,4)
    print("###################################################################")

    return input_val

def get_server_info():
    server_info={}
    server_info["asis_bastion_ip"]=get_input_val("AS-IS BASTION_IP")
    server_info["asis_bastion_user"]=get_input_val("AS-IS BASTION USER")
    server_info["asis_bastion_pwd"]=get_input_val("AS-IS BASTION PASSWORD")
    server_info["asis_endpoint"]=get_input_val("AS-IS ENDPOINT")
    server_info["asis_db_user"]=get_input_val("AS-IS DB USER")
    server_info["asis_db_pwd"]=get_input_val("AS-IS DB PASSWORD")
    server_info["tobe_bastion_ip"]=get_input_val("TO-BE BASTION_IP")
    server_info["tobe_bastion_user"]=get_input_val("TO-BE BASTION USER")
    server_info["tobe_bastion_pwd"]=get_input_val("TO-BE BASTION PASSWORD")
    server_info["tobe_endpoint"]=get_input_val("TO-BE ENDPOINT")
    server_info["tobe_db_user"]=get_input_val("TO-BE DB USER")
    server_info["tobe_db_pwd"]=get_input_val("TO-BE DB PASSWORD")
    return server_info

def IsChangeWord():
    print("###################################################################")
    print("  1. 스키마 스크립트 변경")
    print("  2. 스크립트 전체 변경")
    print("  3. 변경없음")
    print("  4. 초기메뉴")
    input_val = InputNumber(1,4)
    print("###################################################################")

    return input_val
def IsAllSchema():
    print("###################################################################")
    print("  1. 스키마 전체")
    print("  2. 스키마 선택")
    input_val = InputNumber(1,2)
    print("###################################################################")
    return input_val
def IsAllTable():
    print("###################################################################")
    print("  1. 테이블 전체")
    print("  2. 테이블 선택")
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

def InputSchemaList(asis_schema_list):

    schema_list=[]
    check_list=""
    for schema in asis_schema_list:
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
            
            if(~(schema in check_list)):
                print("스키마목록에 없는 스키마입니다.")
            schema_list.extend([schema])

def MakeTunnel(bastion_ip,bastion_user,bastion_pwd,endpoint):
    tunnel=SSHTunnelForwarder(
        (bastion_ip, 22),
        ssh_username=bastion_user,
        ssh_password=bastion_pwd,
        remote_bind_address=(endpoint, 3306)
    )
    return tunnel

def get_change_schemalist(change_word_list,asis_schema_list):
    change_schemalist=[]
    for schema in asis_schema_list:
        old_schema=schema[0]
        new_schema=old_schema
        for change_word in change_word_list:
            new_schema=new_schema.replace(change_word[0], change_word[1])
        if(old_schema != new_schema):
            change_schemalist.extend([[old_schema,new_schema]])
    return change_schemalist

def schema_dump(target_schema_list,local_bind_port,db_user,db_pwd):    
    command = 'mysqldump -h 127.0.0.1 -P ' + str(local_bind_port) + ' -u ' + str(db_user) + ' -p' + str(db_pwd)
    command = command + ' --databases ' + target_schema_list + ' --routines --default-character-set=utf8 --result-file=schema.sql'
    print(command)
    os.system(command)

def table_dump(target_schema,target_table_list,local_bind_port,db_user,db_pwd):    
    command = 'mysqldump -h 127.0.0.1 -P ' + str(local_bind_port) + ' -u ' + str(db_user) + ' -p' + str(db_pwd)
    command = command + ' '+ target_schema + ' ' + target_schema_list + ' --routines --default-character-set=utf8 --result-file=table.sql'
    print(command)
    #os.system(command)


if __name__=='__main__':
    try:

        TUNNEL_FLAG=0
        schema_list_query = "SELECT sc.SCHEMA_NAME,\n"
        schema_list_query = schema_list_query+"floor(sum(tb.data_length + tb.index_length)/1024/1024) as MB\n"
        schema_list_query = schema_list_query+"FROM information_schema.SCHEMATA sc\n"
        schema_list_query = schema_list_query+"left join information_schema.TABLES tb on sc.SCHEMA_NAME = tb.TABLE_SCHEMA\n"
        schema_list_query = schema_list_query+"where sc.schema_name not in ('mysql','performance_schema','sys','awsdms_control','information_schema')\n"
        schema_list_query = schema_list_query+"group by sc.schema_name\n"
        schema_list_query = schema_list_query+"ORDER BY MB DESC\n"

        table_list_query = "SELECT table_name from information_Schema.tables where table_schema='"

        while True:
            #메인메뉴 입력
            menu_number = MainMenu()

            #메인메뉴 EXIT
            if(menu_number == 4):
                if(TUNNEL_FLAG==1):
                    asis_tunnel.stop()
                    tobe_tunnel.stop()
                break
            
            #터널링 및 DB커넥션
            if(TUNNEL_FLAG==0):
                server_info=get_server_info()

                asis_tunnel = MakeTunnel(server_info["asis_bastion_ip"],server_info["asis_bastion_user"],server_info["asis_bastion_pwd"],server_info["asis_endpoint"])
                tobe_tunnel = MakeTunnel(server_info["tobe_bastion_ip"],server_info["tobe_bastion_user"],server_info["tobe_bastion_pwd"],server_info["tobe_endpoint"])
                asis_tunnel.start()
                TUNNEL_FLAG=1
                tobe_tunnel.start()
                print("ASIS 터널링포트: "+str(asis_tunnel.local_bind_port)+" ,TOBE 터널링포트: " + str(tobe_tunnel.local_bind_port))
                #터널링 커넥션
                asis_conn = pymysql.connect(host='127.0.0.1', port=asis_tunnel.local_bind_port, user=server_info["asis_db_user"], password=server_info['asis_db_pwd'], charset='UTF8')
                tobe_conn = pymysql.connect(host='127.0.0.1', port=tobe_tunnel.local_bind_port, user=server_info["tobe_db_user"], password=server_info['tobe_db_pwd'], charset='UTF8')
                #asis 스키마 리스트 저장
                asis_cursor = asis_conn.cursor()
                tobe_cursor = tobe_conn.cursor()
                asis_cursor.execute(schema_list_query)
                asis_schema_list=asis_cursor.fetchall()
                
                 
                

            #스크립트 변경여부 입력
            change_scripts = IsChangeWord()
            
            
            if(change_scripts == 4):#초기화면
                continue
            elif(change_scripts == 1 or change_scripts == 2):#스크립트변경
                change_word_list=getChangeWord()
                if(change_scripts == 1):#스키마 변경
                    change_word_list=get_change_schemalist(change_word_list,asis_schema_list)
                print(change_word_list)


            if(menu_number==1):#스키마COPY
                for asis_schema in asis_schema_list:#대상스키마 리스트 출력
                    if(asis_schema[0] in target_schema_list):
                        print("스키마:" + asis_schema[0] + ", 용량: " + str(asis_schema[1]) + "MB")
                is_all_schema=IsAllSchema()
                #전체스키마
                target_schema_list=""
                
                if(is_all_schema == 1):#전체스키마
                    for schema in asis_schema_list:
                        target_schema_list = target_schema_list + schema[0] + " "
                    pass
                elif(is_all_schema == 2):#스키마선택
                    input_schema_list = InputSchemaList(asis_schema_list)
                    for schema in input_schema_list:
                        target_schema_list = target_schema_list + schema + " "
                for asis_schema in asis_schema_list:#대상스키마 리스트 출력
                    if(asis_schema[0] in target_schema_list):
                        print("이관 대상 스키마:" + asis_schema[0] + ", 용량: " + str(asis_schema[1]) + "MB")
                Starttime = int((time.time()))#덤프시작시간
                schema_dump(target_schema_list,asis_tunnel.local_bind_port,server_info["asis_db_user"],server_info["asis_db_pwd"])
                Endtime = int(time.time())#덤프종료시간
                print("time:",Endtime - Starttime)
            elif(menu_number==2):#테이블 COPY
                for asis_schema in asis_schema_list:#대상스키마 리스트 출력
                    print("스키마:" + asis_schema[0] + ", 용량: " + str(asis_schema[1]) + "MB")
                print("스키마를 선택하세요.")
                while True:
                    break_flag=0
                    input_schema=get_input_val("스키마")
                    for asis_schema in asis_schema_list:
                        if(asis_schema[0] == input_schema):
                            break_flag=1
                            break
                    if(break_flag==1):
                        break
                    print("스키마항목에 없습니다.")
                #선택한 스키마 테이블리스트 출력
                asis_cursor.execute(table_list_query+input_schema+"'")
                asis_table_list=asis_cursor.fetchall()
                print(asis_table_list)
                #테이블전체인지 선택인지    
                is_all_table=IsAllTable()
                target_table_list=""
                if(is_all_table==1):#전체테이블
                    for table in asis_table_list:
                        target_table_list=target_table_list + " " + table
                elif(is_all_table==2):#특정테이블
                    while True:
                        break_flag=0
                        input_table=get_input_val("테이블")
                        for asis_table in asis_table_list:
                            if(asis_table == input_table):
                                break_flag=1
                                break
                        if(break_flag==1):
                            break
                        print("스키마항목에 없습니다.")
                Starttime = int((time.time()))#덤프시작시간
                table_dump(input_schema,target_table_list,asis_tunnel.local_bind_port,server_info["asis_db_user"],server_info["asis_db_pwd"])
                Endtime = int(time.time())#덤프종료시간
                print("time:",Endtime - Starttime)
                pass         
            
            pass

            


    except Exception as ex:
        if(TUNNEL_FLAG==1):
            asis_tunnel.stop()
            tobe_tunnel.stop()
        print(ex)
        sys.exit()        