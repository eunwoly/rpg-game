import streamlit as st
import time

# -----------------
# 1. 초기 세션 상태 설정
# -----------------

if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""

# 새로운 상태: 현재 위치 (기본값: 'village')
if 'location' not in st.session_state:
    st.session_state.location = 'village'
# 새로운 상태: 인벤토리 (밀 0개로 시작)
if 'inventory' not in st.session_state:
    st.session_state.inventory = {'밀': 0}

# 직업 고정 (플레이어에게는 비공개)
st.session_state.player_class = "농노 (Peasant)"


# -----------------
# 2. 유틸리티 함수 및 사이드바
# -----------------

def start_game():
    """사용자가 '모험 시작' 버튼을 누르면 호출됩니다."""
    # 이름이 비어 있는지 확인
    if not st.session_state.player_name.strip():
        st.warning("캐릭터 이름을 입력해야 합니다.")
        return
    st.session_state.game_started = True
    st.session_state.location = 'village'  # 게임 시작 시 마을로 설정


def go_to_location(location_name):
    """현재 위치 상태를 변경하고 화면을 갱신합니다."""
    st.session_state.location = location_name


def harvest_wheat():
    """밀을 수확하고 인벤토리를 업데이트합니다. 3초의 딜레이를 추가합니다."""

    # 3초 동안 로딩 스피너를 보여주며 딜레이를 만듭니다.
    with st.spinner('🌾 열심히 밀을 수확하는 중입니다... (3초 소요)'):
        time.sleep(3)  # 3초 동안 실행을 멈춥니다.

    st.session_state.inventory['밀'] += 1
    # 딜레이가 끝난 후 성공 메시지를 표시합니다.
    st.success(f"✅ 밀 1개를 수확했습니다! (총 {st.session_state.inventory['밀']}개)")
    st.rerun()  # 수확 메시지 후 화면을 강제로 새로고침하여 스피너 잔상 제거 및 인벤토리 업데이트


def display_sidebar():
    """게임 사이드바를 표시하여 인벤토리와 기본 정보를 보여줍니다."""
    st.sidebar.title("캐릭터 정보")
    st.sidebar.text(f"이름: {st.session_state.player_name}")
    st.sidebar.text("신분: 농노")
    st.sidebar.markdown("---")

    st.sidebar.title("💰 인벤토리")
    # 인벤토리 딕셔너리를 순회하며 아이템 목록을 표시합니다.
    for item, count in st.session_state.inventory.items():
        st.sidebar.write(f"- {item}: **{count}**개")

    st.sidebar.markdown("---")
    # 게임 초기화 버튼
    if st.sidebar.button("<< 게임 초기화"):
        st.session_state.game_started = False
        st.session_state.player_name = ""
        st.session_state.location = 'village'
        st.session_state.inventory = {'밀': 0}
        st.rerun()


# -----------------
# 3. 화면 구성 함수 (각 위치별 화면)
# -----------------

def village_screen():
    """마을 (메인 게임 화면)"""
    st.title("🏘️ 고난의 마을")
    st.header("여정의 서막: 고난의 시작")
    st.markdown("---")

    st.write(f"**{st.session_state.player_name}** 님, 당신은 변변찮은 농노의 삶을 살고 있습니다. 주변에는 힘겹게 일하는 마을 사람들의 모습이 보입니다.")

    st.markdown("---")
    st.subheader("어디로 가시겠습니까?")

    # '농장' 버튼
    st.button("🚜 농장으로 이동", on_click=go_to_location, args=('farm',), use_container_width=True)
    st.button("🏪 상점으로 이동 (미구현)", disabled=True, use_container_width=True)  # 다음 목표를 위해 추가
    st.button("🏠 집으로 돌아가기 (휴식)", disabled=True, use_container_width=True)


def farm_screen():
    """농장 화면"""
    st.title("🌾 공동 농장")
    st.header("밀을 수확할 시간입니다.")
    st.markdown("---")

    st.write("황무지 같은 밭에는 당신이 오늘 수확해야 할 밀들이 힘없이 서 있습니다.")
    st.write(f"현재 당신의 노고로 모인 밀: **{st.session_state.inventory['밀']}**개")

    st.markdown("---")

    # '밀 수확하기' 버튼: on_click 시 harvest_wheat 함수 호출
    # 이 버튼을 누르면 3초 딜레이가 발생합니다.
    st.button("🌾 밀 수확하기 (노동)", on_click=harvest_wheat, use_container_width=True)

    st.markdown("---")

    # '마을로 돌아가기' 버튼
    st.button("🏠 마을로 돌아가기", on_click=go_to_location, args=('village',), use_container_width=True)


def character_setup_screen():
    """게임 시작 전 캐릭터 이름 설정을 위한 화면입니다."""
    st.title("📜 중세 텍스트 RPG: 여정의 시작")
    st.markdown("---")
    st.header("당신의 이름을 입력하십시오.")

    st.text_input("이름",
                  value=st.session_state.player_name,
                  key='player_name',
                  placeholder="예: 존, 마리아...")

    st.markdown("---")

    st.button("⚔️ 모험 시작!", on_click=start_game, use_container_width=True)


# -----------------
# 4. 메인 루프 (화면 분기)
# -----------------

def main_game_loop():
    """게임 상태 및 위치 상태에 따라 적절한 화면을 보여줍니다."""

    if st.session_state.game_started:
        # 게임이 시작되면 사이드바(인벤토리)를 표시합니다.
        display_sidebar()

        # 현재 위치에 따라 화면을 분기합니다.
        if st.session_state.location == 'village':
            village_screen()
        elif st.session_state.location == 'farm':
            farm_screen()

    else:
        # 게임이 시작되지 않았다면 캐릭터 설정 화면을 보여줍니다.
        character_setup_screen()


# -----------------
# 5. 앱 실행
# -----------------
main_game_loop()