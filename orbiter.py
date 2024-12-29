import random
from datetime import datetime, timezone

import requests
from loguru import logger

from datatypes.account import AccItem
from tools.add_logger import add_logger
from tools.executor import pool_executor
from tools.orbiter_requests import get_leaderboard_info_response
from tools.other_utils import sleep_in_range, read_file
from user_data.config import shuffle_accounts, max_workers_range

if __name__ == '__main__':
    add_logger(version='v1.0')

    try:
        while True:
            try:
                today = datetime.now(timezone.utc).strftime("%B%d")
                private_keys = read_file('user_data/private.txt')
                accs = [AccItem(index=index, private_key=pk) for index, pk in enumerate(private_keys, start=1)]

                if accs:
                    if shuffle_accounts:
                        random.shuffle(accs)

                    logger.info(
                        f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}]: '
                        f'{len(accs)} accs to be used.\n'
                    )

                    with requests.Session() as session:
                        leaderboard_info = get_leaderboard_info_response(session=session)

                    logger.info(f'total leaderboard address count: {leaderboard_info.result.addressCount}.')

                    pool_executor(
                        accs=accs,
                        workers_range=max_workers_range,
                        total_address_count=leaderboard_info.result.addressCount
                    )
                else:
                    logger.success(f'{today}: no any pk.')
                    break

                sleep_in_range(30 * 60, 60 * 60, True)
            except Exception as e:
                logger.exception(e)
    except KeyboardInterrupt:
        logger.success('exited by user.')
        exit()
