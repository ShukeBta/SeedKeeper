# SeedKeeper 做种助手

## 插件简介

SeedKeeper 是一款专为 MoviePilot v2 开发的做种助手插件，旨在解决以下问题：

1. **转移后无法做种**：MoviePilot 转移文件后，qBittorrent 中的种子失去关联文件，无法做种
2. **硬链接失败**：部分场景下硬链接容易失败，导致下载目录和媒体库不一致
3. **做种管理混乱**：缺乏统一的做种策略管理

## 核心功能

### 🌱 智能做种
- 自动监听下载完成事件
- 支持转移完成后自动接管做种任务
- 保留原始种子文件引用

### 📊 做种策略
- **按分享率**：达到设定的最小/最大分享率后自动处理
- **按做种时间**：设定做种时间上限，到期自动处理
- **手动管理**：完全手动控制每个任务

### 🔧 配置灵活
- 支持 qBittorrent / Transmission 下载器
- 可设置最小/最大分享率
- 可设置做种时间限制
- 达到限制后可选择删除或暂停

## 工作原理

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   订阅下载       │ ──► │   文件转移       │ ──► │   SeedKeeper     │
│                 │     │  (硬链接/复制)    │     │   接管做种       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   qBittorrent    │
                                                │   继续做种        │
                                                └─────────────────┘
```

## 安装使用

### 1. 安装插件

在 MoviePilot 插件市场中添加此仓库地址，重启后安装。

### 2. 配置下载器

确保下载器配置正确，建议使用以下配置：
- qBittorrent：勾选 "做种至" 选项，设置为 0（无限做种）
- Transmission：设置 "seedRatioLimit" 为 0

### 3. 插件配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 启用插件 | 开启/关闭插件 | 关闭 |
| 自动做种 | 下载完成自动开始做种 | 开启 |
| 做种策略 | 按分享率/按做种时间/手动 | 按分享率 |
| 最小分享率 | 达到此分享率后开始计算 | 1.0 |
| 最大分享率 | 达到此分享率后自动处理 | 5.0 |
| 做种时间限制 | 小时，0 表示不限制 | 0 |
| 达到限制后删除 | 删除种子还是暂停 | 暂停 |

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/plugin/seedkeeper/stats` | GET | 获取做种统计 |
| `/api/v1/plugin/seedkeeper/tasks` | GET | 获取任务列表 |
| `/api/v1/plugin/seedkeeper/task/resume` | POST | 恢复做种 |
| `/api/v1/plugin/seedkeeper/task/pause` | POST | 暂停做种 |
| `/api/v1/plugin/seedkeeper/task/remove` | POST | 删除种子 |
| `/api/v1/plugin/seedkeeper/transfer/hook` | POST | 转移完成回调 |

## 适用场景

1. **媒体库整理**：使用 MoviePilot 自动整理下载的媒体文件到媒体库
2. **保种需求**：需要长期做种的资源不希望被自动删除
3. **多盘NAS**：文件存储在多个硬盘，需要灵活管理做种任务
4. **PT 刷上传**：需要精细控制做种策略来刷上传量

## 注意事项

- 本插件需要配合正确的下载器配置使用
- 硬链接模式需要源目录和目标目录在同一文件系统
- 删除种子前请确认已设置正确的做种策略
- 建议开启 `PLUGIN_AUTO_RELOAD=true` 环境变量方便调试

## 开发说明

### 项目结构

```
seedkeeper/
├── plugins.v2/
│   └── seedkeeper/
│       ├── __init__.py          # 后端插件代码
│       └── package.v2.json      # 插件索引
├── frontend/                     # Vue 前端项目
│   ├── src/
│   │   ├── components/
│   │   │   ├── Page.vue
│   │   │   ├── Config.vue
│   │   │   └── Dashboard.vue
│   │   └── main.ts
│   ├── vite.config.ts
│   └── package.json
└── README.md
```

### 本地开发

1. Clone MoviePilot 主项目
2. Clone 本插件到 `plugins.v2/seedkeeper/`
3. 启动前后端进行调试
4. 使用 `PLUGIN_AUTO_RELOAD=true` 开启热加载

## License

MIT License
