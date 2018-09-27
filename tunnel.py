import pymysql,boto3, sys, botocore 
import io,os
from sshtunnel import SSHTunnelForwarder 
from pprint import pprint
import codecs
from multiprocessing import Queue
from multiprocessing import Pool
import time


def MakeTunnel(bastion_ip,bastion_user,bastion_pwd,endpoint):
    tunnel=SSHTunnelForwarder(
        (bastion_ip, 22),
        ssh_username=bastion_user,
        ssh_password=bastion_pwd,
        remote_bind_address=(endpoint, 3306)
    )
    return tunnel
def func_asis_data_dump(schema):
    print(schema.split(','))
    command = 'mysqldump -h 127.0.0.1 -P ' + schema.split(',')[1] + ' -u ' + schema.split(',')[2] + ' -p' + schema.split(',')[3]
    command = command + ' --databases ' + schema.split(',')[0] + ' --no-create-info --result-file='+ schema.split(',')[0] +'_data.sql'
    print(command)
    os.system(command)

if __name__=='__main__':
    try:
        bastion_ip='13.124.158.221'
        bastion_user='dbaccess'
        bastion_pwd='qwer1234'
        endpoint='ltcmdev.cluster-c0xgcmsoxdvu.ap-northeast-2.rds.amazonaws.com'

        T1=MakeTunnel(bastion_ip,bastion_user,bastion_pwd,endpoint)
        T2=MakeTunnel(bastion_ip,bastion_user,bastion_pwd,endpoint)
        T3=MakeTunnel(bastion_ip,bastion_user,bastion_pwd,endpoint)


        T1.start()
        T2.start()
        #T3.start()

        '''
        arry_list=["ltcmstdev,"+str(T1.local_bind_port)+",b2_dba,qwer1234"]
        arry_list.extend(["ltcmdba,"+str(T2.local_bind_port)+",b2_dba,qwer1234"])
        arry_list.extend(["ltcmatdev,"+str(T3.local_bind_port)+",b2_dba,qwer12"])
        arry_list.extend(["poc_ord_tx,"+str(T1.local_bind_port)+",b2_dba,qwer1"])
        arry_list.extend(["ltcmetldev,"+str(T2.local_bind_port)+",b2_dba,qwer1"])
        arry_list.extend(["lpsdev,"+str(T3.local_bind_port)+",b2_dba,qwer1234"])
        arry_list.extend(["poc_etl,"+str(T1.local_bind_port)+",b2_dba,qwer1234"])
        arry_list.extend(["ltcmprdev,"+str(T2.local_bind_port)+",b2_dba,qwer12"])
        arry_list.extend(["sequence,"+str(T3.local_bind_port)+",b2_dba,qwer123"])
        '''
        arry_list=["ltcmstdev,"+str(T1.local_bind_port)+",b2_dba,qwer1234"]
        arry_list.extend(["ltcmdba,"+str(T2.local_bind_port)+",b2_dba,qwer1234"])
        arry_list.extend(["ltcmatdev,"+str(T1.local_bind_port)+",b2_dba,qwer12"])
        arry_list.extend(["poc_ord_tx,"+str(T2.local_bind_port)+",b2_dba,qwer1"])
        arry_list.extend(["ltcmetldev,"+str(T1.local_bind_port)+",b2_dba,qwer1"])
        arry_list.extend(["lpsdev,"+str(T2.local_bind_port)+",b2_dba,qwer1234"])
        arry_list.extend(["poc_etl,"+str(T1.local_bind_port)+",b2_dba,qwer1234"])
        arry_list.extend(["ltcmprdev,"+str(T2.local_bind_port)+",b2_dba,qwer12"])
        arry_list.extend(["sequence,"+str(T1.local_bind_port)+",b2_dba,qwer123"])
        print(arry_list[0])
        Starttime = int((time.time()))
        p = Pool(1)

        p.map(func_asis_data_dump,arry_list)
        Endtime = int(time.time())
        print("time:",Endtime - Starttime)

        print(T1.local_bind_port)
        print(T2.local_bind_port)
        #print(T3.local_bind_port)

        input(" 입력하세요: ")

        T1.stop()
        T2.stop()
        #T3.stop()

    except Exception as ex:
        T1.stop()
        T2.stop()
        #T3.stop()