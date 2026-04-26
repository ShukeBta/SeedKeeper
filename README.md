# SeedKeeper 做种助手插件

## 📋 项目概述

**SeedKeeper** 是一款专为 MoviePilot v2 开发的做种助手插件，解决以下核心问题：

1. 🔄 **转移后无法做种** - MoviePilot 转移文件后，qBittorrent 种子失去关联
2. 🔗 **硬链接失败** - 部分场景下硬链接容易失败
3. 📊 **做种管理混乱** - 缺乏统一的做种策略管理

## 🏗️ 项目结构

```
seedkeeper/
├── plugins.v2/                    # MoviePilot V2 插件后端
│   └── seedkeeper/
│       ├── __init__.py            # 插件核心代码
│       ├── package.v2.json        # V2 插件索引
│       └── README.md              # 插件说明
├── frontend/                       # Vue 前端项目（Module Federation）
│   ├── src/
│   │   ├── components/
│   │   │   ├── Page.vue           # 详情页面组件
│   │   │   ├── Config.vue         # 配置页面组件
│   │   │   ├── Dashboard.vue      # 仪表板小组件
│   │   │   └── AppPage.vue        # 侧栏全页组件
│   │   ├── styles/
│   │   │   └── variables.scss    # SCSS 变量
│   │   ├── main.ts               # Vue 入口
│   │   └── env.d.ts              # 类型声明
│   ├── vite.config.ts            # Vite + Federation 配置
│   ├── tsconfig.json             # TypeScript 配置
│   └── package.json              # 前端依赖
└── README.md                      # 项目说明
```

## 📦 安装

### 方式一：插件市场安装（推荐）

1. 进入 MoviePilot 后台 → **设置** → **插件市场**
2. 点击「添加源」，输入：
   ```
   https://github.com/ShukeBta/SeedKeeper
   ```
3. 点击**刷新**，搜索 `SeedKeeper` 或 `seedkeeper`
4. 点击**安装**
5. 安装完成后在**我的插件**中找到 SeedKeeper，启用并配置

> ⚠️ 如已安装旧版本，请先卸载后再安装新版本

### 方式二：本地安装

1. 下载本仓库的 `plugins.v2/seedkeeper/` 目录
2. 将其复制到 MoviePilot 的 `plugins.v2/` 目录下
3. 如果有前端 `dist/` 目录，也一并复制
4. 重启 MoviePilot

### 方式三：开发者安装

```bash
# 克隆仓库
git clone https://github.com/ShukeBta/SeedKeeper.git

# 复制插件目录
cp -r plugins.v2/seedkeeper /path/to/MoviePilot/plugins.v2/

# 构建前端（如需开发前端）
cd frontend
npm install
npm run build

# 复制前端构建产物
cp -r dist /path/to/MoviePilot/plugins.v2/seedkeeper/

# 重启 MoviePilot
```

## 🚀 快速开始

### 1. 启用插件

安装完成后：
1. 进入 **插件** 页面
2. 找到 **SeedKeeper** 
3. 点击启用开关

### 2. 配置做种策略

在插件设置中配置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 自动做种 | 下载完成自动开始做种 | ✅ 开启 |
| 做种策略 | 按分享率/按做种时间/手动 | 按分享率 |
| 最小分享率 | 达到此分享率后开始计算 | 1.0 |
| 最大分享率 | 达到此分享率后自动处理 | 5.0 |
| 做种时间限制 | 小时，0 表示不限制 | 0 |
| 达到限制后删除 | 删除种子还是暂停 | 暂停 |

### 3. 开发前端

```bash
cd frontend
npm install
npm run dev    # 开发模式（端口 5001）
npm run build  # 生产构建
```

### 4. 本地调试

```bash
# 在 MoviePilot 环境变量中设置
PLUGIN_AUTO_RELOAD=true
```

重启 MoviePilot 后，修改插件代码会自动重新加载。

## 📖 功能说明

### 核心功能

| 功能 | 说明 |
|------|------|
| 🌱 智能做种 | 自动监听下载完成事件，自动接管做种 |
| 📊 做种策略 | 支持按分享率/按做种时间/手动管理 |
| 🔧 配置灵活 | 支持 qBittorrent / Transmission |
| 📈 统计面板 | Dashboard 实时显示做种状态 |

### 做种策略

| 策略 | 说明 |
|------|------|
| **按分享率** | 达到最小分享率开始计算，达到最大分享率自动处理 |
| **按做种时间** | 设定做种时间上限，到期自动处理 |
| **手动管理** | 完全手动控制每个任务 |

## 🔌 API 接口

| 接口路径 | 方法 | 说明 |
|----------|------|------|
| `/api/v1/plugin/seedkeeper/stats` | GET | 获取做种统计 |
| `/api/v1/plugin/seedkeeper/tasks` | GET | 获取任务列表 |
| `/api/v1/plugin/seedkeeper/task/resume` | POST | 恢复做种 |
| `/api/v1/plugin/seedkeeper/task/pause` | POST | 暂停做种 |
| `/api/v1/plugin/seedkeeper/task/remove` | POST | 删除种子 |
| `/api/v1/plugin/seedkeeper/transfer/hook` | POST | 转移完成回调 |

## 🛠️ 技术栈

- **后端**: Python 3, MoviePilot Plugin V2
- **前端**: Vue 3, TypeScript, Vuetify 3
- **构建**: Vite 5, Module Federation
- **通信**: REST API

## 📝 开发指南

### 后端插件开发

参考 [MoviePilot V2 插件开发指南](https://github.com/jxxghp/MoviePilot-Plugins/blob/main/docs/V2_Plugin_Development.md)

### 前端组件开发

参考 [MoviePilot 前端模块联邦开发指南](https://github.com/jxxghp/MoviePilot-Frontend/blob/v2/docs/module-federation-guide.md)

### 关键配置

```python
# 后端插件返回 Vue 渲染模式
def get_render_mode(self) -> Tuple[str, str]:
    return "vue", "dist/assets"

# 注册侧栏导航
def get_sidebar_nav(self) -> List[Dict[str, Any]]:
    return [{
        "nav_key": "main",
        "title": "SeedKeeper",
        "icon": "mdi-seed",
        "section": "organize",
        "permission": "manage",
        "order": 15
    }]
```

## ⚠️ 注意事项

1. **下载器配置**: 确保 qBittorrent 设置 "做种至" 为 0（无限做种）
2. **硬链接**: 需要源目录和目标目录在同一文件系统
3. **权限**: 插件需要 `manage` 权限级别

## 📄 License

MIT License
