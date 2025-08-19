# -*- coding: utf-8 -*-
# GamePadTester
# Version: 1.8.5
"""
XInput 기반 게임 컨트롤러 테스터 (화이트 UI 테마)
- v1.8.5: icon.py 의존성 제거 및 아이콘 내장, 코드 최적화
- v1.8.4: 코드 전반 재점검 및 최적화, 버튼 비활성화 스타일 적용, D-Pad 및 UI 레이아웃 최종 수정
- v1.8.3: 자이로/모션 입력을 라디오 버튼으로 변경, 샘플 수 옵션 및 기본값 수정, D-Pad 레이아웃 조정
- v1.8.2: LB/RB 및 LT/RT 버튼 크기 재조정, 좌측 패널 '테스트 대상' 레이아웃 조정, 체크박스 스타일 수정
- v1.8.1: 샘플 수 기반 자동 측정 종료 기능 추가, '500' 샘플 옵션 추가 및 기본값 설정, 미연결 시 측정 버튼 비활성화 처리
- v1.8.0: LB/RB 및 LT/RT 버튼 크기 조정
- v1.7.9: D-Pad 간격 추가 조정, 어깨/트리거 버튼 크기 미세 조정, 체크박스 스타일 개선
- v1.7.8: 트리거/어깨 버튼 레이아웃 변경, 체크박스 스타일 수정, 좌측 패널 레이아웃 미세 조정
- v1.7.7: 체크박스 체크 표시 시인성 개선, 게임패드 UI 레이아웃 전면 재배치, D-Pad 디자인 변경
- v1.7.6: 체크박스 시인성 개선, 게임패드 UI 레이아웃 재배치 및 버튼 크기 조정
- v1.7.5: 콤보박스 드롭다운 스타일 수정, D-Pad 및 트리거 UI 시각적 개선
- v1.7.4: UI 크기 변동 문제 수정, 진동 테스트 그룹박스 제목 제거
- v1.7.3: UI 레이아웃 및 스타일 미세 조정 (체크박스, 버튼, 그룹박스 제목 잘림 문제 해결)
- v1.7.2: 좌측 패널 레이아웃 조정, 게임패드 D-Pad 및 ABXY 버튼 시인성 개선
- v1.7.1: 화이트 테마 적용 및 시인성 개선, 게임패드 UI 재설계 (트리거 버튼 위치 및 스타일 변경), 이름 변경
- 기능은 원본 코드를 계승, UI/UX 및 코드 구조를 완전히 재설계
- 의존성: PySide6, pygame
"""
from __future__ import annotations
import sys
import os
import time
import threading
import math
import base64
import webbrowser
import atexit
import tempfile
import json
from collections import deque
from statistics import mean, median, stdev
from typing import Deque, List, Optional, Tuple
from datetime import datetime
from urllib import request as url_request

# ----- 버전 정보 -----
VERSION = "2.0.1"

# ----- 아이콘 데이터 -----
ICON_BASE64 = "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"

# ----- Qt (PySide6) -----
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer, QPointF, QRectF, QSize
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QIcon, QPixmap, QPainterPath, QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QFileDialog, QFrame, QSlider, QSizePolicy, QMessageBox, QDialog,
    QRadioButton
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

class PollingThread(QThread):
    statsUpdated = Signal(dict)
    deviceError = Signal(str)
    measurementFinished = Signal() # Signal to indicate measurement is complete
    def __init__(self, device_index: int, max_samples: int = 1000, include_gyro: bool = False):
        super().__init__()
        self.device_index = device_index; self.max_samples = max(20, int(max_samples)); self.include_gyro = include_gyro; self._stop = threading.Event(); self.xi = XInput(); self._lock = threading.Lock(); self._intervals_ns: Deque[int] = deque(maxlen=self.max_samples); self._all_intervals_ns: List[int] = []; self._last_state = XINPUT_STATE(); self._last_change_ts_ns: Optional[int] = None
    
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
                        with self._lock: 
                            self._intervals_ns.append(dt)
                            self._all_intervals_ns.append(dt)
                            # Check if max samples reached
                            if len(self._all_intervals_ns) >= self.max_samples:
                                self.statsUpdated.emit(self._compute_stats(list(self._intervals_ns)))
                                self.measurementFinished.emit()
                                break
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

class UpdateCheckThread(QThread):
    updateAvailable = Signal(str)
    def run(self):
        try:
            req = url_request.Request("[https://api.github.com/repos/deuxdoom/GamePadTester/releases/latest](https://api.github.com/repos/deuxdoom/GamePadTester/releases/latest)", headers={'Accept': 'application/vnd.github.v3+json'})
            with url_request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                latest_version_tag = data['tag_name']
                latest_version = latest_version_tag.lstrip('v')
                if tuple(map(int, latest_version.split('.'))) > tuple(map(int, VERSION.split('.'))):
                    self.updateAvailable.emit(latest_version)
        except Exception as e:
            print(f"업데이트 확인 실패: {e}")

STYLESHEET = """
QWidget { color: #333; font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; font-size: 10pt; }
MainWindow, QDialog { background-color: #f4f4f4; }
QGroupBox { font-size: 11pt; font-weight: bold; border: 1px solid #ccc; border-radius: 8px; margin-top: 10px; background-color: #fff; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; left: 10px; color: #555; }
QLabel#TitleLabel { font-size: 16pt; font-weight: bold; color: #000; }
QLabel#StatusLabel { font-size: 9pt; color: #666; }
QLabel#AxisValueLabel { font-size: 11pt; font-weight: bold; color: #005a9e; }
QLabel#AxisTitleLabel { font-size: 8pt; color: #777; }
QLabel#StatTitleLabel { color: #666; font-size: 9pt; }
QLabel#StatValueLabel { color: #005a9e; font-size: 18pt; font-weight: bold; }
QLabel#StatUnitLabel { color: #666; font-size: 12pt; margin-bottom: 2px; }
QPushButton { background-color: #e7e7e7; border: 1px solid #adadad; border-radius: 6px; padding: 8px 12px; font-weight: bold; min-width: 80px; color: #333; }
QPushButton:hover { background-color: #dcdcdc; }
QPushButton:pressed { background-color: #d0d0d0; }
QPushButton:disabled { background-color: #f5f5f5; color: #aaa; border-color: #dcdcdc; }
QPushButton#StartButton { background-color: #007bff; color: white; border-color: #0069d9; }
QPushButton#StartButton:hover { background-color: #0069d9; }
QPushButton#StartButton:disabled { background-color: #e7e7e7; color: #aaa; border-color: #dcdcdc; }
QPushButton#StopButton { background-color: #dc3545; color: white; border-color: #c82333; }
QPushButton#StopButton:hover { background-color: #c82333; }
QPushButton#VibButton { background-color: #ffc107; color: #212529; border-color: #e0a800; }
QPushButton#VibButton:hover { background-color: #e0a800; }
QPushButton#InfoButton { background-color: #17a2b8; color: white; border-color: #138496; padding: 5px 10px; min-width: 0; }
QPushButton#InfoButton:hover { background-color: #138496; }
QComboBox { background-color: #fff; border: 1px solid #ccc; border-radius: 4px; padding: 6px; }
QComboBox QAbstractItemView {
    background-color: #fff;
    color: #333;
    selection-background-color: #007bff;
    border: 1px solid #ccc;
}
QRadioButton { color: #333; }
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #adadad;
    border-radius: 8px;
    background-color: #fff;
}
QRadioButton::indicator:checked {
    background-color: #007bff;
    border: 3px solid #fff;
    outline: 1px solid #007bff;
}
QComboBox::drop-down { border: none; }
QSlider::groove:horizontal { height: 4px; background: #ddd; border-radius: 2px; }
QSlider::handle:horizontal { width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; background: #007bff; }
"""

class StatWidget(QWidget):
    def __init__(self, title: str, unit: str):
        super().__init__()
        self.title_label = QLabel(title)
        self.value_label = QLabel("-")
        self.unit_label = QLabel(unit)
        self.title_label.setObjectName("StatTitleLabel")
        self.value_label.setObjectName("StatValueLabel")
        self.unit_label.setObjectName("StatUnitLabel")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.title_label, 1, Qt.AlignBottom)
        layout.addSpacing(10)
        layout.addWidget(self.value_label, 0, Qt.AlignBottom | Qt.AlignRight)
        layout.addSpacing(5)
        layout.addWidget(self.unit_label, 0, Qt.AlignBottom | Qt.AlignLeft)

    def set_value(self, value: Optional[float], fmt: str = "{:.2f}"):
        self.value_label.setText(fmt.format(value) if value is not None else "-")

class AnalogStickWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.x, self.y = 0.0, 0.0
        self.is_pressed = False
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(100, 100)

    def set_pos(self, x: float, y: float):
        self.x, self.y = x, -y
        self.update()

    def set_pressed(self, pressed: bool):
        if self.is_pressed != pressed:
            self.is_pressed = pressed
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        size = min(self.width(), self.height())
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = size / 2 * 0.9
        
        # White Theme Colors
        border_color = QColor("#007bff") if self.is_pressed else QColor("#adadad")
        handle_color = QColor("#333333")
        bg_color = QColor("#f0f0f0")

        painter.setPen(QPen(border_color, 2))
        painter.setBrush(bg_color)
        painter.drawEllipse(center, radius, radius)
        
        handle_pos = QPointF(center.x() + self.x * radius * 0.7, center.y() + self.y * radius * 0.7)
        painter.setBrush(handle_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(handle_pos, radius * 0.4, radius * 0.4)

class GamepadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.button_states = {}
        self.trigger_L_val = 0.0
        self.trigger_R_val = 0.0
        self.stick_L = AnalogStickWidget()
        self.stick_R = AnalogStickWidget()
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setRowStretch(0, 1) # Top area for drawing
        layout.addWidget(self.stick_L, 1, 0)
        layout.addWidget(self.stick_R, 1, 1)
        layout.setRowStretch(1, 0) # Sticks take their own size

    def update_state(self, gp_state: XINPUT_GAMEPAD):
        self.button_states = {
            "DPAD_UP": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_UP),
            "DPAD_DOWN": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_DOWN),
            "DPAD_LEFT": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_LEFT),
            "DPAD_RIGHT": bool(gp_state.wButtons & XINPUT_GAMEPAD_DPAD_RIGHT),
            "START": bool(gp_state.wButtons & XINPUT_GAMEPAD_START),
            "BACK": bool(gp_state.wButtons & XINPUT_GAMEPAD_BACK),
            "LTHUMB": bool(gp_state.wButtons & XINPUT_GAMEPAD_LEFT_THUMB),
            "RTHUMB": bool(gp_state.wButtons & XINPUT_GAMEPAD_RIGHT_THUMB),
            "LB": bool(gp_state.wButtons & XINPUT_GAMEPAD_LEFT_SHOULDER),
            "RB": bool(gp_state.wButtons & XINPUT_GAMEPAD_RIGHT_SHOULDER),
            "A": bool(gp_state.wButtons & XINPUT_GAMEPAD_A),
            "B": bool(gp_state.wButtons & XINPUT_GAMEPAD_B),
            "X": bool(gp_state.wButtons & XINPUT_GAMEPAD_X),
            "Y": bool(gp_state.wButtons & XINPUT_GAMEPAD_Y),
        }
        self.stick_L.set_pos(gp_state.sThumbLX / 32767.0, gp_state.sThumbLY / 32767.0)
        self.stick_R.set_pos(gp_state.sThumbRX / 32767.0, gp_state.sThumbRY / 32767.0)
        self.stick_L.set_pressed(self.button_states.get("LTHUMB", False))
        self.stick_R.set_pressed(self.button_states.get("RTHUMB", False))
        self.trigger_L_val = gp_state.bLeftTrigger / 255.0
        self.trigger_R_val = gp_state.bRightTrigger / 255.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c, w, h = self.rect().center(), self.width(), self.height()

        # White Theme Colors
        C_OUTLINE = QColor("#d0d0d0")
        C_BG = QColor("#ffffff")
        C_BTN_OFF = QColor("#e9e9e9")
        C_BTN_ON = QColor("#007bff")
        C_TEXT = QColor("#333333")
        C_BORDER = QColor("#adadad")

        # Gamepad Body Shape
        painter.setPen(QPen(C_OUTLINE, 2))
        painter.setBrush(C_BG)
        body_rect = self.rect().adjusted(10, 10, -10, -(self.stick_L.height() + 22))
        painter.drawRoundedRect(body_rect, 30, 30)

        # --- Triggers (LT/RT) and Shoulder Buttons (LB/RB) ---
        trigger_h = 65
        trigger_w = 35
        shoulder_h = 32
        shoulder_w = w * 0.17
        
        trigger_y = body_rect.y() + 15
        shoulder_y = trigger_y + trigger_h + 12

        # Left Side
        left_x_center = body_rect.x() + 85
        lt_rect = QRectF(left_x_center - trigger_w / 2, trigger_y, trigger_w, trigger_h)
        lb_rect = QRectF(left_x_center - shoulder_w / 2, shoulder_y, shoulder_w, shoulder_h)

        # Right Side
        right_x_center = body_rect.right() - 85
        rt_rect = QRectF(right_x_center - trigger_w / 2, trigger_y, trigger_w, trigger_h)
        rb_rect = QRectF(right_x_center - shoulder_w / 2, shoulder_y, shoulder_w, shoulder_h)

        # Draw LT (Vertical)
        painter.setPen(QPen(C_BORDER, 1))
        painter.setBrush(C_BTN_OFF)
        painter.drawRoundedRect(lt_rect, 6, 6)
        if self.trigger_L_val > 0:
            fill_h = lt_rect.height() * self.trigger_L_val
            fill_lt = QRectF(lt_rect.x(), lt_rect.y() + lt_rect.height() - fill_h, lt_rect.width(), fill_h)
            painter.setBrush(C_BTN_ON)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(fill_lt, 6, 6)
        painter.setPen(C_TEXT)
        painter.drawText(lt_rect, Qt.AlignTop | Qt.AlignHCenter, "LT")

        # Draw LB
        painter.setPen(QPen(C_BORDER, 1))
        painter.setBrush(C_BTN_ON if self.button_states.get("LB") else C_BTN_OFF)
        painter.drawRoundedRect(lb_rect, 8, 8)
        painter.setPen(C_TEXT)
        painter.drawText(lb_rect, Qt.AlignCenter, "LB")

        # Draw RT (Vertical)
        painter.setPen(QPen(C_BORDER, 1))
        painter.setBrush(C_BTN_OFF)
        painter.drawRoundedRect(rt_rect, 6, 6)
        if self.trigger_R_val > 0:
            fill_h = rt_rect.height() * self.trigger_R_val
            fill_rt = QRectF(rt_rect.x(), rt_rect.y() + rt_rect.height() - fill_h, rt_rect.width(), fill_h)
            painter.setBrush(C_BTN_ON)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(fill_rt, 6, 6)
        painter.setPen(C_TEXT)
        painter.drawText(rt_rect, Qt.AlignTop | Qt.AlignHCenter, "RT")

        # Draw RB
        painter.setPen(QPen(C_BORDER, 1))
        painter.setBrush(C_BTN_ON if self.button_states.get("RB") else C_BTN_OFF)
        painter.drawRoundedRect(rb_rect, 8, 8)
        painter.setPen(C_TEXT)
        painter.drawText(rb_rect, Qt.AlignCenter, "RB")

        def draw_button(x_pos, y_pos, name, text=""):
            is_on = self.button_states.get(name, False)
            painter.setBrush(C_BTN_ON if is_on else C_BTN_OFF)
            painter.setPen(QPen(C_BORDER, 1))
            painter.drawEllipse(QPointF(x_pos, y_pos), 22, 22)
            if text:
                painter.setPen(C_TEXT)
                painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
                painter.drawText(QRectF(x_pos - 22, y_pos - 22, 44, 44), Qt.AlignCenter, text)

        # ABXY Buttons
        abxy_y_base = c.y() + h * 0.05
        abxy_x_base = c.x() + w * 0.27
        abxy_radius = 32
        draw_button(abxy_x_base, abxy_y_base - abxy_radius, "Y", "Y")
        draw_button(abxy_x_base - abxy_radius, abxy_y_base, "X", "X")
        draw_button(abxy_x_base + abxy_radius, abxy_y_base, "B", "B")
        draw_button(abxy_x_base, abxy_y_base + abxy_radius, "A", "A")

        # D-Pad
        dpad_x_base = c.x() - w * 0.27
        dpad_y_base = abxy_y_base
        arm_w = 30
        arm_l = 30
        gap = 15 # D-Pad gap adjusted
        
        # Define rects for each arm
        rect_up = QRectF(dpad_x_base - arm_w/2, dpad_y_base - arm_l - gap, arm_w, arm_l)
        rect_down = QRectF(dpad_x_base - arm_w/2, dpad_y_base + gap, arm_w, arm_l)
        rect_left = QRectF(dpad_x_base - arm_l - gap, dpad_y_base - arm_w/2, arm_l, arm_w)
        rect_right = QRectF(dpad_x_base + gap, dpad_y_base - arm_w/2, arm_l, arm_w)

        painter.setPen(QPen(C_BORDER, 1))
        painter.setBrush(C_BTN_ON if self.button_states.get("DPAD_UP") else C_BTN_OFF); painter.drawRoundedRect(rect_up, 4, 4)
        painter.setBrush(C_BTN_ON if self.button_states.get("DPAD_DOWN") else C_BTN_OFF); painter.drawRoundedRect(rect_down, 4, 4)
        painter.setBrush(C_BTN_ON if self.button_states.get("DPAD_LEFT") else C_BTN_OFF); painter.drawRoundedRect(rect_left, 4, 4)
        painter.setBrush(C_BTN_ON if self.button_states.get("DPAD_RIGHT") else C_BTN_OFF); painter.drawRoundedRect(rect_right, 4, 4)

        # Center Buttons (Start/Back)
        draw_button(c.x() - 50, c.y() - h * 0.15, "BACK", "⁝")
        draw_button(c.x() + 50, c.y() - h * 0.15, "START", "≡")

class AxisDisplayWidget(QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setMinimumWidth(200)
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.axis0_title = QLabel("AXIS 0"); self.axis0_title.setObjectName("AxisTitleLabel"); self.axis0_title.setAlignment(Qt.AlignCenter)
        self.axis0_value = QLabel("-.-----"); self.axis0_value.setObjectName("AxisValueLabel"); self.axis0_value.setAlignment(Qt.AlignCenter)
        self.axis1_title = QLabel("AXIS 1"); self.axis1_title.setObjectName("AxisTitleLabel"); self.axis1_title.setAlignment(Qt.AlignCenter)
        self.axis1_value = QLabel("-.-----"); self.axis1_value.setObjectName("AxisValueLabel"); self.axis1_value.setAlignment(Qt.AlignCenter)
        layout = QGridLayout(self); layout.setSpacing(2); layout.setContentsMargins(0, 5, 0, 5)
        layout.addWidget(self.title_label, 0, 0, 1, 2)
        layout.addWidget(self.axis0_title, 1, 0); layout.addWidget(self.axis1_title, 1, 1)
        layout.addWidget(self.axis0_value, 2, 0); layout.addWidget(self.axis1_value, 2, 1)
        self.reset()
    def reset(self):
        self.axis0_value.setText(f"{0.0:+.5f}"); self.axis1_value.setText(f"{0.0:+.5f}")
    def update_values(self, x: float, y: float):
        self.axis0_value.setText(f"{x:+.5f}"); self.axis1_value.setText(f"{y:+.5f}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"게임패드 테스터 v{VERSION}")
        self.setObjectName("MainWindow")
        self.setFixedSize(1300, 720)
        self._thread: Optional[PollingThread] = None; self._xi = XInput(); self._dev_idx = 0; self._vib_on = False; self.is_measuring = False
        self.last_connection_state = [False, False, False, False]
        
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(20)
        
        left_panel = self._create_left_panel()
        center_panel = self._create_center_panel()
        root_layout.addWidget(left_panel, 4)
        root_layout.addWidget(center_panel, 6)

        self._timer = QTimer(self); self._timer.setInterval(16); self._timer.timeout.connect(self.on_timer_tick); self._timer.start()
        self.refresh_devices()
        self.update_checker = UpdateCheckThread(); self.update_checker.updateAvailable.connect(self.show_update_dialog); self.update_checker.start()

    def _create_left_panel(self) -> QWidget:
        panel=QWidget()
        layout=QGridLayout(panel)
        layout.setSpacing(15)
        layout.setColumnStretch(1, 1) # Make second column stretchable

        title=QLabel("폴링 및 입력 테스트"); title.setObjectName("TitleLabel")
        status=QLabel("장치 연결 후 시작 버튼을 누르세요."); status.setObjectName("StatusLabel"); status.setWordWrap(True)
        self.status_label = status
        self.status_label.setFixedHeight(35) # Fix height to prevent UI resizing
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.btn_about = QPushButton("정보"); self.btn_about.setObjectName("InfoButton")
        self.btn_about.clicked.connect(self.show_about_dialog)
        self.btn_about.setFixedSize(60, 28)

        layout.addWidget(title, 0, 0, 1, 1)
        layout.addWidget(self.btn_about, 0, 1, Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(status, 1, 0, 1, 2)
        
        self.btn_refresh = QPushButton("새로고침")
        self.btn_refresh.clicked.connect(self.refresh_devices)
        layout.addWidget(self.btn_refresh, 2, 1, Qt.AlignRight) 

        device_label = QLabel("테스트 대상:")
        device_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        layout.addWidget(device_label, 3, 0)
        self.cmb_xinput_device = QComboBox()
        self.cmb_xinput_device.currentIndexChanged.connect(self.update_start_button_state)
        layout.addWidget(self.cmb_xinput_device, 3, 1)

        self.stats = {
            "mean_hz": StatWidget("평균", "Hz"), 
            "median_hz": StatWidget("중앙값", "Hz"), 
            "mean_ms": StatWidget("평균 간격", "ms"), 
            "stability_pct": StatWidget("안정도", "%"),
        }
        
        layout.addWidget(self.stats["mean_hz"], 4, 0)
        layout.addWidget(self.stats["median_hz"], 4, 1)
        layout.addWidget(self.stats["mean_ms"], 5, 0)
        layout.addWidget(self.stats["stability_pct"], 5, 1)

        samples_layout = QHBoxLayout()
        samples_layout.addWidget(QLabel("샘플 수:"))
        self.cmb_samples = QComboBox()
        self.cmb_samples.addItems(["1000", "2000", "4000"])
        self.cmb_samples.setCurrentText("2000")
        samples_layout.addWidget(self.cmb_samples)
        samples_layout.addStretch(1)
        
        layout.addLayout(samples_layout, 6, 0)
        
        gyro_layout = QHBoxLayout()
        self.radio_standard = QRadioButton("표준 입력")
        self.radio_gyro = QRadioButton("자이로 포함")
        self.radio_standard.setChecked(True)
        gyro_layout.addWidget(self.radio_standard)
        gyro_layout.addWidget(self.radio_gyro)
        gyro_layout.addStretch(1)
        layout.addLayout(gyro_layout, 6, 1)


        line = QFrame(); line.setFrameShape(QFrame.HLine); line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 7, 0, 1, 2)

        self.axis_box = QGroupBox("스틱 AXIS 값")
        axis_layout = QHBoxLayout(self.axis_box)
        self.axis_L = AxisDisplayWidget("좌측 스틱"); self.axis_R = AxisDisplayWidget("우측 스틱")
        self.axis_L.axis0_title.setText("AXIS 0"); self.axis_L.axis1_title.setText("AXIS 1")
        self.axis_R.axis0_title.setText("AXIS 2"); self.axis_R.axis1_title.setText("AXIS 3")
        axis_layout.addWidget(self.axis_L); axis_layout.addWidget(self.axis_R)
        
        # Remove title from vibration GroupBox
        vib_box=QGroupBox("")
        vib_layout=QVBoxLayout(vib_box)
        self.sld_left=QSlider(Qt.Horizontal); self.sld_left.setRange(0,100); self.sld_left.setValue(50)
        self.sld_right=QSlider(Qt.Horizontal); self.sld_right.setRange(0,100); self.sld_right.setValue(50)
        self.btn_vib=QPushButton("진동 테스트"); self.btn_vib.setObjectName("VibButton"); self.btn_vib.clicked.connect(self.toggle_vibration)
        vib_layout.addWidget(QLabel("좌측 진동 모터")); vib_layout.addWidget(self.sld_left); vib_layout.addWidget(QLabel("우측 진동 모터")); vib_layout.addWidget(self.sld_right); vib_layout.addWidget(self.btn_vib)
        self.sld_left.valueChanged.connect(self.update_vibration_intensity); self.sld_right.valueChanged.connect(self.update_vibration_intensity)
        
        layout.addWidget(self.axis_box, 8, 0, 1, 2)
        layout.addWidget(vib_box, 9, 0, 1, 2)
        
        layout.setRowStretch(10, 1)
        
        return panel
        
    def _create_center_panel(self) -> QWidget:
        panel=QWidget(); layout=QVBoxLayout(panel)
        self.gamepad_widget=GamepadWidget(); layout.addWidget(self.gamepad_widget,1)
        self.toggle_measure_button = QPushButton("측정 시작"); self.toggle_measure_button.setObjectName("StartButton"); self.toggle_measure_button.clicked.connect(self.toggle_measurement)
        button_layout=QHBoxLayout(); button_layout.addStretch(1); button_layout.addWidget(self.toggle_measure_button); button_layout.addStretch(1)
        layout.addLayout(button_layout)
        return panel

    @Slot()
    def on_timer_tick(self):
        self.check_connection_status_realtime(); self.update_gamepad_ui()

    def check_connection_status_realtime(self):
        current_connections = [self._xi.get_state(i)[0] == ERROR_SUCCESS for i in range(4)]
        if current_connections != self.last_connection_state:
            self.last_connection_state = current_connections; self.refresh_devices()

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
            self.axis_L.update_values(gp.sThumbLX / 32767.0, -gp.sThumbLY / 32767.0)
            self.axis_R.update_values(gp.sThumbRX / 32767.0, -gp.sThumbRY / 32767.0)

    @Slot()
    def toggle_measurement(self):
        if self.is_measuring: self.stop_measure()
        else: self.start_measure()

    def start_measure(self):
        if self._thread and self._thread.isRunning(): return
        self._dev_idx = int(self.cmb_xinput_device.currentData(Qt.UserRole) or 0)
        max_samples = int(self.cmb_samples.currentText())
        include_gyro = self.radio_gyro.isChecked()
        self._thread = PollingThread(self._dev_idx, max_samples=max_samples, include_gyro=include_gyro)
        self._thread.statsUpdated.connect(self.on_stats)
        self._thread.deviceError.connect(self.on_error)
        self._thread.measurementFinished.connect(self.stop_measure) # Connect new signal
        self._thread.start()
        self.is_measuring = True; self.toggle_measure_button.setText("측정 중지"); self.toggle_measure_button.setObjectName("StopButton"); self.style().polish(self.toggle_measure_button); self.status_label.setText("측정 중... 컨트롤러를 계속 움직여주세요.")
        self.cmb_xinput_device.setEnabled(False); self.btn_refresh.setEnabled(False)

    @Slot()
    def stop_measure(self):
        data_to_save = None
        if self._thread:
            if self._thread.snapshot_intervals_ns(): data_to_save = self._thread.snapshot_intervals_ns()
            self._thread.stop(); self._thread.wait(1500); self._thread = None
        if data_to_save: self.auto_save_report(data_to_save)
        if self._vib_on: self._xi.set_vibration(self._dev_idx, 0, 0); self._vib_on = False; self.btn_vib.setText("진동 테스트")
        self.is_measuring = False; self.toggle_measure_button.setText("측정 시작"); self.toggle_measure_button.setObjectName("StartButton"); self.style().polish(self.toggle_measure_button); self.status_label.setText("측정이 중지되었습니다.")
        self.cmb_xinput_device.setEnabled(True); self.btn_refresh.setEnabled(True); self.update_start_button_state()
        for stat_widget in self.stats.values():
            stat_widget.set_value(None)

    @Slot(dict)
    def on_stats(self, stats: dict):
        self.stats["mean_hz"].set_value(stats.get("mean_hz"))
        self.stats["median_hz"].set_value(stats.get("median_hz"))
        self.stats["mean_ms"].set_value(stats.get("mean_ms"))
        self.stats["stability_pct"].set_value(stats.get("stability_pct"))

    @Slot(str)
    def on_error(self, msg: str): self.status_label.setText(f"오류: {msg}"); self.stop_measure()

    def refresh_devices(self):
        pygame_names = get_gamepad_names_from_pygame()
        current_selection = self.cmb_xinput_device.currentData(Qt.UserRole)
        self.cmb_xinput_device.clear()
        any_connected = False
        for idx in range(4):
            res, _ = self._xi.get_state(idx); label = f"#{idx + 1}"
            if res == ERROR_SUCCESS:
                any_connected = True
                name = pygame_names.get(idx, "")
                if name: label += f" [{name.split(' (Controller')[0]}]"
                else:
                    caps = self._xi.get_capabilities(idx)
                    subtype_name = _SUBTYPE_NAME.get(caps.SubType, "장치") if caps else "장치"; label += f" [{subtype_name}]"
            else: label += " (미연결)"
            self.cmb_xinput_device.addItem(label, userData=idx)
        if current_selection is not None: self.cmb_xinput_device.setCurrentIndex(current_selection)
        
        self.toggle_measure_button.setEnabled(any_connected)
        self.update_start_button_state()


    def auto_save_report(self, data_ns: List[int]):
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        dev_text = self.cmb_xinput_device.currentText(); sanitized_name = "".join(c for c in dev_text if c.isalnum() or c in " _-").replace("__", "_").strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S'); filename = f"Report_{sanitized_name}_{timestamp}.txt"; path = os.path.join(base_path, filename)
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
        ms = [x / 1_000_000.0 for x in intervals_ns]; mu = mean(ms)
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

    @Slot(str)
    def show_update_dialog(self, new_version: str):
        msg_box = QMessageBox(self); msg_box.setWindowTitle("업데이트 알림")
        msg_box.setText(f"새로운 버전 {new_version}을(를) 사용할 수 있습니다.\n다운로드 페이지로 이동하시겠습니까?"); msg_box.setIcon(QMessageBox.Information)
        update_button = msg_box.addButton("업데이트", QMessageBox.ActionRole); cancel_button = msg_box.addButton("나중에", QMessageBox.RejectRole)
        msg_box.exec()
        if msg_box.clickedButton() == update_button: webbrowser.open("[https://github.com/deuxdoom/GamePadTester/releases](https://github.com/deuxdoom/GamePadTester/releases)")

    def show_about_dialog(self):
        about = AboutDialog(self); about.exec()

    def closeEvent(self, event):
        self.stop_measure(); super().closeEvent(event)

class AboutDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("정보")
        self.setFixedSize(400, 280)
        layout = QVBoxLayout(self); layout.setSpacing(15); layout.setContentsMargins(20, 20, 20, 20)
        icon_label = QLabel(); pixmap = _load_app_pixmap()
        if pixmap: icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter); layout.addWidget(icon_label)
        title_label = QLabel(f"게임패드 테스터 v{VERSION}"); title_label.setObjectName("TitleLabel"); title_label.setAlignment(Qt.AlignCenter); layout.addWidget(title_label)
        desc_label = QLabel("XInput 컨트롤러의 폴링레이트, 버튼, 스틱, 진동을 테스트하는 프로그램입니다."); desc_label.setWordWrap(True); desc_label.setAlignment(Qt.AlignCenter); layout.addWidget(desc_label)
        layout.addStretch(1)
        github_button = QPushButton("GitHub 방문"); github_button.clicked.connect(lambda: webbrowser.open("[https://github.com/deuxdoom/GamePadTester](https://github.com/deuxdoom/GamePadTester)")); layout.addWidget(github_button)

_temp_icon_path = None
def _cleanup_temp_icon():
    global _temp_icon_path
    if _temp_icon_path and os.path.exists(_temp_icon_path):
        try: os.remove(_temp_icon_path)
        except Exception as e: print(f"임시 아이콘 파일 삭제 실패: {e}")

def _load_app_pixmap() -> Optional[QPixmap]:
    global _temp_icon_path
    try:
        data = base64.b64decode(ICON_BASE64)
        if _temp_icon_path is None or not os.path.exists(_temp_icon_path):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(data)
                _temp_icon_path = f.name
            atexit.register(_cleanup_temp_icon)
        
        pixmap = QPixmap(_temp_icon_path)
        return pixmap
    except Exception as e:
        print(f"아이콘 로드 실패: {e}")
        return None

def main():
    if os.name != "nt": print("이 프로그램은 Windows(XInput) 전용입니다."); return
    app = QApplication(sys.argv); app.setStyleSheet(STYLESHEET)
    
    pixmap = _load_app_pixmap()
    app_icon = QIcon(pixmap) if pixmap else QIcon()
    app.setWindowIcon(app_icon)
    
    w = MainWindow()
    w.setWindowIcon(app_icon)
    
    w.show(); sys.exit(app.exec())

if __name__ == "__main__":
    main()
