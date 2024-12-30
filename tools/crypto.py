from loguru import logger
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.middleware import geth_poa_middleware

from datatypes.balance import Balance
from datatypes.chain import ChainItem
from user_data.config import gas_multiplier


def pad_to_32_bytes(value):
    return value.rjust(64, '0')


def sign_and_wait(w3: Web3, transaction: {}, private_key: str, timeout: int = 300):
    account = w3.eth.account.from_key(private_key)
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    try:
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout)

        if receipt.status == 1:
            return txn_hash.hex()
        else:
            return None
    except TimeExhausted:
        logger.error(f"{account.address}: {txn_hash.hex()} not confirmed in {timeout} seconds.")
        return None
    except ValueError as e:
        logger.error(f"{account.address}: {e.args[0]}.")


def get_gas(w3: Web3()):
    latest_block = w3.eth.block_number
    fee_history = w3.eth.fee_history(1, latest_block, reward_percentiles=[50])
    base_fee_per_gas1 = fee_history['baseFeePerGas'][0]
    max_priority_fee_per_gas = int(fee_history['reward'][0][0])

    max_fee_per_gas = int(base_fee_per_gas1 + max_priority_fee_per_gas * 1.1)

    base_fee_per_gas2 = w3.eth.get_block('latest')['baseFeePerGas']
    if int(base_fee_per_gas2) > max_fee_per_gas:
        max_fee_per_gas = int(base_fee_per_gas2)

    return int(max_priority_fee_per_gas * 2), int(max_fee_per_gas * 3)


def get_account_nonce(private_key: str, chain: ChainItem):
    w3 = Web3(Web3.HTTPProvider(chain.rpc))
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)
    return nonce


def get_balance(address: str, rpc: str):
    web3 = Web3(Web3.HTTPProvider(rpc))
    balance = web3.eth.get_balance(web3.to_checksum_address(address))
    return Balance(
        int=balance,
        float=round(web3.from_wei(balance, 'ether'), 6)
    )


def checkin_tx(private_key: str, current_date: str, chain: ChainItem):
    try:
        w3 = Web3(Web3.HTTPProvider(chain.rpc))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        account = w3.eth.account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address)

        max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

        current_date_hex = hex(int(current_date))[2:]
        data = '0x30ea198a' + pad_to_32_bytes(current_date_hex)

        gas_limit = int(w3.eth.estimate_gas({
            "from": account.address,
            "to": chain.checkin_contract,
            "value": 0,
            "data": data
        }) * gas_multiplier)

        transaction = {
            "chainId": chain.id,
            "from": account.address,
            "to": chain.checkin_contract,
            "value": 0,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if 'ACKI' in str(e):
            return "already checkin"
        else:
            logger.exception(e)
