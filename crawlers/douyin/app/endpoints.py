class DouyinAppEndpoints:
    """
    API Endpoints for Douyin APP
    """

    # 抖音移动端域名 (Douyin Mobile Domain)
    DOUYIN_APP_DOMAIN = "https://aweme.snssdk.com"

    # 视频Feed (Video Feed)
    HOME_FEED = f"{DOUYIN_APP_DOMAIN}/aweme/v1/feed/"

    # 视频详情 (Video Detail)
    VIDEO_DETAIL = f"{DOUYIN_APP_DOMAIN}/aweme/v1/aweme/detail/"
