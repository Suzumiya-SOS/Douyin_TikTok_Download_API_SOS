from fastapi import APIRouter, Query, Request, HTTPException
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel

from crawlers.douyin.app.app_crawler import DouyinAPPCrawler
from crawlers.douyin.app.creator_crawler import DouyinCreatorCrawler

router = APIRouter()
DouyinAPPCrawler = DouyinAPPCrawler()
DouyinCreatorCrawler = DouyinCreatorCrawler()


# 获取单个作品数据
@router.get("/fetch_one_video",
            response_model=ResponseModel,
            summary="获取单个作品数据/Get single video data"
            )
async def fetch_one_video(request: Request,
                          aweme_id: str = Query(example="7339393672959757570", description="作品id/Video id")):
    """
    # [中文]
    ### 用途:
    - 获取单个抖音作品数据（抖音App移动端接口）
    ### 参数:
    - aweme_id: 作品id
    ### 返回:
    - 作品数据

    # [English]
    ### Purpose:
    - Get single Douyin video data (Douyin App mobile API)
    ### Parameters:
    - aweme_id: Video id
    ### Return:
    - Video data

    # [示例/Example]
    aweme_id = "7339393672959757570"
    """
    try:
        data = await DouyinAPPCrawler.fetch_one_video(aweme_id)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 获取单个作品详情数据（detail接口）
@router.get("/fetch_video_detail",
            response_model=ResponseModel,
            summary="获取单个作品详情数据/Get single video detail data"
            )
async def fetch_video_detail(request: Request,
                              aweme_id: str = Query(example="7339393672959757570", description="作品id/Video id")):
    """
    # [中文]
    ### 用途:
    - 获取单个抖音作品详情数据（aweme/v1/aweme/detail/ 端点，可能包含播放量）
    ### 参数:
    - aweme_id: 作品id
    ### 返回:
    - 作品详情数据

    # [English]
    ### Purpose:
    - Get single Douyin video detail data (aweme/v1/aweme/detail/ endpoint, may include play_count)
    ### Parameters:
    - aweme_id: Video id
    ### Return:
    - Video detail data
    """
    try:
        data = await DouyinAPPCrawler.fetch_video_detail(aweme_id)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 通过创作者平台获取作品统计数据（含真实播放量）
@router.get("/fetch_creator_video_stats",
            response_model=ResponseModel,
            summary="通过创作者平台获取作品统计/Get video stats via Creator Platform"
            )
async def fetch_creator_video_stats(
        request: Request,
        aweme_id: str = Query(
            example="7619222887555239206",
            description="作品id/Video id（必须属于当前Cookie对应的账号 / Must belong to the Cookie account）"
        )
):
    """
    # [中文]
    ### 用途:
    - 通过抖音创作者平台获取作品的真实统计数据，包括真实播放量（play_count）
    - 抖音已从所有公开 API 中移除 play_count，只有通过此创作者平台接口才能获取
    ### 重要限制:
    - **Cookie 必须属于视频的发布者账号**，否则将返回无权限错误
    - 普通用户 Cookie 无法查询他人视频的播放量
    ### 参数:
    - aweme_id: 作品id（必须是当前 Cookie 账号发布的视频）
    ### 返回:
    - 真实统计数据，包括 play_count、digg_count、comment_count、share_count 等

    # [English]
    ### Purpose:
    - Get real video statistics via Douyin Creator Platform, including real play_count
    - Douyin removed play_count from all public APIs; only the creator platform can return it
    ### Important Limitation:
    - **Cookie must belong to the VIDEO AUTHOR's account**, otherwise "no permission" error
    - Regular user cookies cannot query other users' video play counts
    ### Parameters:
    - aweme_id: Video id (must be published by the current Cookie account)
    ### Return:
    - Real statistics including play_count, digg_count, comment_count, share_count, etc.

    # [示例/Example]
    aweme_id = "7619222887555239206"
    """
    try:
        data = await DouyinCreatorCrawler.fetch_video_play_count(aweme_id)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except PermissionError as e:
        status_code = 403
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())
    except ValueError as e:
        status_code = 404
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 获取创作者平台作品统计列表（当前账号的所有作品）
@router.get("/fetch_creator_items_list",
            response_model=ResponseModel,
            summary="获取创作者平台作品统计列表/Get creator platform items statistics list"
            )
async def fetch_creator_items_list(
        request: Request,
        count: int = Query(default=20, description="每页数量/Count per page"),
        cursor: int = Query(default=0, description="分页游标/Pagination cursor"),
):
    """
    # [中文]
    ### 用途:
    - 获取当前 Cookie 账号发布的所有作品统计列表（含真实 play_count）
    - 通过抖音创作者平台接口获取，返回真实播放量等统计数据
    ### 参数:
    - count: 每页数量（默认20）
    - cursor: 分页游标（默认0，首页）
    ### 返回:
    - 作品统计列表，每个作品包含真实的 play_count 等统计信息

    # [English]
    ### Purpose:
    - Get statistics list for all videos published by the current Cookie account (with real play_count)
    - Retrieved from Douyin Creator Platform, returns real play counts
    ### Parameters:
    - count: Items per page (default 20)
    - cursor: Pagination cursor (default 0 for first page)
    ### Return:
    - List of video statistics including real play_count for each video
    """
    try:
        data = await DouyinCreatorCrawler.fetch_item_statistics_list(count=count, cursor=cursor)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except PermissionError as e:
        status_code = 403
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())
