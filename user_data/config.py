from data.constants import *
from datatypes.chain import ChainItem

shuffle_accounts = True
max_workers_range = (1, 1)
sleep_between_accounts = (10, 20)
mobile_proxy = "http://log:pass@ip:port"
change_ip_url = ""  # leave empty, if you have travchis

gas_multiplier = 2
chains = [
    ChainItem(
        name='base',
        id=8453,
        rpc='https://rpc.ankr.com/base',
        explorer='https://basescan.org/tx',
        checkin_contract=BASE_ORBITER_CHECKIN_CONTRACT
    ),
    ChainItem(
        name='linea',
        id=59144,
        rpc='https://rpc.ankr.com/linea',
        explorer='https://lineascan.build/tx',
        checkin_contract=LINEA_ORBITER_CHECKIN_CONTRACT
    ),
]
