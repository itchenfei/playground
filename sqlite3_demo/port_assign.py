import sqlite3
import getpass
import os
import random
import sys
import subprocess

# PATH
iperf_port_db_name = "iperf3_port.db"
iperf_port_db_path = os.path.join("C:\\", "Users", getpass.getuser(), iperf_port_db_name)

# CONN DATABASE
conn = sqlite3.connect(iperf_port_db_path)
c = conn.cursor()

# CREATE IPERF TABLE
cursor = c.execute("select count(*) from sqlite_master where type='table' and name='IPERF';")
if cursor.fetchone()[0] == 0:
    c.execute('''CREATE TABLE IPERF (PORT INT PRIMARY KEY NOT NULL);''')
    conn.commit()

if len(sys.argv) == 1:
    # GET PORT NUM
    port = random.randint(29000, 29999)  # USE HIGH LEVEL PORT

    # GET PORT LIST
    cursor = c.execute("SELECT PORT FROM IPERF")
    port_list = list(port[0] for port in cursor.fetchall())

    # GET NETSTAT
    net_stat = subprocess.getoutput('netstat -an | findstr {}'.format(port))

    # TEST
    if port not in port_list and not net_stat:
        # INSERT
        c.execute("INSERT INTO IPERF (PORT) VALUES ({});".format(port))
        conn.commit()

    # CLOSE DATABASE
    c.close()

    # OUTPUT
    print(port)

else:
    c.execute("DELETE FROM IPERF WHERE PORT={}".format(sys.argv[1]))
    conn.commit()
    c.close()
