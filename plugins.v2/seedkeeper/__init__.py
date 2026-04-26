"""
SeedKeeper - 做种助手插件
用于管理 MoviePilot 转移后的种子做种任务
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType
from app.helper.event import eventmanager
import json
from pathlib import Path
from datetime import datetime


class Seedkeeper(_PluginBase):
    """SeedKeeper 做种助手插件"""
    
    # ==================== 插件元数据 ====================
    plugin_name = "SeedKeeper"
    plugin_desc = "做种助手 - 智能管理转移后的种子做种任务"
    plugin_icon = "mdi-seed"
    plugin_version = "1.0.0"
    plugin_author = "SeedKeeper"
    author_url = "https://github.com/seedkeeper"
    plugin_config_prefix = "seedkeeper_"
    plugin_order = 50
    auth_level = 1

    # ==================== Vue 渲染模式 ====================
    def get_render_mode(self) -> Tuple[str, str]:
        """
        获取插件渲染模式
        返回: (渲染模式, 组件路径)
        vuetify: JSON 配置模式
        vue: Module Federation 远程组件模式
        """
        return "vue", "dist/assets"
    
    # ==================== 侧栏导航 ====================
    def get_sidebar_nav(self) -> List[Dict[str, Any]]:
        """
        注册侧栏导航入口
        """
        return [
            {
                "nav_key": "main",
                "title": "SeedKeeper",
                "icon": "mdi-seed",
                "section": "organize",  # 放在整理分类下
                "permission": "manage",
                "order": 15
            }
        ]

    # ==================== 可配置属性 ====================
    _enabled: bool = False
    _auto_seed: bool = True
    _min_ratio: float = 1.0
    _max_ratio: float = 5.0
    _seed_time_limit: int = 0
    _remove_on_limit: bool = False
    _strategy: str = "ratio"
    _downloaders: List[str] = []

    # ==================== 初始化 ====================
    def init_plugin(self, config: dict = None) -> None:
        """初始化插件配置"""
        if config:
            self._enabled = config.get("enabled", False)
            self._auto_seed = config.get("auto_seed", True)
            self._min_ratio = float(config.get("min_ratio", 1.0))
            self._max_ratio = float(config.get("max_ratio", 5.0))
            self._seed_time_limit = int(config.get("seed_time_limit", 0))
            self._remove_on_limit = config.get("remove_on_limit", False)
            self._strategy = config.get("strategy", "ratio")
            self._downloaders = config.get("downloaders", [])
        logger.info(f"SeedKeeper 插件初始化完成，auto_seed={self._auto_seed}")

    # ==================== 状态管理 ====================
    def get_state(self) -> bool:
        """获取插件运行状态"""
        return self._enabled

    def stop_service(self) -> None:
        """停止插件服务"""
        logger.info("SeedKeeper 插件已停止")

    # ==================== 配置页面 ====================
    def get_form(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """获取配置表单"""
        return [
            {
                "component": "VSwitch",
                "props": {
                    "label": "启用插件",
                    "hint": "开启后自动管理做种任务",
                    "persistent-hint": True,
                },
                "model": "enabled"
            },
            {
                "component": "VSwitch",
                "props": {
                    "label": "自动做种",
                    "hint": "下载完成后自动开始做种",
                    "persistent-hint": True,
                },
                "model": "auto_seed"
            },
            {
                "component": "VSelect",
                "props": {
                    "label": "做种策略",
                    "items": [
                        {"title": "按分享率", "value": "ratio"},
                        {"title": "按做种时间", "value": "seedtime"},
                        {"title": "手动管理", "value": "manual"}
                    ],
                    "hint": "决定何时停止做种的策略",
                    "persistent-hint": True,
                },
                "model": "strategy"
            },
            {
                "component": "VTextField",
                "props": {
                    "label": "最小分享率",
                    "type": "number",
                    "hint": "达到此分享率后开始计算",
                    "persistent-hint": True,
                },
                "model": "min_ratio"
            },
            {
                "component": "VTextField",
                "props": {
                    "label": "最大分享率",
                    "type": "number",
                    "hint": "达到此分享率后自动处理",
                    "persistent-hint": True,
                },
                "model": "max_ratio"
            },
            {
                "component": "VTextField",
                "props": {
                    "label": "做种时间限制（小时）",
                    "type": "number",
                    "hint": "0 表示不做限制",
                    "persistent-hint": True,
                },
                "model": "seed_time_limit"
            },
            {
                "component": "VSwitch",
                "props": {
                    "label": "达到限制后删除种子",
                    "hint": "否则只暂停不做种",
                    "persistent-hint": True,
                },
                "model": "remove_on_limit"
            },
            {
                "component": "VSelect",
                "props": {
                    "label": "下载器",
                    "items": [
                        {"title": "全部", "value": ""},
                        {"title": "qBittorrent", "value": "qbittorrent"},
                        {"title": "Transmission", "value": "transmission"}
                    ],
                    "multiple": True,
                    "chips": True,
                    "hint": "选择要管理的下载器",
                    "persistent-hint": True,
                },
                "model": "downloaders"
            }
        ], {
            "enabled": False,
            "auto_seed": True,
            "strategy": "ratio",
            "min_ratio": 1.0,
            "max_ratio": 5.0,
            "seed_time_limit": 0,
            "remove_on_limit": False,
            "downloaders": []
        }

    # ==================== 详情页面 ====================
    def get_page(self) -> List[Dict[str, Any]]:
        """获取详情页面"""
        return [
            {
                "component": "VCard",
                "props": {"class": "mb-4"},
                "content": [
                    {
                        "component": "VCardTitle",
                        "props": {"class": "text-h6"},
                        "content": "📊 做种统计"
                    },
                    {
                        "component": "VCardText",
                        "content": [
                            {
                                "component": "VRow",
                                "content": [
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 4},
                                        "content": [
                                            {
                                                "component": "VSheet",
                                                "props": {"class": "text-center pa-2", "color": "primary"},
                                                "content": [
                                                    {"component": "div", "props": {"class": "text-h4"}, "content": "{{ stats.active }}"},
                                                    {"component": "div", "props": {"class": "text-caption"}, "content": "做种中"}
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 4},
                                        "content": [
                                            {
                                                "component": "VSheet",
                                                "props": {"class": "text-center pa-2", "color": "success"},
                                                "content": [
                                                    {"component": "div", "props": {"class": "text-h4"}, "content": "{{ stats.completed }}"},
                                                    {"component": "div", "props": {"class": "text-caption"}, "content": "已完成"}
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 4},
                                        "content": [
                                            {
                                                "component": "VSheet",
                                                "props": {"class": "text-center pa-2", "color": "warning"},
                                                "content": [
                                                    {"component": "div", "props": {"class": "text-h4"}, "content": "{{ stats.pending }}"},
                                                    {"component": "div", "props": {"class": "text-caption"}, "content": "等待中"}
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "component": "VCard",
                "content": [
                    {
                        "component": "VCardTitle",
                        "props": {"class": "d-flex justify-space-between align-center"},
                        "content": [
                            {"component": "span", "content": "🌱 做种任务列表"},
                            {
                                "component": "VBtn",
                                "props": {
                                    "size": "small",
                                    "color": "primary",
                                    "variant": "tonal",
                                    "@click": "refreshTasks"
                                },
                                "content": "刷新"
                            }
                        ]
                    },
                    {
                        "component": "VCardText",
                        "content": [
                            {
                                "component": "VTable",
                                "props": {"density": "compact"},
                                "content": {
                                    "headers": [
                                        {"title": "任务名称"},
                                        {"title": "当前分享率"},
                                        {"title": "做种时间"},
                                        {"title": "状态"},
                                        {"title": "操作"}
                                    ],
                                    "items": "{{ tasks }}"
                                }
                            }
                        ]
                    }
                ]
            }
        ]

    # ==================== API 接口 ====================
    def get_api(self) -> List[Dict[str, Any]]:
        """获取插件 API"""
        return [
            {
                "path": "/stats",
                "endpoint": self.get_stats,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取做种统计"
            },
            {
                "path": "/tasks",
                "endpoint": self.get_tasks,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取做种任务列表"
            },
            {
                "path": "/task/resume",
                "endpoint": self.resume_task,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "恢复做种"
            },
            {
                "path": "/task/pause",
                "endpoint": self.pause_task,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "暂停做种"
            },
            {
                "path": "/task/remove",
                "endpoint": self.remove_task,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "删除种子"
            },
            {
                "path": "/transfer/hook",
                "endpoint": self.transfer_hook,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "转移完成回调"
            }
        ]

    # ==================== 事件处理 ====================
    @eventmanager.register(EventType.DownloadAdded)
    def on_download_added(self, event) -> None:
        """下载添加事件"""
        if not self._enabled or not self._auto_seed:
            return
        
        event_data = event.event_data or {}
        download_info = event_data.get("download", {})
        self._handle_new_download(download_info)

    @eventmanager.register(EventType.TransferComplete)
    def on_transfer_complete(self, event) -> None:
        """转移完成事件"""
        if not self._enabled:
            return
        
        event_data = event.event_data or {}
        self._handle_transfer_complete(event_data)

    @eventmanager.register(EventType.DownloadComplete)
    def on_download_complete(self, event) -> None:
        """下载完成事件"""
        if not self._enabled or not self._auto_seed:
            return
        
        event_data = event.event_data or {}
        download_info = event_data.get("download", {})
        self._ensure_seeding(download_info)

    # ==================== 业务逻辑 ====================
    def _handle_new_download(self, download_info: dict) -> None:
        """处理新下载任务"""
        torrent_hash = download_info.get("hash") or download_info.get("id")
        if not torrent_hash:
            return
        
        task_info = {
            "hash": torrent_hash,
            "name": download_info.get("title") or download_info.get("name", "Unknown"),
            "added_time": datetime.now().isoformat(),
            "status": "seeding",
            "current_ratio": 0.0,
            "seeding_time": 0
        }
        
        tasks = self.get_data("tasks") or {}
        tasks[torrent_hash] = task_info
        self.save_data("tasks", tasks)
        
        logger.info(f"SeedKeeper: 新任务已添加 {task_info['name']}")

    def _handle_transfer_complete(self, event_data: dict) -> None:
        """处理转移完成事件"""
        src_path = event_data.get("src_path")
        dest_path = event_data.get("dest_path")
        torrent_hash = event_data.get("hash")
        
        if not dest_path:
            return
        
        if self._should_keep_seeding():
            tasks = self.get_data("tasks") or {}
            if torrent_hash and torrent_hash in tasks:
                tasks[torrent_hash]["src_path"] = src_path
                tasks[torrent_hash]["dest_path"] = dest_path
                tasks[torrent_hash]["keep_source"] = True
                self.save_data("tasks", tasks)
                logger.info(f"SeedKeeper: 标记任务需要保留做种 {torrent_hash}")
            else:
                task_info = {
                    "hash": torrent_hash,
                    "src_path": src_path,
                    "dest_path": dest_path,
                    "status": "seeding",
                    "keep_source": True,
                    "added_time": datetime.now().isoformat()
                }
                tasks[torrent_hash] = task_info
                self.save_data("tasks", tasks)

    def _ensure_seeding(self, download_info: dict) -> None:
        """确保种子继续做种"""
        torrent_hash = download_info.get("hash") or download_info.get("id")
        if not torrent_hash:
            return
        
        self._send_seeding_command(torrent_hash)
        logger.info(f"SeedKeeper: 确保做种 {torrent_hash}")

    def _should_keep_seeding(self) -> bool:
        """判断是否应该保持做种"""
        return self._strategy in ["ratio", "seedtime"]

    def _send_seeding_command(self, torrent_hash: str) -> None:
        """发送做种命令到下载器"""
        try:
            from app.helper.downloader import DownloaderHelper
            downloader = DownloaderHelper()
            service = downloader.get_service()
            if service:
                service.set_upload_limit(torrent_hash, 0)
                logger.info(f"SeedKeeper: 已设置 {torrent_hash} 为做种模式")
        except Exception as e:
            logger.error(f"SeedKeeper: 发送做种命令失败 {e}")

    # ==================== API 实现 ====================
    def get_stats(self) -> Dict[str, Any]:
        """获取做种统计"""
        tasks = self.get_data("tasks") or {}
        
        stats = {"total": len(tasks), "active": 0, "completed": 0, "pending": 0}
        
        for task in tasks.values():
            status = task.get("status", "pending")
            if status == "seeding":
                stats["active"] += 1
            elif status == "completed":
                stats["completed"] += 1
            else:
                stats["pending"] += 1
        
        return stats

    def get_tasks(self) -> List[Dict[str, Any]]:
        """获取任务列表"""
        tasks = self.get_data("tasks") or {}
        return list(tasks.values())

    def resume_task(self, data: dict) -> Dict[str, Any]:
        """恢复做种"""
        torrent_hash = data.get("hash")
        if not torrent_hash:
            return {"success": False, "message": "缺少 hash 参数"}
        
        tasks = self.get_data("tasks") or {}
        if torrent_hash in tasks:
            tasks[torrent_hash]["status"] = "seeding"
            self.save_data("tasks", tasks)
            self._send_seeding_command(torrent_hash)
            return {"success": True, "message": "任务已恢复做种"}
        
        return {"success": False, "message": "任务不存在"}

    def pause_task(self, data: dict) -> Dict[str, Any]:
        """暂停做种"""
        torrent_hash = data.get("hash")
        if not torrent_hash:
            return {"success": False, "message": "缺少 hash 参数"}
        
        tasks = self.get_data("tasks") or {}
        if torrent_hash in tasks:
            tasks[torrent_hash]["status"] = "paused"
            self.save_data("tasks", tasks)
            return {"success": True, "message": "任务已暂停"}
        
        return {"success": False, "message": "任务不存在"}

    def remove_task(self, data: dict) -> Dict[str, Any]:
        """删除种子"""
        torrent_hash = data.get("hash")
        if not torrent_hash:
            return {"success": False, "message": "缺少 hash 参数"}
        
        tasks = self.get_data("tasks") or {}
        if torrent_hash in tasks:
            del tasks[torrent_hash]
            self.save_data("tasks", tasks)
            return {"success": True, "message": "种子已删除"}
        
        return {"success": False, "message": "任务不存在"}

    def transfer_hook(self, data: dict) -> Dict[str, Any]:
        """转移完成回调"""
        self._handle_transfer_complete(data)
        return {"success": True, "message": "回调处理完成"}
