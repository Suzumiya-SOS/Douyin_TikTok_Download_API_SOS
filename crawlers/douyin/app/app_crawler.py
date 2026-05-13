# ==============================================================================
# Copyright (C) 2021 Evil0ctal
#
# This file is part of the Douyin_TikTok_Download_API project.
#
# This project is licensed under the Apache License 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import asyncio
import time
import yaml
import os

from crawlers.base_crawler import BaseCrawler
from crawlers.douyin.app.endpoints import DouyinAppEndpoints
from crawlers.douyin.app.models import FeedVideoDetail, VideoDetail
from crawlers.utils.utils import model_to_query_string

from tenacity import *

path = os.path.abspath(os.path.dirname(__file__))

with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class DouyinAPPCrawler:

    async def get_douyin_app_headers(self):
        douyin_config = config["TokenManager"]["douyin"]
        kwargs = {
            "headers": {
                "User-Agent": douyin_config["headers"]["User-Agent"],
                "Cookie": douyin_config["headers"]["Cookie"] or "",
            },
            "proxies": {
                "http://": douyin_config["proxies"]["http"],
                "https://": douyin_config["proxies"]["https"],
            }
        }
        return kwargs

    """-------------------------------------------------------handler接口列表-------------------------------------------------------"""

    # 获取单个作品数据 / Fetch single video data
    @retry(stop=stop_after_attempt(10), wait=wait_fixed(1))
    async def fetch_one_video(self, aweme_id: str):
        kwargs = await self.get_douyin_app_headers()
        params = FeedVideoDetail(aweme_id=aweme_id)
        param_str = model_to_query_string(params)
        url = f"{DouyinAppEndpoints.HOME_FEED}?{param_str}"
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            response = await crawler.fetch_get_json(url)
            aweme_list = response.get("aweme_list", [])
            if not aweme_list:
                raise Exception("未获取到作品数据 / No video data returned")
            video = aweme_list[0]
            if video.get("aweme_id") != aweme_id:
                raise Exception("作品ID不匹配 / Video ID mismatch")
        return video

    # 获取单个作品详情数据（detail接口） / Fetch single video detail
    @retry(stop=stop_after_attempt(10), wait=wait_fixed(1))
    async def fetch_video_detail(self, aweme_id: str):
        kwargs = await self.get_douyin_app_headers()
        params = VideoDetail(aweme_id=aweme_id)
        param_str = model_to_query_string(params)
        url = f"{DouyinAppEndpoints.VIDEO_DETAIL}?{param_str}"
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            response = await crawler.fetch_get_json(url)
            aweme_detail = response.get("aweme_detail")
            if not aweme_detail:
                raise Exception("未获取到作品数据 / No video data returned")
        return aweme_detail

    """-------------------------------------------------------main------------------------------------------------------"""

    async def main(self):
        aweme_id = "7339393672959757570"
        response = await self.fetch_one_video(aweme_id)
        print(response)


if __name__ == "__main__":
    crawler = DouyinAPPCrawler()
    start = time.time()
    asyncio.run(crawler.main())
    end = time.time()
    print(f"耗时：{end - start}")
