#!/usr/bin/env python3
import random
import sys
import requests

from checklib import *



class Checker(BaseChecker):
    vulns: int = 2
    timeout: int = 5
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        print(args)
        self.url = f"http://{args[0]}:8001"
        super(Checker, self).__init__(*args, **kwargs)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

    def check(self):
        session = get_initialized_session()

        #check company creation
        companyid = rnd_string(20)
        create_company_request = session.post(self.url + "/api/v1/token/create?companyid=" + companyid)
        data = session.get(self.url + "/api/v1/token/list")
        self.assert_in(companyid, data.text, "Company cannot be created")
        #TODO check log read

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        company_id = rnd_username()
        create_company_request = requests.post(self.url + "/api/v1/token/create?companyid=" + company_id)

        card_number = random.randint(100000, 999999)
        token = create_company_request.json()['token']
        secret = create_company_request.json()['secret']
       
        
        store_payment_data_request = requests.post(self.url + f"/api/v1/payment_data/store",params={"token": token, "secret": secret, "card_secret": flag, "card_number": str(card_number)})
        print(store_payment_data_request.text)
        self.cquit(Status.OK, f"{token}:{secret}", f"{token}:{secret}")

    def get(self, flag_id: str, flag: str, vuln: str):
        s = get_initialized_session()
        token, secret = flag_id.split(':')
    
        get_payment_data_request = s.get(self.url + "/api/v1/payment_data/get", params={"token": token, "secret":secret})
        value = get_payment_data_request.text

        self.assert_in(flag,value, "Cannot find flag", Status.CORRUPT)

        self.cquit(Status.OK)


if __name__ == '__main__':
    print(sys.argv)
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)