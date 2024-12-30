import concurrent.futures
import random
from datetime import datetime, timedelta

import requests
import web3
from loguru import logger
from web3 import Web3

from datatypes.account import AccItem
from tools.crypto import checkin_tx
from tools.orbiter_requests import (
    get_user_rank_and_points_response,
    get_checkin_record_response,
    post_checkin_response
)
from tools.other_utils import sleep_in_range
from user_data.config import mobile_proxy, chains, sleep_between_accounts


def single_executor(acc: AccItem, total_address_count: int):
    try:
        account = web3.Account.from_key(acc.private_key)
        address = Web3.to_checksum_address(account.address)

        with requests.Session() as session:
            if mobile_proxy:
                session.proxies = {
                    'http': mobile_proxy,
                    'https': mobile_proxy
                }

                rank_and_points = get_user_rank_and_points_response(
                    index=acc.index, address=address, session=session
                )
                address_rank_in_perc = round(rank_and_points.result.rank / total_address_count * 100, 2)
                checkin_info = get_checkin_record_response(index=acc.index, address=address, session=session)

                logger.info(
                    f'#{acc.index} | {address} | '
                    f'points: {rank_and_points.result.point}, #{rank_and_points.result.rank} | '
                    f'{address_rank_in_perc}% | '
                    f'total_count: {checkin_info.result.totalCount}, '
                    f'checkin_count: {checkin_info.result.checkInCount}.'
                )

                current_date = datetime.now()
                tomorrow_date = current_date + timedelta(days=1)
                current_date_formatted = current_date.strftime('%Y-%m-%d')
                tomorrow_date_formatted = tomorrow_date.strftime('%Y-%m-%d')
                checkin_chain = random.choice(chains)
                checkin_hash = checkin_tx(
                    private_key=acc.private_key,
                    chain=checkin_chain,
                    current_date=datetime.now().strftime('%Y%m%d')
                )
                if checkin_hash and 'already checkin' in checkin_hash:
                    logger.info(
                        f"#{acc.index} | {address} | [{checkin_chain.name}] | come back on {tomorrow_date_formatted}.")
                elif checkin_hash:
                    checkin_response = post_checkin_response(
                        index=acc.index,
                        address=address,
                        chain_id=checkin_chain.id,
                        tx_hash=checkin_hash,
                        session=session
                    )
                    if checkin_response.message:
                        logger.error(
                            f"#{acc.index} | {address} | [{checkin_chain.name}] | "
                            f"checkin on {current_date_formatted}: {checkin_chain.explorer}/{checkin_hash} | "
                            f"error: {checkin_response.message}"
                        )
                    elif checkin_response.result == "ok":
                        logger.success(
                            f"#{acc.index} | {address} | [{checkin_chain.name}] | "
                            f"checkin on {current_date_formatted}: {checkin_chain.explorer}/{checkin_hash}"
                        )
                    else:
                        logger.warning(
                            f"#{acc.index} | {address} | [{checkin_chain.name}] | "
                            f"checkin on {current_date_formatted}: {checkin_chain.explorer}/{checkin_hash} | "
                            f"unexpected response: {checkin_response.dict()}"
                        )

                    sleep_in_range(sec_from=sleep_between_accounts[0], sec_to=sleep_between_accounts[1])
                    checkin_info = get_checkin_record_response(index=acc.index, address=address, session=session)
                    logger.info(
                        f'#{acc.index} | {address} | '
                        f'points: {rank_and_points.result.point}, #{rank_and_points.result.rank} | '
                        f'{address_rank_in_perc}% | '
                        f'total_count: {checkin_info.result.totalCount}, '
                        f'checkin_count: {checkin_info.result.checkInCount}.'
                    )
                else:
                    logger.error(f'#{acc.index} | {address}: checkin_tx has failed.')
    except Exception as e:
        logger.exception(e)


def pool_executor(accs: [AccItem], workers_range: [], total_address_count: int):
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=random.randint(workers_range[0], workers_range[1])
    ) as executor:

        futures = [
            executor.submit(
                single_executor, acc, total_address_count
            ) for acc in accs
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")
