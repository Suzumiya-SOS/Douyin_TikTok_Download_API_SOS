"""
抖音创作者平台爬虫
Douyin Creator Platform Crawler

说明 / Notes:
  此爬虫使用 creator.douyin.com API 获取视频统计数据（含真实播放量）。
  条件：需要使用视频作者自己的有效 Cookie，才能获取该作者发布视频的统计数据。
  若 Cookie 不属于视频作者，将返回 "无权限" 错误。

  This crawler uses creator.douyin.com APIs to retrieve real video statistics (including play_count).
  Requirement: The cookie must belong to the VIDEO AUTHOR's account.
  If the cookie does not belong to the author, a "no permission" error will be returned.
"""

import asyncio
import os
import yaml

from tenacity import retry, stop_after_attempt, wait_fixed
from crawlers.base_crawler import BaseCrawler
from crawlers.utils.logger import logger

# 配置文件路径
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 读取 web 配置（获取 Cookie）
with open(f"{path}/web/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class DouyinCreatorEndpoints:
    """Creator platform API endpoints"""
    CREATOR_DOMAIN = "https://creator.douyin.com"

    # 作品统计数据列表（需要是账号自己的视频）
    # Item statistics list (only works for videos owned by the authenticated account)
    ITEM_DATA_LIST = f"{CREATOR_DOMAIN}/aweme/v1/creator/data/item/list/"

    # 作品概览统计（仅适用于账号自己的视频）
    # Item overview stats (only for own videos)
    ITEM_STAT = f"{CREATOR_DOMAIN}/aweme/v1/creator/data/item/stat/"


class DouyinCreatorCrawler:
    """
    抖音创作者平台爬虫
    用于获取账号自身发布作品的真实统计数据（播放量等）。
    注意：只能获取当前登录账号自己发布视频的统计，无法获取他人视频的数据。
    """

    async def get_creator_headers(self):
        """获取 creator.douyin.com 专用请求头"""
        douyin_config = config["TokenManager"]["douyin"]
        return {
            "headers": {
                "User-Agent": douyin_config["headers"]["User-Agent"],
                "Cookie": douyin_config["headers"]["Cookie"],
                "Referer": "https://creator.douyin.com/creator-micro/home",
                "Origin": "https://creator.douyin.com",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": douyin_config["headers"]["Accept-Language"],
            },
            "proxies": {
                "http://": douyin_config["proxies"]["http"],
                "https://": douyin_config["proxies"]["https"],
            }
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def fetch_item_statistics_list(self, count: int = 20, cursor: int = 0):
        """
        获取账号自身发布作品的统计数据列表（含真实播放量）
        Get statistics list for the authenticated account's own videos (includes real play_count)

        Returns:
            dict: 包含 aweme_list 的响应数据，每个作品包含真实的统计信息（play_count 等）
                  Response with aweme_list, each item containing real statistics
        """
        kwargs = await self.get_creator_headers()
        base_crawler = BaseCrawler(
            proxies=kwargs["proxies"],
            crawler_headers=kwargs["headers"]
        )
        params = {
            "count": count,
            "cursor": cursor,
        }
        from urllib.parse import urlencode
        url = f"{DouyinCreatorEndpoints.ITEM_DATA_LIST}?{urlencode(params)}"

        async with base_crawler as crawler:
            response = await crawler.fetch_get_json(url)

        if not response:
            raise Exception("Creator platform returned empty response")

        status_code = response.get("status_code", -1)
        if status_code == 7:
            raise PermissionError(
                "账号无权限访问创作者数据平台 / No permission to access creator data. "
                "此接口仅适用于已发布视频的创作者账号，且 Cookie 必须属于视频作者本人。"
            )
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def fetch_video_play_count(self, aweme_id: str):
        """
        通过创作者数据平台获取单个作品的真实播放量
        Get real play_count for a specific video via creator platform

        重要提示 / Important:
          - Cookie 必须属于该视频的发布者账号
          - The Cookie must belong to the VIDEO AUTHOR's account
          - 若视频不属于当前账号，将抛出 PermissionError

        Args:
            aweme_id: 视频作品ID

        Returns:
            dict: 包含 play_count 的统计数据 / Statistics dict with real play_count
        """
        # Creator platform lists all items for the account — paginate until we find the target
        cursor = 0
        count = 20
        pages_checked = 0
        max_pages = 10  # Check up to 200 most recent videos

        while pages_checked < max_pages:
            response = await self.fetch_item_statistics_list(count=count, cursor=cursor)

            aweme_list = response.get("aweme_list", [])
            if not aweme_list:
                break

            for aweme in aweme_list:
                if aweme.get("aweme_id") == aweme_id:
                    statistics = aweme.get("statistics", {})
                    logger.info(f"Found video {aweme_id} in creator data: {statistics}")
                    return statistics

            has_more = response.get("has_more", 0)
            if not has_more:
                break

            cursor = response.get("cursor", cursor + count)
            pages_checked += 1

        raise ValueError(
            f"视频 {aweme_id} 未在当前账号发布的作品中找到 / "
            f"Video {aweme_id} not found in the authenticated account's published videos. "
            f"只能查询账号自己发布的视频统计。"
        )

    async def main(self):
        """测试: 打印账号最近发布视频的统计数据"""
        print("Fetching creator statistics for authenticated account's videos...")
        try:
            result = await self.fetch_item_statistics_list(count=5)
            aweme_list = result.get("aweme_list", [])
            print(f"Got {len(aweme_list)} videos:")
            for aweme in aweme_list:
                vid = aweme.get("aweme_id")
                stats = aweme.get("statistics", {})
                desc = aweme.get("desc", "")[:30]
                print(f"  [{vid}] {desc!r}")
                print(f"    play_count={stats.get('play_count')}, digg={stats.get('digg_count')}")
        except PermissionError as e:
            print(f"Permission Error: {e}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import time
    crawler = DouyinCreatorCrawler()
    start = time.time()
    asyncio.run(crawler.main())
    print(f"耗时：{time.time() - start:.2f}s")
