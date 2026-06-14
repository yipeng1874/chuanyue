import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import math
import random

# ── 亮色主题色板 ──────────────────────────────────────────
BG         = "#f0f4ff"   # 主背景（淡蓝白）
BG2        = "#e2e8f8"   # 卡片背景
BG3        = "#ffffff"   # 输入框/进度条背景
ACCENT     = "#3b7bff"   # 主强调色（蓝）
ACCENT2    = "#7c3aed"   # 副强调色（紫）
TEXT       = "#1a1a2e"   # 主文字
TEXT2      = "#4a5a8a"   # 次要文字
TEXT3      = "#8898bb"   # 弱文字
BORDER     = "#c3d0f0"   # 边框
ARC_MAIN   = "#3b7bff"   # 圆弧主色
ARC_MID    = "#f59e0b"   # 圆弧中段
ARC_END    = "#ef4444"   # 圆弧末段
GLOW_MAIN  = "#bfd3ff"
GLOW_MID   = "#fde68a"
GLOW_END   = "#fecaca"
BTN_START  = "#3b7bff"
BTN_START_FG = "#ffffff"
BTN_PAUSE  = "#e2e8f8"
BTN_PAUSE_FG = "#4a5a8a"
BTN_RESET  = "#f1f5ff"
BTN_RESET_FG = "#6b7daa"
POPUP_BG   = "#f8faff"


class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("时空隧穿器 · SPACETIME TUNNEL ENGINE")
        self.root.geometry("520x520")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.total_seconds = 0
        self.remaining_seconds = 0
        self.running = False
        self.paused = False
        self.timer_thread = None
        self._anim_angle = 0
        self._anim_id = None
        self._scan_offset = 0

        # 粒子列表 [(x, y, dx, dy, size, color)]
        self._particles = []
        self._step_index = 0
        self._step_job = None

        # 穿越步骤文案
        self._steps = [
            "🔍  AI 定位四维坐标...",
            "⚛️   锁定纠缠量子对...",
            "🌀  疏通时空隧道...",
            "🧲  校准普朗克常数...",
            "📡  与未来建立握手连接...",
            "⚡  压缩时间维度...",
            "🛸  加载目标时间戳...",
            "🔐  绕过时间悖论检测...",
            "🌌  折叠空间曲率...",
            "🚀  穿越通道稳定，准备发射！",
        ]

        # 保存用户输入（用于结束弹窗）
        self._travel_value = 0
        self._travel_unit = "秒"

        self._build_ui()
        self._animate_bg()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self):
        # 顶部装饰画布
        self.deco_canvas = tk.Canvas(self.root, width=520, height=40,
                                     bg=BG, highlightthickness=0)
        self.deco_canvas.pack()
        self._draw_deco()

        # 标题
        title_frame = tk.Frame(self.root, bg=BG)
        title_frame.pack(pady=(0, 2))
        tk.Label(title_frame, text="◈", font=("Consolas", 16),
                 bg=BG, fg=ACCENT).pack(side="left", padx=(0, 6))
        tk.Label(title_frame, text="时 空 隧 穿 器",
                 font=("Consolas", 14, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(title_frame, text="◈", font=("Consolas", 16),
                 bg=BG, fg=ACCENT).pack(side="left", padx=(6, 0))

        # 副标题
        tk.Label(self.root, text="─── SPACETIME TUNNEL ENGINE v9.4 ───",
                 font=("Consolas", 9), bg=BG, fg=TEXT3).pack()

        # 输入卡片
        card = tk.Frame(self.root, bg=BG2, relief="flat",
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(padx=36, pady=6, fill="x")

        inner = tk.Frame(card, bg=BG2, padx=16, pady=14)
        inner.pack(fill="x")

        tk.Label(inner, text="输入穿越时长", font=("Consolas", 9),
                 bg=BG2, fg=ACCENT).grid(row=0, column=0, sticky="w")
        tk.Label(inner, text="穿越单位", font=("Consolas", 9),
                 bg=BG2, fg=ACCENT).grid(row=0, column=2, sticky="w", padx=(30, 0))

        self.value_var = tk.StringVar()
        vcmd = (self.root.register(self._validate_input), "%P")
        entry = tk.Entry(inner, textvariable=self.value_var,
                         font=("Consolas", 22, "bold"), width=9,
                         bg=BG3, fg=TEXT,
                         insertbackground=ACCENT,
                         relief="flat", bd=0, justify="center",
                         validate="key", validatecommand=vcmd,
                         highlightthickness=1,
                         highlightbackground=BORDER,
                         highlightcolor=ACCENT)
        entry.grid(row=1, column=0, columnspan=2, pady=(4, 0))
        entry.focus()

        # 下拉框
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Sci.TCombobox",
                         fieldbackground=BG3,
                         background=BG3,
                         foreground=TEXT,
                         selectbackground=BG3,
                         selectforeground=TEXT,
                         bordercolor=BORDER,
                         arrowcolor=ACCENT,
                         font=("Consolas", 14, "bold"))
        style.map("Sci.TCombobox",
                  fieldbackground=[("readonly", BG3)],
                  foreground=[("readonly", TEXT)],
                  selectbackground=[("readonly", BG3)])

        self.unit_var = tk.StringVar(value="秒")
        self.unit_combo = ttk.Combobox(inner, textvariable=self.unit_var,
                                        values=["秒", "分钟", "小时", "天"],
                                        state="readonly", width=5,
                                        font=("Consolas", 14, "bold"),
                                        style="Sci.TCombobox",
                                        justify="center")
        self.unit_combo.grid(row=1, column=2, padx=(30, 0), pady=(4, 0), sticky="ew")

        # 大字时间显示区域
        time_frame = tk.Frame(self.root, bg=BG2,
                              highlightbackground=BORDER, highlightthickness=1)
        time_frame.pack(padx=36, pady=(8, 2), fill="x")

        self.time_label = tk.Label(time_frame, text="00:00:00",
                                   font=("Consolas", 52, "bold"),
                                   bg=BG2, fg=ACCENT)
        self.time_label.pack(pady=(12, 4))

        self.pct_ring_label = tk.Label(time_frame, text="100.0%",
                                       font=("Consolas", 16, "bold"),
                                       bg=BG2, fg=TEXT2)
        self.pct_ring_label.pack(pady=(0, 10))

        # 粒子画布（扁平，横向，紧贴时间框下方）
        self.ring_canvas = tk.Canvas(self.root, width=448, height=10,
                                     bg=BG, highlightthickness=0)
        self.ring_canvas.pack()

        # 状态文字
        self.status_label = tk.Label(self.root, text="🛸  隧穿器待机中...",
                                     font=("Consolas", 10),
                                     bg=BG, fg=TEXT3)
        self.status_label.pack(pady=(1, 4))

        # 进度条区域
        bar_frame = tk.Frame(self.root, bg=BG)
        bar_frame.pack(padx=36, fill="x")

        self.bar_canvas = tk.Canvas(bar_frame, width=448, height=20,
                                    bg=BG3, highlightthickness=1,
                                    highlightbackground=BORDER)
        self.bar_canvas.pack(fill="x")

        self.pct_label = tk.Label(self.root, text="穿越进度  0.0%",
                                  font=("Consolas", 9),
                                  bg=BG, fg=TEXT3)
        self.pct_label.pack(pady=(2, 2))

        # 按钮
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=6)

        self.start_btn = self._sci_button(btn_frame, "🚀  开始穿越",
                                           BTN_START, BTN_START_FG, self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.pause_btn = self._sci_button(btn_frame, "⏸  暂停穿越",
                                           BTN_PAUSE, BTN_PAUSE_FG, self.pause_timer)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.pause_btn.config(state="disabled")

        self.reset_btn = self._sci_button(btn_frame, "↺  终止穿越",
                                           BTN_RESET, BTN_RESET_FG, self.reset_timer)
        self.reset_btn.grid(row=0, column=2, padx=10)

        # 底部装饰
        tk.Label(self.root, text="◄◄◄  量子纠缠引擎 · 在线  ►►►",
                 font=("Consolas", 8), bg=BG, fg=TEXT3).pack(pady=(6, 0))

    def _sci_button(self, parent, text, bg, fg, cmd):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=("Consolas", 11, "bold"),
                        bg=bg, fg=fg,
                        activebackground=ACCENT,
                        activeforeground="#ffffff",
                        relief="flat", bd=0, padx=14, pady=8,
                        cursor="hand2",
                        highlightthickness=1,
                        highlightbackground=BORDER,
                        highlightcolor=ACCENT)
        return btn

    def _validate_input(self, val):
        if val == "":
            return True
        try:
            float(val)
            return True
        except ValueError:
            return False

    # ── 装饰绘制 ───────────────────────────────────────────

    def _draw_deco(self):
        c = self.deco_canvas
        c.delete("all")
        w = 520
        for y in [6, 10, 14]:
            c.create_line(0, y, w, y, fill=BORDER, width=1)
        c.create_line(0, 18, w, 18, fill=ACCENT, width=1)
        for x, flip in [(0, False), (w, True)]:
            ox = x if not flip else x - 28
            c.create_line(ox, 18, ox + (28 if not flip else -28), 18, fill=ACCENT, width=2)
            c.create_line(ox + (28 if not flip else -28), 18,
                          ox + (28 if not flip else -28), 36, fill=ACCENT, width=2)
        for dx in [100, 200, 300, 420]:
            c.create_polygon(dx, 22, dx+5, 28, dx, 34, dx-5, 28,
                             fill=BORDER, outline=ACCENT, width=1)

    def _draw_ring(self, ratio, scanning=False):
        """不再绘制圆环，改为更新大字 Label 和粒子横条"""
        # 颜色
        if ratio > 0.5:
            arc_color = ARC_MAIN
        elif ratio > 0.2:
            arc_color = ARC_MID
        else:
            arc_color = ARC_END

        # 更新时间文字
        text = self._format_time(self.remaining_seconds) if self.total_seconds > 0 else "00:00:00"
        pct = (1 - self.remaining_seconds / self.total_seconds) * 100 if self.total_seconds > 0 else 0
        self.time_label.config(text=text, fg=arc_color if self.total_seconds > 0 else TEXT3)
        self.pct_ring_label.config(text=f"{100 - pct:.1f}%", fg=arc_color if self.total_seconds > 0 else TEXT3)

        # 粒子横条（10px 高度，随机散点）
        c = self.ring_canvas
        c.delete("all")
        if self.running and self._particles:
            W = 448
            for px, py, pdx, pdy, psize, pcol in self._particles:
                # 将粒子 x 映射到横条宽度，y 映射到 0-10
                bx = int(px / 240 * W)
                by = int(py / 240 * 10)
                bx = max(0, min(W - 1, bx))
                by = max(0, min(9, by))
                sz = max(1, int(psize * 0.8))
                c.create_oval(bx - sz, by - sz, bx + sz, by + sz, fill=pcol, outline="")

    def _draw_bar(self, pct):
        c = self.bar_canvas
        c.delete("all")
        W, H = 448, 20
        filled = int(W * pct / 100)

        # 背景格子
        for x in range(0, W, 8):
            shade = "#edf1fc" if (x // 8) % 2 == 0 else BG3
            c.create_rectangle(x, 0, x+8, H, fill=shade, outline="")

        if filled > 0:
            if pct < 50:
                color = ARC_MAIN
                glow = GLOW_MAIN
            elif pct < 80:
                color = ARC_MID
                glow = GLOW_MID
            else:
                color = ARC_END
                glow = GLOW_END

            c.create_rectangle(0, 4, filled, H-4, fill=glow, outline="")
            c.create_rectangle(0, 6, filled, H-6, fill=color, outline="")

            # 扫描光
            sx = (self._scan_offset % filled) if filled > 10 else 0
            if sx < filled:
                for i in range(12):
                    alpha_x = sx - i
                    if 0 <= alpha_x < filled:
                        shade_val = int(200 * (1 - i / 12))
                        sc = f"#{min(shade_val+55,255):02x}{min(shade_val+55,255):02x}{255:02x}"
                        c.create_line(alpha_x, 5, alpha_x, H-5, fill=sc, width=1)

        c.create_line(0, 0, filled, 0, fill=ACCENT if pct > 0 else BORDER, width=1)

    # ── 粒子系统 ────────────────────────────────────────────

    def _init_particles(self):
        self._particles = []
        cx, cy = 120, 120
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.5)
            size = random.uniform(1.5, 3.5)
            self._particles.append([
                cx, cy,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                size,
                ACCENT
            ])

    def _update_particles(self):
        cx, cy, max_r = 120, 120, 48
        ratio = self.remaining_seconds / self.total_seconds if self.total_seconds > 0 else 1

        if ratio > 0.5:
            colors = ["#3b7bff", "#6ea3ff", "#93bfff", "#2563eb"]
        elif ratio > 0.2:
            colors = ["#f59e0b", "#fbbf24", "#fcd34d", "#d97706"]
        else:
            colors = ["#ef4444", "#f87171", "#fca5a5", "#dc2626"]

        target_count = int(15 + (1 - ratio) * 40)
        while len(self._particles) < target_count:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.5)
            size = random.uniform(1.5, 3.5)
            self._particles.append([cx, cy, math.cos(angle) * speed, math.sin(angle) * speed, size,
                                     random.choice(colors)])

        new_particles = []
        for p in self._particles:
            p[0] += p[2]
            p[1] += p[3]
            dist = math.sqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2)
            if dist < max_r:
                p[5] = random.choice(colors)
                new_particles.append(p)
            else:
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.5, 2.5)
                size = random.uniform(1.5, 3.5)
                new_particles.append([cx, cy, math.cos(angle) * speed, math.sin(angle) * speed, size,
                                      random.choice(colors)])
        self._particles = new_particles

    # ── 动画循环 ───────────────────────────────────────────

    def _animate_bg(self):
        if self.running:
            self._scan_offset += 3
            pct = (1 - self.remaining_seconds / self.total_seconds) * 100 if self.total_seconds > 0 else 0
            self._draw_bar(pct)
            self._update_particles()
            ratio = self.remaining_seconds / self.total_seconds if self.total_seconds > 0 else 0
            self._draw_ring(ratio)
        self.root.after(50, self._animate_bg)

    # ── 搞笑步骤文案 ──────────────────────────────────────

    def _start_steps(self):
        self._step_index = 0
        total = self.total_seconds
        if total <= 0:
            return
        interval_ms = max(int(total * 1000 / len(self._steps)), 800)
        self._schedule_step(interval_ms)

    def _schedule_step(self, interval_ms):
        if not self.running:
            return
        if self._step_index < len(self._steps):
            self.status_label.config(
                text=self._steps[self._step_index],
                fg=ACCENT
            )
            self._step_index += 1
            self._step_job = self.root.after(interval_ms, lambda: self._schedule_step(interval_ms))

    def _cancel_steps(self):
        if self._step_job:
            self.root.after_cancel(self._step_job)
            self._step_job = None

    # ── 工具 ───────────────────────────────────────────────

    def _to_seconds(self, value, unit):
        return int(value * {"秒": 1, "分钟": 60, "小时": 3600, "天": 86400}[unit])

    def _format_time(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _format_travel_result(self, value, unit):
        if value == int(value):
            val_str = str(int(value))
        else:
            val_str = str(value)
        return f"{val_str} {unit}后"

    def _update_display(self):
        ratio = self.remaining_seconds / self.total_seconds if self.total_seconds > 0 else 0
        self._draw_ring(ratio)
        pct = (1 - ratio) * 100
        self._draw_bar(pct)
        self.pct_label.config(text=f"穿越进度  {pct:.1f}%")

    # ── 控制 ───────────────────────────────────────────────

    def start_timer(self):
        if self.paused:
            self.paused = False
            self.running = True
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal", text="⏸  暂停穿越")
            self.status_label.config(text="🌀  正在穿越时空...", fg=ACCENT)
            self._start_steps()
            self.timer_thread = threading.Thread(target=self._run, daemon=True)
            self.timer_thread.start()
            return

        raw = self.value_var.get().strip()
        if not raw:
            messagebox.showwarning("输入错误", "请输入穿越时长！")
            return
        try:
            val = float(raw)
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效正数！")
            return

        secs = self._to_seconds(val, self.unit_var.get())
        if secs > 86400 * 30:
            messagebox.showwarning("范围错误", "时空隧穿器最大支持30天穿越！")
            return

        self._travel_value = val
        self._travel_unit = self.unit_var.get()

        self.total_seconds = secs
        self.remaining_seconds = secs
        self.running = True
        self.paused = False
        self._init_particles()
        self._update_display()
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal", text="⏸  暂停穿越")
        self.status_label.config(text="🌀  正在穿越时空...", fg=ACCENT)
        self._start_steps()

        self.timer_thread = threading.Thread(target=self._run, daemon=True)
        self.timer_thread.start()

    def pause_timer(self):
        if self.running:
            self.running = False
            self.paused = True
            self._cancel_steps()
            self.pause_btn.config(text="▶  继续穿越")
            self.start_btn.config(state="normal", text="▶  继续穿越")
            self.status_label.config(text="⚠️  穿越暂停！请勿随意停止！", fg=ARC_MID)
        elif self.paused:
            self.start_timer()

    def reset_timer(self):
        self.running = False
        self.paused = False
        self._cancel_steps()
        self._particles = []
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.time_label.config(text="00:00:00", fg=ACCENT)
        self.pct_ring_label.config(text="100.0%", fg=TEXT2)
        self._draw_ring(1.0)
        self._draw_bar(0)
        self.pct_label.config(text="穿越进度  0.0%")
        self.status_label.config(text="🛸  隧穿器待机中...", fg=TEXT3)
        self.start_btn.config(state="normal", text="🚀  开始穿越")
        self.pause_btn.config(state="disabled", text="⏸  暂停穿越")
        self.value_var.set("")

    def _run(self):
        while self.running and self.remaining_seconds > 0:
            time.sleep(1)
            if self.running:
                self.remaining_seconds -= 1
                self.root.after(0, self._update_display)
        if self.running and self.remaining_seconds == 0:
            self.root.after(0, self._on_finish)

    def _on_finish(self):
        self.running = False
        self._cancel_steps()
        self._particles = []
        self._draw_ring(0)
        self._draw_bar(100)
        self.pct_label.config(text="穿越进度  100.0%")
        self.status_label.config(text="✅  穿越成功！欢迎来到未来", fg=ARC_END)
        self.start_btn.config(state="normal", text="🚀  开始穿越")
        self.pause_btn.config(state="disabled", text="⏸  暂停穿越")
        self._flash_ring(6)
        self.root.after(1800, self._show_arrival_popup)

    def _show_arrival_popup(self):
        travel_str = self._format_travel_result(self._travel_value, self._travel_unit)

        popup = tk.Toplevel(self.root)
        popup.title("⚡ 穿越成功")
        popup.geometry("420x320")
        popup.resizable(False, False)
        popup.configure(bg=POPUP_BG)
        popup.grab_set()

        popup.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width() - 420) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - 320) // 2
        popup.geometry(f"420x320+{rx}+{ry}")

        border = tk.Frame(popup, bg=ACCENT, padx=2, pady=2)
        border.pack(fill="both", expand=True, padx=10, pady=10)

        inner = tk.Frame(border, bg=POPUP_BG)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="⚡  穿 越 成 功  ⚡",
                 font=("Consolas", 16, "bold"),
                 bg=POPUP_BG, fg=ACCENT).pack(pady=(18, 6))

        tk.Label(inner, text="─────────────────────────",
                 font=("Consolas", 9), bg=POPUP_BG, fg=BORDER).pack()

        tk.Label(inner, text="恭喜！你已成功穿越至",
                 font=("Consolas", 11),
                 bg=POPUP_BG, fg=TEXT2).pack(pady=(12, 4))

        tk.Label(inner, text=f"[ {travel_str} ]",
                 font=("Consolas", 20, "bold"),
                 bg=POPUP_BG, fg=ACCENT).pack(pady=(0, 10))

        tk.Label(inner, text="欢迎来到未来，请注意不要改变历史！",
                 font=("Consolas", 9),
                 bg=POPUP_BG, fg=TEXT3).pack()

        tk.Label(inner, text="─────────────────────────",
                 font=("Consolas", 9), bg=POPUP_BG, fg=BORDER).pack(pady=(6, 0))

        confirm_btn = tk.Button(inner, text="✓  确认穿越",
                                command=popup.destroy,
                                font=("Consolas", 12, "bold"),
                                bg=ACCENT, fg="#ffffff",
                                activebackground=ACCENT2,
                                activeforeground="#ffffff",
                                relief="flat", bd=0, padx=20, pady=8,
                                cursor="hand2")
        confirm_btn.pack(pady=14)

    def _flash_ring(self, n):
        if n <= 0:
            self.time_label.config(text="00:00:00", fg=ARC_END)
            self.pct_ring_label.config(text="穿越完成！", fg=ARC_MID)
            return
        col = ARC_END if n % 2 == 0 else ACCENT
        self.time_label.config(text="00:00:00", fg=col)
        self.pct_ring_label.config(text="穿越完成！", fg=ARC_MID)
        self.root.after(300, lambda: self._flash_ring(n - 1))


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()
