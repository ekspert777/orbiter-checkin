import json

import requests
from loguru import logger

from datatypes.responses.checkin_post import CheckinPostResponse
from datatypes.responses.checkin_record import CheckinRecordResponse
from datatypes.responses.leaderboard_info import LeaderboardInfoResponse
from datatypes.responses.rank_and_point import RankAndPointResponse
from tools.change_ip import execute_change_ip
from user_data.config import change_ip_url


def get_user_rank_and_points_response(
        index: int,
        address: str,
        session: requests.Session()
) -> RankAndPointResponse:
    change_ip = execute_change_ip(change_ip_url=change_ip_url)
    if change_ip:
        logger.info(f"#{index} | {address} | ip has been changed.")

    url = f"https://api.orbiter.finance/points_platform/rank/address/{address.lower()}"
    response = session.get(url=url)
    if response.status_code == 200:
        return RankAndPointResponse.parse_obj(json.loads(response.content))


def get_leaderboard_info_response(session: requests.Session()) -> LeaderboardInfoResponse:
    change_ip = execute_change_ip(change_ip_url=change_ip_url)
    if change_ip:
        logger.info(f"ip has been changed.")

    url = f"https://api.orbiter.finance/points_platform/rank/info"
    response = session.get(url=url)
    if response.status_code == 200:
        return LeaderboardInfoResponse.parse_obj(json.loads(response.content))


def get_checkin_record_response(
        index: int,
        address: str,
        session: requests.Session()
) -> CheckinRecordResponse:
    change_ip = execute_change_ip(change_ip_url=change_ip_url)
    if change_ip:
        logger.info(f"#{index} | {address} | ip has been changed.")

    url = f"https://api.orbiter.finance/active-platform/checkin/getCheckInRecord?address={address.lower()}&page=1"
    response = session.get(url=url)
    if response.status_code == 200:
        return CheckinRecordResponse.parse_obj(json.loads(response.content))


def post_checkin_response(
        index: int,
        address: str,
        chain_id: int,
        tx_hash: str,
        session: requests.Session()
) -> CheckinPostResponse:
    change_ip = execute_change_ip(change_ip_url=change_ip_url)
    if change_ip:
        logger.info(f"#{index} | {address} | ip has been changed.")

    url = f"https://api.orbiter.finance/active-platform/checkin"
    payload = {
        "address": address.lower(),
        "chainId": str(chain_id),
        "hash": tx_hash.lower()
    }
    response = session.post(url=url, json=payload)
    if 200 <= response.status_code < 300:
        return CheckinPostResponse.parse_obj(json.loads(response.content))
