<p align="center">
  <img src="icon.png" width="256" alt="GamePadTester icon" />
</p>
<h1 align="center">GamePadTester</h1>
<p align="center">
  <a href="https://github.com/deuxdoom/GamePadTester/releases"><img src="https://img.shields.io/github/v/release/deuxdoom/GamePadTester?logo=github" alt="release"/></a>
  <a href="https://github.com/deuxdoom/GamePadTester/blob/main/LICENSE"><img src="https://img.shields.io/github/license/deuxdoom/GamePadTester" alt="license"/></a>
  <img src="https://img.shields.io/badge/OS-Windows-0078D6?logo=windows" alt="os"/>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python" alt="python"/>
  <img src="https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt" alt="pyside6"/>
  <a href="https://github.com/deuxdoom/GamePadTester/releases"><img src="https://img.shields.io/github/downloads/deuxdoom/GamePadTester/total?logo=github" alt="downloads"/></a>
</p>

> 윈도우용 XInput 게임패드 테스터: 폴링레이트 측정, D-Pad/ABXY/LB RB 등 버튼 테스트, 스틱 원형도 Axis값 측정, 진동 테스트

---

## 📘 프로그램 설명
**GamePadTester**는 XInput 기반 컨트롤러의 입력 변화를 고속 샘플링해 폴링 특성을 수치화하고, 버튼·스틱·트리거 상태를 직관적인 GUI로 시각화합니다. 

## ✨ 핵심 기능
- **폴링레이트 분석**: 평균/중앙값(Hz·ms), 안정도(%), 샘플 수(1000/2000/4000) 선택
- **버튼 시각화**: D-Pad와 ABXY를 비롯해 각종 패드 버튼 **LB/RB / OPTION(≡)·MENU(⁝) / L3·R3** 상태 표시
- **스틱 원형도**: 좌·우 스틱의 원형 움직임 분포 및 **Avg Error %**로 균일성 점검
- **진동 테스트**: 좌/우(저주파/고주파) 모터 강도 슬라이더 + 온/오프 토글
- **결과 저장**: 폴링레이트 결과값을 측정 종료시 자동으로 **TXT**로 저장
- **장치명 표시**: `pygame`을 통해 장치명 표시(추정)

## ⚠️ 주의 사항
- **대상 OS/장치**: Windows 10/11, XInput 호환 컨트롤러(예: Xbox Series/One 패드, 일부 호환 제품)
- **SmartScreen 경고(서명 미적용 EXE)**: 실행 시 “Windows에서 PC를 보호함”이 뜰 수 있습니다. 신뢰 가능한 출처에서 받은 파일임을 확인한 뒤, **`추가 정보` → `실행`**을 선택하세요. 다운로드한 파일의 `속성`에서 **차단 해제** 체크 후 실행하면 경고가 줄어듭니다.
- **백신 오탐 가능성**: 자체 빌드/압축 방식에 따라 간헐적 오탐이 있을 수 있습니다. **Releases 페이지**의 배포본 사용을 권장하며, 필요 시 해시값(SHA-256)으로 무결성을 확인하세요.
- **관리자 권한**: 일반 사용자 권한으로 동작합니다. 특정 드라이버/무선 동글 환경에선 진동 기능이 제한될 수 있습니다.

## 🔗 참고
- XInput 샘플/아이디어
  - https://github.com/chrizonix/XInputTest
  - https://github.com/cakama3a/Polling

## 🙏 크레딧
- 아이콘: <a href="https://www.flaticon.com/free-icon/game-control_1722368">Game control</a> by <a href="https://www.flaticon.com/authors/freepik">Freepik</a> from <a href="https://www.flaticon.com/">Flaticon</a>. 이 아이콘은 Flaticon 라이선스에 따라 사용되며, 출처 표기가 필요합니다.

## 📄 라이선스
[LICENSE](LICENSE) 참고.
