"""一次性探针(可删): 对比 profile 用 X-Bogus(现状) vs a_bogus(拟修)。"""

import asyncio
from urllib.parse import urlencode

from crawlers.douyin.web.web_crawler import DouyinWebCrawler
from crawlers.douyin.web.endpoints import DouyinAPIEndpoints
from crawlers.douyin.web.models import UserProfile
from crawlers.douyin.web.utils import BogusManager
from crawlers.base_crawler import BaseCrawler

# 取自报错日志里的真实 sec_user_id
SEC = "MS4wLjABAAAAdN_lotGxXIKfAG7itXmYqIa6wQftwlrFlRjj794t4TI"


def brief(resp):
    if not isinstance(resp, dict):
        return f"(non-dict: {type(resp).__name__})"
    user = resp.get("user") or {}
    return (f"status_code={resp.get('status_code')} has_user={bool(user)} "
            f"nickname={user.get('nickname')!r} room_id={user.get('room_id')} "
            f"live_status={user.get('live_status')}")


async def main():
    dy = DouyinWebCrawler()

    # 1) 现状: handler_user_profile 用 X-Bogus
    try:
        r = await dy.handler_user_profile(SEC)
        print("X-Bogus (现状):", brief(r))
    except Exception as e:
        print("X-Bogus (现状): EXC", type(e).__name__, str(e)[:120])

    # 2) 拟修: 同一请求改用 a_bogus
    kwargs = await dy.get_douyin_headers()
    ua = kwargs["headers"]["User-Agent"]
    async with BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"]) as crawler:
        pd = UserProfile(sec_user_id=SEC).dict()
        pd["msToken"] = ""
        ab = BogusManager.ab_model_2_endpoint(pd, ua)
        endpoint = f"{DouyinAPIEndpoints.USER_DETAIL}?{urlencode(pd)}&a_bogus={ab}"
        try:
            r2 = await crawler.fetch_get_json(endpoint)
            print("a_bogus (拟修):", brief(r2))
        except Exception as e:
            print("a_bogus (拟修): EXC", type(e).__name__, str(e)[:120])


if __name__ == "__main__":
    asyncio.run(main())
