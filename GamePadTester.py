# -*- coding: utf-8 -*-
# GamePadTester
# Version: 1.5.1
"""
XInput 기반 게임 컨트롤러 테스터 (프리미엄 UI/UX 리디자인)
- v23: 컨트롤러 연결상태 실시간 반영, 측정 버튼 연동, 순서 문제 설명 및 UI 개선
- 기능은 원본 코드를 계승, UI/UX 및 코드 구조를 완전히 재설계
- 다크 테마 기반의 현대적이고 직관적인 시각화에 중점
- 의존성: PySide6
"""
from __future__ import annotations
import sys
import os
import time
import threading
import math
import base64
from collections import deque
from statistics import mean, median, stdev
from typing import Deque, List, Optional, Tuple
from datetime import datetime

# ----- 버전 정보 -----
VERSION = "1.5.1"

# ----- Qt (PySide6) -----
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer, QPointF, QRectF, QSize
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QIcon, QPixmap, QPainterPath, QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QFileDialog, QFrame, QSlider, QSizePolicy, QCheckBox, QMessageBox
)

# ----- Windows API (ctypes) -----
import ctypes
from ctypes import wintypes

# (XInput 관련 클래스 및 상수 정의는 이전과 동일)
_XINPUT_DLLS = ["xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"]
class XINPUT_GAMEPAD(ctypes.Structure): _fields_ = [("wButtons", wintypes.WORD),("bLeftTrigger", ctypes.c_ubyte),("bRightTrigger", ctypes.c_ubyte),("sThumbLX", ctypes.c_short),("sThumbLY", ctypes.c_short),("sThumbRX", ctypes.c_short),("sThumbRY", ctypes.c_short),]
class XINPUT_STATE(ctypes.Structure): _fields_ = [("dwPacketNumber", wintypes.DWORD),("Gamepad", XINPUT_GAMEPAD),]
class XINPUT_VIBRATION(ctypes.Structure): _fields_ = [("wLeftMotorSpeed", wintypes.WORD),("wRightMotorSpeed", wintypes.WORD),]
class XINPUT_CAPABILITIES(ctypes.Structure): _fields_ = [("Type", ctypes.c_ubyte),("SubType", ctypes.c_ubyte),("Flags", ctypes.c_ushort),("Gamepad", XINPUT_GAMEPAD),("Vibration", XINPUT_VIBRATION),]
XINPUT_GAMEPAD_DPAD_UP, XINPUT_GAMEPAD_DPAD_DOWN, XINPUT_GAMEPAD_DPAD_LEFT, XINPUT_GAMEPAD_DPAD_RIGHT, XINPUT_GAMEPAD_START, XINPUT_GAMEPAD_BACK, XINPUT_GAMEPAD_LEFT_THUMB, XINPUT_GAMEPAD_RIGHT_THUMB, XINPUT_GAMEPAD_LEFT_SHOULDER, XINPUT_GAMEPAD_RIGHT_SHOULDER, XINPUT_GAMEPAD_A, XINPUT_GAMEPAD_B, XINPUT_GAMEPAD_X, XINPUT_GAMEPAD_Y = 0x0001,0x0002,0x0004,0x0008,0x0010,0x0020,0x0040,0x0080,0x0100,0x0200,0x1000,0x2000,0x4000,0x8000
XINPUT_DEVSUBTYPE_GAMEPAD, XINPUT_DEVSUBTYPE_WHEEL, XINPUT_DEVSUBTYPE_ARCADE_STICK = 0x01, 0x02, 0x03
_SUBTYPE_NAME = {XINPUT_DEVSUBTYPE_GAMEPAD: "Gamepad", XINPUT_DEVSUBTYPE_WHEEL: "Wheel", XINPUT_DEVSUBTYPE_ARCADE_STICK: "Arcade Stick"}
ERROR_SUCCESS, ERROR_DEVICE_NOT_CONNECTED = 0, 1167

class XInput:
    def __init__(self) -> None:
        self.lib = None; last_err: Optional[Exception] = None
        for name in _XINPUT_DLLS:
            try: self.lib = ctypes.WinDLL(name); break
            except OSError as e: last_err = e; continue
        if self.lib is None: raise OSError(f"XInput DLL을 찾을 수 없습니다: {_XINPUT_DLLS} / 마지막 오류: {last_err}")
        self.XInputGetState = self.lib.XInputGetState; self.XInputGetState.argtypes = [wintypes.DWORD, ctypes.POINTER(XINPUT_STATE)]; self.XInputGetState.restype = wintypes.DWORD
        try: self.XInputSetState = self.lib.XInputSetState; self.XInputSetState.argtypes = [wintypes.DWORD, ctypes.POINTER(XINPUT_VIBRATION)]; self.XInputSetState.restype = wintypes.DWORD
        except AttributeError: self.XInputSetState = None
        try: self.XInputGetCapabilities = self.lib.XInputGetCapabilities; self.XInputGetCapabilities.argtypes = [wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(XINPUT_CAPABILITIES)]; self.XInputGetCapabilities.restype = wintypes.DWORD
        except AttributeError: self.XInputGetCapabilities = None
    def get_state(self, idx: int) -> Tuple[int, XINPUT_STATE]:
        state = XINPUT_STATE(); res = self.XInputGetState(idx, ctypes.byref(state)); return int(res), state
    def set_vibration(self, idx: int, left: int, right: int) -> bool:
        if not self.XInputSetState: return False
        vib = XINPUT_VIBRATION(int(max(0, min(65535, left))), int(max(0, min(65535, right)))); res = self.XInputSetState(idx, ctypes.byref(vib)); return res == ERROR_SUCCESS
    def get_capabilities(self, idx: int) -> Optional[XINPUT_CAPABILITIES]:
        if not self.XInputGetCapabilities: return None
        caps = XINPUT_CAPABILITIES(); res = self.XInputGetCapabilities(idx, 0, ctypes.byref(caps))
        if res == ERROR_SUCCESS: return caps
        return None

def get_gamepad_names_from_pygame() -> dict[int, str]:
    names = {}
    try:
        import pygame
        pygame.init()
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            names[i] = pygame.joystick.Joystick(i).get_name()
        pygame.joystick.quit()
        pygame.quit()
    except Exception as e:
        print(f"Pygame으로 장치명 로딩 실패: {e}")
    return names

def percentile(sorted_list: List[float], p: float) -> float:
    if not sorted_list: return float('nan')
    k = (len(sorted_list) - 1) * (p / 100.0); f = int(k); c = min(f + 1, len(sorted_list) - 1)
    if f == c: return sorted_list[f]
    d0 = sorted_list[f] * (c - k); d1 = sorted_list[c] * (k - f); return d0 + d1

class PollingThread(QThread):
    statsUpdated = Signal(dict)
    deviceError = Signal(str)
    def __init__(self, device_index: int, window_samples: int = 1000, include_gyro: bool = False):
        super().__init__()
        self.device_index = device_index; self.window_samples = max(20, int(window_samples)); self.include_gyro = include_gyro; self._stop = threading.Event(); self.xi = XInput(); self._lock = threading.Lock(); self._intervals_ns: Deque[int] = deque(maxlen=self.window_samples); self._all_intervals_ns: List[int] = []; self._last_state = XINPUT_STATE(); self._last_change_ts_ns: Optional[int] = None
    def set_include_gyro(self, include: bool): self.include_gyro = include
    def snapshot_intervals_ns(self) -> List[int]:
        with self._lock: return list(self._all_intervals_ns)
    def stop(self): self._stop.set()
    def run(self):
        res, self._last_state = self.xi.get_state(self.device_index)
        if res != ERROR_SUCCESS: self.deviceError.emit("XInput 장치를 찾을 수 없습니다."); return
        self._last_change_ts_ns = time.perf_counter_ns(); last_report_time_ns = time.perf_counter_ns()
        while not self._stop.is_set():
            res, current_state = self.xi.get_state(self.device_index)
            if res != ERROR_SUCCESS: self.deviceError.emit("장치 연결 끊어짐"); break
            now_ns = time.perf_counter_ns()
            if current_state.dwPacketNumber != self._last_state.dwPacketNumber:
                gamepad_changed = (ctypes.string_at(ctypes.byref(current_state.Gamepad), ctypes.sizeof(XINPUT_GAMEPAD)) != ctypes.string_at(ctypes.byref(self._last_state.Gamepad), ctypes.sizeof(XINPUT_GAMEPAD)))
                if self.include_gyro or gamepad_changed:
                    dt = now_ns - self._last_change_ts_ns
                    if dt > 1000:
                        with self._lock: self._intervals_ns.append(dt); self._all_intervals_ns.append(dt)
                    self._last_change_ts_ns = now_ns
                self._last_state = current_state
            if now_ns - last_report_time_ns >= 50_000_000:
                last_report_time_ns = now_ns
                with self._lock: intervals = list(self._intervals_ns)
                self.statsUpdated.emit(self._compute_stats(intervals))
            time.sleep(0.0001)
    def _compute_stats(self, intervals_ns: List[int]) -> dict:
        if len(intervals_ns) < 10: return {"samples": len(intervals_ns)}
        ms = [x / 1_000_000.0 for x in intervals_ns]
        mu = mean(ms)
        if len(ms) > 1:
            sigma = stdev(ms); low, high = mu - 2 * sigma, mu + 2 * sigma
            stability = (sum(1 for v in ms if low <= v <= high) / len(ms)) * 100.0
        else: stability = 100.0
        return {"samples": len(ms), "mean_ms": mu, "median_ms": median(ms), "mean_hz": 1000.0/mu if mu > 0 else 0, "median_hz": 1000.0/median(ms) if median(ms) > 0 else 0, "stability_pct": stability}

STYLESHEET = """
QWidget { color: #e0e0e0; font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; font-size: 10pt; }
MainWindow { background-color: #282c34; }
QGroupBox { font-size: 11pt; font-weight: bold; border: 1px solid #404552; border-radius: 8px; margin-top: 10px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 10px; color: #9299b1; }
QLabel#TitleLabel { font-size: 16pt; font-weight: bold; color: #ffffff; }
QLabel#StatusLabel, QLabel#DeviceListLabel { font-size: 9pt; color: #9299b1; }
QLabel#AxisValueLabel { font-size: 11pt; font-weight: bold; color: #ffffff; }
QLabel#AxisTitleLabel { font-size: 8pt; color: #9299b1; }
QPushButton { background-color: #404552; border: 1px solid #525968; border-radius: 6px; padding: 8px 12px; font-weight: bold; min-width: 80px; }
QPushButton:hover { background-color: #525968; }
QPushButton:pressed { background-color: #3a3f4a; }
QPushButton:disabled { background-color: #3a3f4a; color: #8a8a8a; }
QPushButton#StartButton { background-color: #528bff; color: white; }
QPushButton#StartButton:hover { background-color: #679eff; }
QPushButton#StopButton { background-color: #ff5252; color: white; }
QPushButton#StopButton:hover { background-color: #ff6d6d; }
QComboBox, QCheckBox { background-color: #3a3f4a; border: 1px solid #525968; border-radius: 4px; padding: 6px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QComboBox::drop-down { border: none; }
QSlider::groove:horizontal { height: 4px; background: #3a3f4a; border-radius: 2px; }
QSlider::handle:horizontal { width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; background: #528bff; }
"""

class StatWidget(QWidget):
    def __init__(self, title: str, unit: str):
        super().__init__(); self.title_label = QLabel(title); self.value_label = QLabel("-"); self.unit_label = QLabel(unit)
        self.title_label.setStyleSheet("color: #9299b1; font-size: 9pt;"); self.value_label.setStyleSheet("color: white; font-size: 18pt; font-weight: bold;"); self.unit_label.setStyleSheet("color: #9299b1; font-size: 12pt; margin-bottom: 2px;")
        layout = QHBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.addWidget(self.title_label, 1, Qt.AlignBottom); layout.addSpacing(10); layout.addWidget(self.value_label, 0, Qt.AlignBottom | Qt.AlignRight); layout.addSpacing(5); layout.addWidget(self.unit_label, 0, Qt.AlignBottom | Qt.AlignLeft)
    def set_value(self, value: Optional[float], fmt: str = "{:.2f}"): self.value_label.setText(fmt.format(value) if value is not None else "-")

class AnalogStickWidget(QWidget):
    def __init__(self):
        super().__init__(); self.x, self.y = 0.0, 0.0; self.is_pressed = False; self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); self.setMinimumSize(100, 100)
    def set_pos(self, x: float, y: float): self.x, self.y = x, -y; self.update()
    def set_pressed(self, pressed: bool):
        if self.is_pressed != pressed: self.is_pressed = pressed; self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing); size = min(self.width(), self.height()); center = QPointF(self.width() / 2, self.height() / 2); radius = size / 2 * 0.9
        border_color = QColor("#528bff") if self.is_pressed else QColor("#525968"); painter.setPen(QPen(border_color, 4)); painter.setBrush(Qt.NoBrush); painter.drawEllipse(center, radius, radius)
        handle_pos = QPointF(center.x() + self.x * radius * 0.7, center.y() + self.y * radius * 0.7); painter.setBrush(QColor("#e0e0e0")); painter.setPen(Qt.NoPen); painter.drawEllipse(handle_pos, radius * 0.4, radius * 0.4)

class TriggerWidget(QWidget):
    def __init__(self, title: str):
        super().__init__(); self.title = title; self.value = 0.0; self.setMinimumHeight(120)
    def set_value(self, value: float): self.value = value; self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing); rect = self.rect().adjusted(5, 20, -5, -5)
        painter.setPen(Qt.NoPen); painter.setBrush(QColor("#3a3f4a")); painter.drawRoundedRect(rect, 5, 5)
        fill_height = rect.height() * self.value; fill_rect = QRectF(rect.x(), rect.y() + rect.height() - fill_height, rect.width(), fill_height); painter.setBrush(QColor("#528bff")); painter.drawRoundedRect(fill_rect, 5, 5)
        painter.setPen(QColor("#e0e0e0")); painter.drawText(self.rect(), Qt.AlignHCenter | Qt.AlignTop, self.title)

class GamepadWidget(QWidget):
    def __init__(self):
        super().__init__(); self.button_states = {}; self.stick_L = AnalogStickWidget(); self.stick_R = AnalogStickWidget(); self.trigger_L = TriggerWidget("LT"); self.trigger_R = TriggerWidget("RT")
        layout = QGridLayout(self); layout.setColumnStretch(2, 1); layout.setRowStretch(1, 1); layout.addWidget(self.trigger_L, 0, 0, 1, 2); layout.addWidget(self.trigger_R, 0, 3, 1, 2); layout.addWidget(self.stick_L, 2, 0, 1, 2); layout.addWidget(self.stick_R, 2, 3, 1, 2)
    def update_state(self, gp_state: XINPUT_GAMEPAD):
        self.button_states = {"DPAD_UP": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_UP),"DPAD_DOWN": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_DOWN),"DPAD_LEFT": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_LEFT),"DPAD_RIGHT": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_RIGHT),"START": bool(gp_state.wButtons & XINPUT_GAMEPAD_START),"BACK": bool(gp_state.wButtons & XINPUT_GAMEPAD_BACK),"LTHUMB": bool(gp_state.wButtons & XINPUT_GAMEPAD_LEFT_THUMB),"RTHUMB": bool(gp_state.wButtons & XINPUT_GAMEPAD_RIGHT_THUMB),"LB": bool(gp_state.wButtons & XINPUT_GAMEPAD_LEFT_SHOULDER),"RB": bool(gp_state.wButtons & XINPUT_GAMEPAD_RIGHT_SHOULDER),"A": bool(gp_state.wButtons & XINPUT_GAMEPAD_A),"B": bool(gp_state.wButtons & XINPUT_GAMEPAD_B),"X": bool(gp_state.wButtons & XINPUT_GAMEPAD_X),"Y": bool(gp_state.wButtons & XINPUT_GAMEPAD_Y),}
        self.stick_L.set_pos(gp_state.sThumbLX / 32767.0, gp_state.sThumbLY / 32767.0); self.stick_R.set_pos(gp_state.sThumbRX / 32767.0, gp_state.sThumbRY / 32767.0)
        self.stick_L.set_pressed(self.button_states.get("LTHUMB", False)); self.stick_R.set_pressed(self.button_states.get("RTHUMB", False))
        self.trigger_L.set_value(gp_state.bLeftTrigger / 255.0); self.trigger_R.set_value(gp_state.bRightTrigger / 255.0); self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing); c, w, h = self.rect().center(), self.width(), self.height()
        C_OUTLINE = QColor(82, 139, 255, 60); C_BG = QColor("#2c313a"); C_BTN_OFF = QColor("#404552"); C_BTN_ON = QColor("#528bff"); C_TEXT = QColor("#e0e0e0")
        path = QPainterPath(); path.moveTo(w*0.3, h*0.05); path.cubicTo(w*0.1, h*0.05, w*0.05, h*0.3, w*0.05, h*0.5); path.cubicTo(w*0.05, h*0.8, w*0.2, h*0.95, w*0.35, h*0.95); path.lineTo(w*0.65, h*0.95); path.cubicTo(w*0.8, h*0.95, w*0.95, h*0.8, w*0.95, h*0.5); path.cubicTo(w*0.95, h*0.3, w*0.9, h*0.05, w*0.7, h*0.05); path.closeSubpath()
        painter.setPen(QPen(C_OUTLINE, 3)); painter.setBrush(C_BG); painter.drawPath(path)
        def draw_button(x_off, y_off, name, text=""):
            is_on = self.button_states.get(name, False); painter.setBrush(C_BTN_ON if is_on else C_BTN_OFF); painter.setPen(Qt.NoPen); painter.drawEllipse(QPointF(c.x() + x_off, c.y() + y_off), 16, 16)
            if text: painter.setPen(C_TEXT); painter.setFont(QFont("Segoe UI", 10, QFont.Bold)); painter.drawText(QRectF(c.x()+x_off-16, c.y()+y_off-16, 32, 32), Qt.AlignCenter, text)
        abxy_y_base = h * 0.12; abxy_base_x = w * 0.29; abxy_radius = 22
        draw_button(abxy_base_x, abxy_y_base - abxy_radius, "Y", "Y"); draw_button(abxy_base_x - abxy_radius, abxy_y_base, "X", "X"); draw_button(abxy_base_x + abxy_radius, abxy_y_base, "B", "B"); draw_button(abxy_base_x, abxy_y_base + abxy_radius, "A", "A")
        dpad_bg_size = 30; dpad_arm_width=20; dpad_arm_height=25; dpad_x_base = c.x() - w*0.28; dpad_y_base = c.y() + abxy_y_base
        dpad_path = QPainterPath(); dpad_path.addRoundedRect(-dpad_bg_size/2, -dpad_bg_size/2, dpad_bg_size, dpad_bg_size, 6, 6); painter.setPen(Qt.NoPen); painter.setBrush(C_BTN_OFF); painter.drawPath(dpad_path.translated(dpad_x_base, dpad_y_base))
        def draw_dpad(name, path_segment): painter.setBrush(C_BTN_ON if self.button_states.get(name) else C_BTN_OFF); painter.setPen(Qt.NoPen); painter.drawPath(path_segment.translated(dpad_x_base, dpad_y_base))
        path_u=QPainterPath();path_u.addRect(-dpad_arm_width/2,-dpad_arm_height,dpad_arm_width,dpad_arm_height);draw_dpad("DPAD_UP",path_u); path_d=QPainterPath();path_d.addRect(-dpad_arm_width/2,0,dpad_arm_width,dpad_arm_height);draw_dpad("DPAD_DOWN",path_d); path_l=QPainterPath();path_l.addRect(-dpad_arm_height,-dpad_arm_width/2,dpad_arm_height,dpad_arm_width);draw_dpad("DPAD_LEFT",path_l); path_r=QPainterPath();path_r.addRect(0,-dpad_arm_width/2,dpad_arm_height,dpad_arm_width);draw_dpad("DPAD_RIGHT",path_r)
        draw_button(w*-0.08, h*-0.05, "BACK", "⁝"); draw_button(w*0.08, h*-0.05, "START", "≡")
        y_shoulder = h * 0.25
        lb_path=QPainterPath(); lb_path.addRoundedRect(w*0.15, y_shoulder, w*0.2, 25, 8, 8); painter.setBrush(C_BTN_ON if self.button_states.get("LB") else C_BTN_OFF); painter.drawPath(lb_path)
        rb_path=QPainterPath(); rb_path.addRoundedRect(w*0.65, y_shoulder, w*0.2, 25, 8, 8); painter.setBrush(C_BTN_ON if self.button_states.get("RB") else C_BTN_OFF); painter.drawPath(rb_path)
        painter.setPen(C_TEXT); painter.drawText(lb_path.boundingRect(), Qt.AlignCenter, "LB"); painter.drawText(rb_path.boundingRect(), Qt.AlignCenter, "RB")

class CircularityWidget(QWidget):
    def __init__(self, title: str):
        super().__init__(); self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding); self.setMinimumWidth(220)
        self.title_label = QLabel(title); self.title_label.setAlignment(Qt.AlignCenter)
        self.graph = CircularityGraph(); self.graph.setMinimumSize(180, 180)
        self.axis0_title = QLabel("AXIS 0"); self.axis0_title.setObjectName("AxisTitleLabel"); self.axis0_title.setAlignment(Qt.AlignCenter); self.axis0_value = QLabel("-.-----"); self.axis0_value.setObjectName("AxisValueLabel"); self.axis0_value.setAlignment(Qt.AlignCenter)
        self.axis1_title = QLabel("AXIS 1"); self.axis1_title.setObjectName("AxisTitleLabel"); self.axis1_title.setAlignment(Qt.AlignCenter); self.axis1_value = QLabel("-.-----"); self.axis1_value.setObjectName("AxisValueLabel"); self.axis1_value.setAlignment(Qt.AlignCenter)
        layout = QGridLayout(self); layout.setSpacing(2); layout.setContentsMargins(0, 5, 0, 5)
        layout.addWidget(self.title_label, 0, 0, 1, 2); layout.addWidget(self.graph, 1, 0, 1, 2); layout.addWidget(self.axis0_title, 2, 0); layout.addWidget(self.axis1_title, 2, 1); layout.addWidget(self.axis0_value, 3, 0); layout.addWidget(self.axis1_value, 3, 1)
        self.reset()
    def reset(self):
        self.graph.reset(); self.axis0_value.setText(f"{0.0:+.5f}"); self.axis1_value.setText(f"{0.0:+.5f}")
    def add_sample(self, x: float, y: float):
        self.graph.add_sample(x, y); self.axis0_value.setText(f"{x:+.5f}"); self.axis1_value.setText(f"{y:+.5f}")

class CircularityGraph(QWidget):
    def __init__(self, sectors: int = 24):
        super().__init__(); self.sectors = max(8, sectors); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); self.reset()
    def reset(self): self.radius_sums=[0.0]*self.sectors; self.counts=[0]*self.sectors; self.radii_all=deque(maxlen=5000); self.avg_error_pct=0.0; self.update()
    def add_sample(self, x: float, y: float):
        r = math.sqrt(x*x + y*y)
        self.radii_all.append(r); ang = math.atan2(y, x); ang = ang + 2*math.pi if ang<0 else ang; idx = int((ang/(2*math.pi))*self.sectors)%self.sectors; self.radius_sums[idx]+=r; self.counts[idx]+=1
        if len(self.radii_all) >= 20:
            avg_r = mean(self.radii_all)
            if avg_r > 1e-6: avg_deviation = mean([abs(val - avg_r) for val in self.radii_all]); self.avg_error_pct = (avg_deviation / avg_r) * 100.0
        self.update()
    def paintEvent(self, e):
        painter=QPainter(self); painter.setRenderHint(QPainter.Antialiasing); w,h,cx,cy=self.width(),self.height(),self.width()//2,self.height()//2; R=int(min(w,h)*0.45)
        painter.setPen(QPen(QColor("#404552"), 2)); painter.setBrush(Qt.NoBrush); painter.drawEllipse(cx-R,cy-R,2*R,2*R)
        for i in range(self.sectors):
            c=self.counts[i]; val=(self.radius_sums[i]/c) if c else 0.0; rlen=int(max(0.0,min(1.0,val))*R); ang=(i+0.5)*(2*math.pi/self.sectors); x2=cx+int(math.cos(ang)*rlen); y2=cy+int(math.sin(ang)*rlen)
            grad=QLinearGradient(cx,cy,x2,y2); grad.setColorAt(0,QColor(82,139,255,80)); grad.setColorAt(1,QColor(82,139,255,255)); painter.setPen(QPen(QBrush(grad),3)); painter.drawLine(cx,cy,x2,y2)
        painter.setBrush(QColor("#282c34")); painter.setPen(Qt.NoPen); painter.drawEllipse(cx-4,cy-4,8,8)
        painter.setPen(QColor("#e0e0e0")); painter.setFont(QFont("Segoe UI",10)); txt=f"Avg Error: {self.avg_error_pct:.1f}%"; tw=painter.fontMetrics().horizontalAdvance(txt); painter.drawText(int(cx-tw/2), int(cy+R+15), txt)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__(); self.setWindowTitle(f"게임패드 테스터 (GamePad Tester) v{VERSION}"); self.setObjectName("MainWindow"); self.setFixedSize(1300, 720)
        self._thread: Optional[PollingThread] = None; self._xi = XInput(); self._dev_idx = 0; self._vib_on = False; self.is_measuring = False
        self.last_connection_state = [False, False, False, False] # 실시간 연결 확인용
        root_layout = QHBoxLayout(self); root_layout.setContentsMargins(20, 20, 20, 20); root_layout.setSpacing(20)
        left_panel = self._create_left_panel(); center_panel = self._create_center_panel(); right_panel = self._create_right_panel()
        root_layout.addWidget(left_panel); root_layout.addWidget(center_panel, 1); root_layout.addWidget(right_panel)
        self._timer = QTimer(self); self._timer.setInterval(30); self._timer.timeout.connect(self.on_timer_tick); self._timer.start()
        self.refresh_devices()
    def _create_left_panel(self) -> QWidget:
        panel=QWidget(); panel.setMaximumWidth(300); layout=QVBoxLayout(panel); layout.setSpacing(15)
        title=QLabel("POLLING ANALYSIS"); title.setObjectName("TitleLabel"); status=QLabel("장치 연결 후 시작 버튼을 누르세요."); status.setObjectName("StatusLabel"); status.setWordWrap(True); self.status_label = status; self.status_label.setMinimumHeight(35); self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(title); layout.addWidget(status)
        layout.addWidget(QLabel("테스트 대상:"))
        self.cmb_xinput_device = QComboBox(); layout.addWidget(self.cmb_xinput_device)
        self.cmb_xinput_device.currentIndexChanged.connect(self.update_start_button_state)
        self.btn_refresh = QPushButton("새로고침"); self.btn_refresh.clicked.connect(self.refresh_devices); layout.addWidget(self.btn_refresh)
        self.stats = {"mean_hz": StatWidget("평균", "Hz"), "median_hz": StatWidget("중앙값", "Hz"), "mean_ms": StatWidget("평균 간격", "ms"), "median_ms": StatWidget("중앙값 간격", "ms"), "stability_pct": StatWidget("안정도", "%"), "samples": StatWidget("샘플", ""),}
        layout.addSpacing(15);
        for stat in self.stats.values(): layout.addWidget(stat)
        layout.addSpacing(15); samples_layout = QHBoxLayout(); samples_layout.addWidget(QLabel("샘플 수:")); self.cmb_samples = QComboBox(); self.cmb_samples.addItems(["1000", "2000", "4000"]); samples_layout.addWidget(self.cmb_samples); samples_layout.addStretch(1); layout.addLayout(samples_layout)
        self.chk_gyro = QCheckBox("자이로/모션 입력 포함"); layout.addWidget(self.chk_gyro)
        layout.addStretch(1);
        return panel
    def _create_center_panel(self) -> QWidget:
        panel=QWidget(); layout=QVBoxLayout(panel)
        self.gamepad_widget=GamepadWidget(); layout.addWidget(self.gamepad_widget,1)
        self.toggle_measure_button = QPushButton("측정 시작"); self.toggle_measure_button.setObjectName("StartButton"); self.toggle_measure_button.clicked.connect(self.toggle_measurement)
        button_layout=QHBoxLayout(); button_layout.addStretch(1); button_layout.addWidget(self.toggle_measure_button); button_layout.addStretch(1)
        layout.addLayout(button_layout)
        return panel
    def _create_right_panel(self) -> QWidget:
        panel=QWidget(); panel.setMinimumWidth(480)
        layout=QVBoxLayout(panel); layout.setSpacing(15)
        circ_box=QGroupBox("스틱 원형도"); circ_layout_main = QHBoxLayout()
        self.circL = CircularityWidget("L STICK"); self.circL.axis0_title.setText("AXIS 0"); self.circL.axis1_title.setText("AXIS 1")
        self.circR = CircularityWidget("R STICK"); self.circR.axis0_title.setText("AXIS 2"); self.circR.axis1_title.setText("AXIS 3")
        circ_layout_main.addWidget(self.circL); circ_layout_main.addWidget(self.circR)
        final_circ_layout = QVBoxLayout(circ_box); final_circ_layout.addLayout(circ_layout_main)
        btn_circ_reset=QPushButton("원형도 데이터 리셋"); btn_circ_reset.clicked.connect(lambda:[self.circL.reset(),self.circR.reset()]); final_circ_layout.addWidget(btn_circ_reset)
        vib_box=QGroupBox("진동(Rumble) 테스트"); vib_layout=QVBoxLayout(vib_box)
        self.sld_left=QSlider(Qt.Horizontal); self.sld_left.setRange(0,100); self.sld_left.setValue(50); self.sld_right=QSlider(Qt.Horizontal); self.sld_right.setRange(0,100); self.sld_right.setValue(50)
        self.btn_vib=QPushButton("진동 테스트"); self.btn_vib.clicked.connect(self.toggle_vibration)
        vib_layout.addWidget(QLabel("저주파")); vib_layout.addWidget(self.sld_left); vib_layout.addWidget(QLabel("고주파")); vib_layout.addWidget(self.sld_right); vib_layout.addWidget(self.btn_vib)
        self.sld_left.valueChanged.connect(self.update_vibration_intensity); self.sld_right.valueChanged.connect(self.update_vibration_intensity)
        layout.addWidget(circ_box,1); layout.addWidget(vib_box,0)
        return panel
    @Slot()
    def on_timer_tick(self):
        self.check_connection_status_realtime()
        self.update_gamepad_ui()
    def check_connection_status_realtime(self):
        current_connections = [self._xi.get_state(i)[0] == ERROR_SUCCESS for i in range(4)]
        if current_connections != self.last_connection_state:
            self.last_connection_state = current_connections
            self.refresh_devices()
    def update_start_button_state(self):
        if self.is_measuring: return
        idx = self.cmb_xinput_device.currentData(Qt.UserRole)
        if idx is None:
            self.toggle_measure_button.setEnabled(False)
            return
        res, _ = self._xi.get_state(idx)
        self.toggle_measure_button.setEnabled(res == ERROR_SUCCESS)
    @Slot()
    def update_gamepad_ui(self):
        idx = int(self.cmb_xinput_device.currentData(Qt.UserRole) or 0); res, state = self._xi.get_state(idx)
        if res == ERROR_SUCCESS:
            gp = state.Gamepad; self.gamepad_widget.update_state(gp)
            self.circL.add_sample(gp.sThumbLX / 32767.0, -gp.sThumbLY / 32767.0)
            self.circR.add_sample(gp.sThumbRX / 32767.0, -gp.sThumbRY / 32767.0)
    @Slot()
    def toggle_measurement(self):
        if self.is_measuring: self.stop_measure()
        else: self.start_measure()
    def start_measure(self):
        if self._thread and self._thread.isRunning(): return
        self._dev_idx = int(self.cmb_xinput_device.currentData(Qt.UserRole) or 0); window_samples = int(self.cmb_samples.currentText()); include_gyro = self.chk_gyro.isChecked()
        self._thread = PollingThread(self._dev_idx, window_samples=window_samples, include_gyro=include_gyro)
        if self.chk_gyro.isCheckable(): self.chk_gyro.toggled.connect(self._thread.set_include_gyro)
        self._thread.statsUpdated.connect(self.on_stats); self._thread.deviceError.connect(self.on_error); self._thread.start()
        self.is_measuring = True; self.toggle_measure_button.setText("측정 중지"); self.toggle_measure_button.setObjectName("StopButton"); self.style().polish(self.toggle_measure_button); self.status_label.setText("측정 중... 컨트롤러를 계속 움직여주세요.")
        self.cmb_xinput_device.setEnabled(False); self.btn_refresh.setEnabled(False)
    def stop_measure(self):
        if self._thread and self._thread.snapshot_intervals_ns():
            self.auto_save_report(self._thread.snapshot_intervals_ns())
        if self._thread: self._thread.stop(); self._thread.wait(1500); self._thread = None
        if self._vib_on: self._xi.set_vibration(self._dev_idx, 0, 0); self._vib_on = False; self.btn_vib.setText("진동 테스트")
        self.is_measuring = False; self.toggle_measure_button.setText("측정 시작"); self.toggle_measure_button.setObjectName("StartButton"); self.style().polish(self.toggle_measure_button); self.status_label.setText("측정이 중지되었습니다.")
        self.cmb_xinput_device.setEnabled(True); self.btn_refresh.setEnabled(True); self.update_start_button_state()
    @Slot(dict)
    def on_stats(self, stats: dict):
        self.stats["mean_hz"].set_value(stats.get("mean_hz")); self.stats["median_hz"].set_value(stats.get("median_hz")); self.stats["mean_ms"].set_value(stats.get("mean_ms"))
        self.stats["median_ms"].set_value(stats.get("median_ms")); self.stats["stability_pct"].set_value(stats.get("stability_pct")); self.stats["samples"].set_value(stats.get("samples"), "{:,.0f}")
    @Slot(str)
    def on_error(self, msg: str): self.status_label.setText(f"오류: {msg}"); self.stop_measure()
    def refresh_devices(self):
        pygame_names = get_gamepad_names_from_pygame()
        current_selection = self.cmb_xinput_device.currentData(Qt.UserRole)
        self.cmb_xinput_device.clear()
        for idx in range(4):
            res, _ = self._xi.get_state(idx); label = f"#{idx + 1}"
            if res == ERROR_SUCCESS:
                name = pygame_names.get(idx)
                if name: label += f" [{name}]"
                else:
                    caps = self._xi.get_capabilities(idx)
                    subtype_name = _SUBTYPE_NAME.get(caps.SubType, "장치") if caps else "장치"; label += f" [{subtype_name}]"
            else: label += " (미연결)"
            self.cmb_xinput_device.addItem(label, userData=idx)
        if current_selection is not None: self.cmb_xinput_device.setCurrentIndex(current_selection)
        self.update_start_button_state()

    def auto_save_report(self, data_ns: List[int]):
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        dev_text = self.cmb_xinput_device.currentText()
        sanitized_name = "".join(c for c in dev_text if c.isalnum() or c in " _-").replace("__", "_").strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Report_{sanitized_name}_{timestamp}.txt"
        path = os.path.join(base_path, filename)
        stats = self._compute_stats_static(data_ns)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Gamepad Polling Rate Test Report\n"); f.write("="*40 + "\n"); f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"); f.write(f"Device: {dev_text}\n"); f.write("="*40 + "\n\n")
                f.write("[Summary]\n"); f.write(f"  Average Rate: {stats.get('mean_hz', 0):.2f} Hz\n"); f.write(f"  Median Rate: {stats.get('median_hz', 0):.2f} Hz\n"); f.write(f"  Average Interval: {stats.get('mean_ms', 0):.3f} ms\n")
                f.write(f"  Median Interval: {stats.get('median_ms', 0):.3f} ms\n"); f.write(f"  Stability: {stats.get('stability_pct', 0):.1f}%\n"); f.write(f"  Total Samples: {len(data_ns):,}\n\n")
                f.write("[Raw Interval Data (ms)]\n")
                for ns in data_ns: f.write(f"{ns / 1_000_000.0:.4f}\n")
            self.status_label.setText(f"결과가 {filename}에 자동 저장되었습니다.")
            dlg = QMessageBox(self); dlg.setWindowTitle("저장 완료"); dlg.setText("테스트 결과가 저장되었습니다."); dlg.setInformativeText(f"파일 위치: {path}"); ok_button = dlg.addButton("확인", QMessageBox.AcceptRole); dlg.setIcon(QMessageBox.Information); dlg.exec()
        except Exception as e:
            self.status_label.setText(f"파일 자동 저장 실패: {e}")
    @staticmethod
    def _compute_stats_static(intervals_ns: List[int]) -> dict:
        if len(intervals_ns) < 10: return {"samples": len(intervals_ns)}
        ms = [x / 1_000_000.0 for x in intervals_ns]
        mu = mean(ms)
        if len(ms) > 1:
            sigma = stdev(ms); low, high = mu - 2 * sigma, mu + 2 * sigma
            stability = (sum(1 for v in ms if low <= v <= high) / len(ms)) * 100.0
        else: stability = 100.0
        return {"samples": len(ms), "mean_ms": mu, "median_ms": median(ms), "mean_hz": 1000.0/mu if mu > 0 else 0, "median_hz": 1000.0/median(ms) if median(ms) > 0 else 0, "stability_pct": stability}
    @Slot()
    def update_vibration_intensity(self):
        if self._vib_on:
            idx = int(self.cmb_xinput_device.currentData(Qt.UserRole) or 0)
            l = int(self.sld_left.value() * 655.35); r = int(self.sld_right.value() * 655.35); self._xi.set_vibration(idx, l, r)
    def toggle_vibration(self):
        idx = int(self.cmb_xinput_device.currentData(Qt.UserRole) or 0)
        if self._xi.get_state(idx)[0] != ERROR_SUCCESS: return
        if not self._vib_on: self._vib_on = True; self.btn_vib.setText("테스트 종료"); self.update_vibration_intensity()
        else: self._vib_on = False; self.btn_vib.setText("진동 테스트"); self._xi.set_vibration(idx, 0, 0)
    def closeEvent(self, event):
        self.stop_measure(); super().closeEvent(event)

def _load_app_icon() -> Optional[QIcon]:
    try: from icon import ICON_BASE64
    except Exception: return None
    try: pm = QPixmap(); pm.loadFromData(base64.b64decode(ICON_BASE64)); return QIcon(pm)
    except Exception: return None

def main():
    if os.name != "nt": print("이 프로그램은 Windows(XInput) 전용입니다."); return
    app = QApplication(sys.argv); app.setStyleSheet(STYLESHEET)
    app_icon = _load_app_icon()
    if app_icon: app.setWindowIcon(app_icon)
    w = MainWindow()
    if app_icon: w.setWindowIcon(app_icon)
    w.show(); sys.exit(app.exec())

if __name__ == "__main__":
    main()