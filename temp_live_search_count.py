import asyncio
import json
from urllib.parse import urlencode

from crawlers.douyin.web.web_crawler import DouyinWebCrawler
from crawlers.douyin.web.endpoints import DouyinAPIEndpoints
from crawlers.douyin.web.utils import BogusManager, TokenManager
from crawlers.base_crawler import BaseCrawler

KEYWORD = "彩虹六号"
COUNT = 15


def build_params(offset, count, mstoken):
    return {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "search_channel": "aweme_live",
        "keyword": KEYWORD,
        "search_source": "normal_search",
        "query_correct_type": "1",
        "is_filter_search": "0",
        "from_group_id": "",
        "disable_rs": "0",
        "offset": str(offset),
        "count": str(count),
        "need_filter_settings": "1",
        "list_type": "single",
        "pc_client_type": "1",
        "pc_libra_divert": "Windows",
        "support_h265": "1",
        "support_dash": "1",
        "cpu_core_num": "12",
        "version_code": "170400",
        "version_name": "17.4.0",
        "update_version_code": "170400",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "148.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "148.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "device_memory": "16",
        "platform": "PC",
        "downlink": "10",
        "effective_type": "4g",
        "round_trip_time": "0",
        "msToken": mstoken,
    }


async def main():
    dy = DouyinWebCrawler()
    kwargs = await dy.get_douyin_headers()
    ua = kwargs["headers"]["User-Agent"]
    mstoken = TokenManager.gen_real_msToken()

    anchors = {}          # key -> nickname
    living = {}           # key -> bool (status == 2)
    offset = 0
    page = 0

    async with BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"]) as crawler:
        while True:
            page += 1
            params = build_params(offset, COUNT, mstoken)
            a_bogus = BogusManager.ab_model_2_endpoint(params, ua)
            endpoint = f"{DouyinAPIEndpoints.LIVE_SEARCH}?{urlencode(params)}&a_bogus={a_bogus}"
            resp = await crawler.fetch_get_json(endpoint)

            status_code = resp.get("status_code")
            data = resp.get("data") or []
            has_more = resp.get("has_more")
            cursor = resp.get("cursor")

            new = 0
            for it in data:
                L = it.get("lives") or {}
                a = L.get("author") or {}
                key = a.get("sec_uid") or a.get("uid") or L.get("aweme_id")
                rd = L.get("rawdata")
                status = None
                if isinstance(rd, str):
                    try:
                        rd = json.loads(rd)
                    except Exception:
                        rd = None
                if isinstance(rd, dict):
                    status = rd.get("status")
                if key and key not in anchors:
                    anchors[key] = a.get("nickname") or ""
                    living[key] = (status == 2)
                    new += 1

            print(f"page {page}: offset={offset} status_code={status_code} "
                  f"got={len(data)} new={new} total={len(anchors)} "
                  f"has_more={has_more} cursor={cursor}")

            if status_code not in (0, None) and not data:
                print("  -> non-zero status / blocked, raw snippet:")
                print("  ", json.dumps(resp, ensure_ascii=False)[:400])
                break
            if not data or not has_more:
                break
            offset = cursor if cursor else (offset + COUNT)
            if page >= 60:
                print("safety stop at 60 pages")
                break
            await asyncio.sleep(0.5)

    print("=" * 50)
    print("UNIQUE ANCHORS RETURNED:", len(anchors))
    print("MARKED status==2 (living):", sum(1 for v in living.values() if v))
    for i, (k, v) in enumerate(anchors.items(), 1):
        print(f"{i:3d}. {v}  (living={living.get(k)})")


if __name__ == "__main__":
    asyncio.run(main())
