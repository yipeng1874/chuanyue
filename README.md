时空隧穿器 · SPACETIME TUNNEL ENGINE v9.4
一款基于 Python + Tkinter 的科幻风格倒计时工具。

目录
项目简介
快速开始
功能特性
项目结构
架构说明
核心模块
配色系统
开发指南
开源协议
项目简介
时空隧穿器是一个以"穿越时空"为主题的桌面倒计时应用，使用纯 Python 标准库开发，无需安装任何第三方依赖。界面采用亮色科幻风格，配合粒子动画、步骤文案滚动和穿越完成弹窗，让普通的倒计时变得有趣。

快速开始
环境要求
项目	版本要求
Python	3.8 及以上
操作系统	Windows / macOS / Linux
依赖	仅标准库（tkinter、threading、math、random、time）
运行
# 直接运行（有控制台窗口）
python 穿越器.py

# Windows 无控制台运行
pythonw 穿越器.py
功能特性
功能	说明
自定义时长	支持秒 / 分钟 / 小时 / 天，接受小数输入
实时倒计时	后台线程计时，主线程 UI 刷新，互不阻塞
大字时间显示	Consolas 52pt 加粗，颜色随进度变化（蓝→黄→红）
粒子动画横条	粒子数量随时间递增，越临近结束越"激烈"
进度条	带扫描光效的科幻风格进度条
步骤文案	10 条搞笑穿越步骤均匀分配到倒计时过程中
暂停 / 继续	支持随时暂停并续计
完成弹窗	闪烁特效后弹出穿越目的地确认窗口
输入校验	仅允许有效正数，最长 30 天
项目结构
穿越系统/
├── 穿越器.py      # 主程序（全部逻辑）
├── LICENSE        # MIT 开源协议
└── README.md      # 开发者文档（本文件）
架构说明
CountdownApp
│
├── _build_ui()            ← 构建全部 UI 组件
│
├── 计时线程（daemon）
│   └── _run()             ← 每秒递减 remaining_seconds
│                            通过 root.after(0, ...) 回调主线程
│
├── 动画循环（50ms）
│   └── _animate_bg()      ← 每 50ms 刷新进度条 + 粒子 + 时间显示
│
├── 粒子系统
│   ├── _init_particles()  ← 初始化 30 个粒子
│   └── _update_particles()← 更新位置，越近结束粒子越多（最多 55 个）
│
├── 步骤文案
│   ├── _start_steps()     ← 根据总时长计算间隔
│   └── _schedule_step()   ← 递归 after 调用，依次显示 10 条文案
│
└── 弹窗
    ├── _flash_ring()      ← 完成时闪烁效果（6 次，300ms/次）
    └── _show_arrival_popup() ← 穿越完成弹窗
线程安全说明
计时器运行在独立 daemon 线程中。所有 UI 更新均通过 root.after(0, callback) 派发回 Tkinter 主线程执行，避免跨线程操作 UI 导致的崩溃问题。

核心模块
_draw_ring(ratio)
负责更新时间大字和粒子横条。

参数	说明
ratio	剩余时间比例，范围 [0.0, 1.0]
颜色映射规则：

ratio > 0.5  → ARC_MAIN（蓝色 #3b7bff）
ratio > 0.2  → ARC_MID （黄色 #f59e0b）
ratio ≤ 0.2  → ARC_END （红色 #ef4444）
_draw_bar(pct)
绘制底部科幻进度条。

参数	说明
pct	已消耗百分比，范围 [0, 100]
进度条由三层组成：

棋盘格背景
辉光层（宽 + 浅色）
核心填充层（细 + 饱和色）
扫描光（每帧向右移动 3px）
_update_particles()
粒子从中心点 (120, 120) 向外扩散，超出半径 48px 后重置到中心。

粒子数量公式：

target_count = int(15 + (1 - ratio) * 40)
# ratio=1.0 时约 15 个，ratio=0.0 时约 55 个
_to_seconds(value, unit)
将用户输入转换为秒数。

单位映射：秒×1 / 分钟×60 / 小时×3600 / 天×86400
配色系统
所有颜色在文件顶部集中定义，修改即全局生效：

变量	色值	用途
BG	#f0f4ff	主背景（淡蓝白）
BG2	#e2e8f8	卡片背景
BG3	#ffffff	输入框/进度条背景
ACCENT	#3b7bff	主强调色（蓝）
ACCENT2	#7c3aed	副强调色（紫）
TEXT	#1a1a2e	主文字
TEXT2	#4a5a8a	次要文字
TEXT3	#8898bb	弱文字
BORDER	#c3d0f0	边框
ARC_MAIN	#3b7bff	进度 > 50% 颜色
ARC_MID	#f59e0b	进度 50%~80% 颜色
ARC_END	#ef4444	进度 > 80% 颜色
开发指南
修改步骤文案
编辑 CountdownApp.__init__ 中的 self._steps 列表，添加或替换任意条目：

self._steps = [
    "🔍  AI 定位四维坐标...",
    # ... 添加你的文案
]
调整窗口大小
修改 _build_ui 中的 geometry：

self.root.geometry("520x520")  # 宽×高，单位 px
修改最大穿越时长
if secs > 86400 * 30:   # 改为你需要的上限（秒）
切换为深色主题
将顶部色板中的 BG、BG2、BG3 改为深色值，TEXT 改为浅色值即可。

开源协议
本项目基于 MIT License 开源，详见 LICENSE。

免责声明：本工具不对任何真实时空穿越失败负责。量子隧穿成功率 100%（仅限界面动画）。
