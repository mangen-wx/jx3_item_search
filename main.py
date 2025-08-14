import httpx # 使用 httpx 进行异步 HTTP 请求
from bs4 import BeautifulSoup # 用于解析 HTML，尽管这里主要用API，但保留以防万一
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 注册插件，严格按照您要求的单行格式，插件名字使用下划线
@register("jx3_item_search", "沐沐沐倾", "查询剑网3物品百科信息，支持模糊搜索。", "1.0.0")
class Jx3ItemSearchStar(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.base_search_url = "https://www.jx3box.com/api/wiki/item/search"
        self.item_detail_base_url = "https://www.jx3box.com/item/" # 用于生成物品详情链接
        logger.info("剑网3物品查询插件初始化完成。")

    async def initialize(self):
        """异步初始化方法，插件实例化后会自动调用。"""
        logger.info("剑网3物品查询插件异步初始化中...")
        # 可以在这里进行一些异步的初始化操作，例如加载配置等
        logger.info("剑网3物品查询插件异步初始化完成。")

    @filter.command("剑网3物品", "jx3物品") # 修正为有效的命令装饰器，并使用您指定的关键词
    async def search_jx3_item(self, event: AstrMessageEvent):
        """
        查询剑网3物品百科信息。
        用法：/剑网3物品 [物品名称] 或 /jx3物品 [物品名称]
        """
        item_name = event.get_arg_text() # 获取指令后的参数作为物品名称

        if not item_name:
            yield event.plain_result("请提供您要查询的物品名称。例如：/剑网3物品 沧海间")
            logger.warning(f"用户 {event.get_sender_name()} 未提供物品名称进行查询。")
            return

        logger.info(f"收到来自 {event.get_sender_name()} 的物品查询请求：'{item_name}'")

        try:
            async with httpx.AsyncClient() as client:
                # 构建API请求参数
                params = {
                    "keyword": item_name,
                    "page": 1,
                    "per": 5 # 限制返回结果数量，避免刷屏
                }
                response = await client.get(self.base_search_url, params=params, timeout=10)
                response.raise_for_status() # 检查HTTP请求是否成功

                data = response.json()

                if data and data.get('code') == 200 and data.get('data'):
                    items = data['data']['list']
                    if items:
                        result_messages = [f"为您找到以下与 '{item_name}' 相关的物品："]
                        for item in items:
                            item_id = item.get('id')
                            item_name_found = item.get('name', '未知名称')
                            item_desc = item.get('desc', '暂无描述')

                            detail_link = f"{self.item_detail_base_url}{item_id}" if item_id else "无详细链接"

                            msg = (
                                f"名称: {item_name_found}\n"
                                f"描述: {item_desc}\n"
                                f"详情: {detail_link}"
                            )
                            result_messages.append(msg)
                        
                        yield event.plain_result("\n\n".join(result_messages))
                        logger.info(f"成功为 '{item_name}' 找到 {len(items)} 个匹配物品。")
                    else:
                        yield event.plain_result(f"未找到与 '{item_name}' 相关的物品。")
                        logger.info(f"未找到与 '{item_name}' 相关的物品。")
                else:
                    error_msg = data.get('msg', '未知错误')
                    yield event.plain_result(f"查询失败或API返回异常：{error_msg}")
                    logger.error(f"JX3Box API返回错误：{error_msg}，查询关键词：'{item_name}'")

        except httpx.RequestError as e:
            logger.error(f"请求JX3Box API失败: {e}", exc_info=True)
            yield event.plain_result(f"查询物品时发生网络错误，请稍后再试。错误信息: {e}")
        except Exception as e:
            logger.error(f"处理物品查询时发生未知错误: {e}", exc_info=True)
            yield event.plain_result("查询物品时发生内部错误，请联系管理员。")

    async def terminate(self):
        """异步销毁方法，插件被卸载/停用时会调用。"""
        logger.info("剑网3物品查询插件正在销毁。")
        # 可以在这里进行资源清理等操作
        logger.info("剑网3物品查询插件销毁完成。")

