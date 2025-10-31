import streamlit as st
import time
import random
from copy import deepcopy

# -----------------
# 1. 초기 세션 상태 및 데이터 설정
# -----------------

# 세션 상태가 초기화되지 않았을 때만 초기화
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.player_name = ""
    st.session_state.location = 'village'
    
    # 인벤토리 (슬라임의 점액 추가)
    st.session_state.inventory = {'밀': 0, '슬라임의 점액': 0}

    # 스탯 초기화
    st.session_state.stats = {
        'HP': 10,
        'STR': 3,
        'DEX': 5,
        'MP': 5,
        'MANA': 0
    }
    
    # 레벨, 경험치, 명성 초기화
    st.session_state.level = 1
    st.session_state.exp = 0
    st.session_state.fame = 0 # 📌 명성 추가

    st.session_state.player_class = "농노 (Peasant)"
    st.session_state.is_combat_active = False
    st.session_state.enemy = None
    st.session_state.combat_log = []

# 몬스터 데이터 정의
ENEMIES = {
    "Slime": {
        "HP": 10,
        "STR": 2, 
        "DEX": 3,
        "NAME": "LV.1 슬라임",
        "EXP_REWARD": 1,
        "ITEM_REWARD": "슬라임의 점액" # 📌 아이템 보상 정의
    }
}

# -----------------
# 2. 유틸리티 함수 및 사이드바
# -----------------

def start_game():
    """사용자가 '모험 시작' 버튼을 누르면 호출됩니다."""
    # 📌 이름이 비어 있는지 확인 (st.session_state.player_name은 text_input의 key로 자동 업데이트됨)
    if not st.session_state.player_name.strip():
        st.warning("캐릭터 이름을 입력해야 합니다.")
        return
    st.session_state.game_started = True
    st.session_state.location = 'village' 

def go_to_location(location_name):
    """현재 위치 상태를 변경하고 화면을 갱신합니다."""
    st.session_state.location = location_name

def harvest_wheat():
    """밀을 수확하고 인벤토리를 업데이트합니다. 3초의 딜레이를 추가합니다."""
    
    with st.spinner('🌾 열심히 밀을 수확하는 중입니다... (3초 소요)'):
        time.sleep(3) 
        
    st.session_state.inventory['밀'] += 1
    st.success(f"✅ 밀 1개를 수확했습니다! (총 {st.session_state.inventory['밀']}개)")
    st.rerun() 

def display_sidebar():
    """게임 사이드바를 표시하여 인벤토리와 기본 정보를 보여줍니다."""
    st.sidebar.title("캐릭터 정보")
    st.sidebar.text(f"이름: {st.session_state.player_name}")
    st.sidebar.text("신분: 농노")
    
    # 레벨, 경험치, 명성 표시
    st.sidebar.text(f"레벨: {st.session_state.level}")
    st.sidebar.text(f"경험치: {st.session_state.exp}")
    st.sidebar.text(f"명성: {st.session_state.fame}") # 📌 명성 표시
    
    st.sidebar.markdown("---")
    
    # 캐릭터 스탯 표시 (순서 변경 및 영어 제거)
    st.sidebar.subheader("능력치")
    st.sidebar.text(f"체력: {st.session_state.stats['HP']}")
    st.sidebar.text(f"힘: {st.session_state.stats['STR']}")
    st.sidebar.text(f"민첩: {st.session_state.stats['DEX']}")
    st.sidebar.text(f"정신력: {st.session_state.stats['MP']}")
    st.sidebar.text(f"마나: {st.session_state.stats['MANA']}")
    
    st.sidebar.markdown("---")
    
    st.sidebar.title("💰 인벤토리")
    # 인벤토리 항목을 키를 기준으로 정렬하여 표시 (밀 -> 점액 순)
    for item in sorted(st.session_state.inventory.keys()):
        count = st.session_state.inventory[item]
        st.sidebar.write(f"- {item}: **{count}**개")
        
    st.sidebar.markdown("---")
    # 게임 초기화 버튼
    if st.sidebar.button("<< 게임 초기화"):
        # 초기화 로직 (session_state를 삭제하는 대신, 초기값으로 재설정)
        keys_to_reset = ['game_started', 'player_name', 'location', 'inventory', 'stats', 
                         'level', 'exp', 'fame', 'is_combat_active', 'enemy', 'combat_log']
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        # 강제 재실행을 통해 초기 세션 상태 설정 블록이 다시 실행되도록 유도
        st.rerun() 

# -----------------
# 3. 전투 시스템 함수 (Combat Logic)
# -----------------

def get_slime_loot():
    """슬라임 점액 보상을 확률에 따라 계산합니다."""
    rand = random.random() # 0.0 이상 1.0 미만의 난수
    
    if rand < 0.6: # 60% 확률
        return 1
    elif rand < 0.9: # 30% 확률 (0.6 ~ 0.9)
        return 2
    else: # 10% 확률 (0.9 ~ 1.0)
        return 3

def start_combat(enemy_type):
    """지정된 몬스터와의 전투를 시작합니다."""
    st.session_state.is_combat_active = True
    st.session_state.location = 'combat'
    
    enemy_base_stats = ENEMIES[enemy_type]
    st.session_state.enemy = deepcopy({
        "type": enemy_type,
        "name": enemy_base_stats["NAME"],
        "HP": enemy_base_stats["HP"],
        "STR": enemy_base_stats["STR"],
        "DEX": enemy_base_stats["DEX"],
        "MAX_HP": enemy_base_stats["HP"],
        "EXP_REWARD": enemy_base_stats["EXP_REWARD"],
        "ITEM_REWARD": enemy_base_stats["ITEM_REWARD"]
    })
    
    st.session_state.combat_log = [f"**⚔️ {st.session_state.enemy['name']}**과의 전투가 시작되었습니다!"]
    
    player_dex = st.session_state.stats['DEX']
    enemy_dex = st.session_state.enemy['DEX']
    
    if player_dex >= enemy_dex:
        st.session_state.combat_log.append("당신의 민첩이 더 높아 선제 공격 권한을 얻었습니다! 먼저 행동하세요.")
    else:
        st.session_state.combat_log.append(f"{st.session_state.enemy['name']}의 민첩({enemy_dex})이 당신({player_dex})보다 높아 선제 공격을 시작합니다!")
        enemy_turn()

def player_attack():
    """플레이어가 몬스터를 공격합니다."""
    
    player_str = st.session_state.stats['STR']
    enemy = st.session_state.enemy
    
    damage = random.randint(1, player_str)
    enemy['HP'] = max(0, enemy['HP'] - damage)
    st.session_state.combat_log.append(f"**{st.session_state.player_name}**이(가) **{enemy['name']}**에게 **{damage}**의 피해를 입혔습니다. (남은 HP: {enemy['HP']})")
    
    # 전투 승리 체크
    if enemy['HP'] <= 0:
        end_combat("win")
        return
    
    # 플레이어 공격 후, 몬스터 턴 실행
    enemy_turn()
    
def enemy_turn():
    """몬스터가 플레이어를 공격합니다."""
    
    enemy = st.session_state.enemy
    
    if enemy['HP'] <= 0:
        return
        
    enemy_str = enemy['STR']
    
    damage = random.randint(1, enemy_str)
    st.session_state.stats['HP'] = max(0, st.session_state.stats['HP'] - damage)
    st.session_state.combat_log.append(f"**{enemy['name']}**이(가) 당신에게 **{damage}**의 피해를 입혔습니다. (남은 HP: {st.session_state.stats['HP']})")
    
    # 전투 패배 체크
    if st.session_state.stats['HP'] <= 0:
        end_combat("lose")
        return

def end_combat(result):
    """전투를 종료하고 결과를 처리합니다."""
    st.session_state.is_combat_active = False
    
    if result == "win":
        st.session_state.combat_log.append("🎉 **전투에서 승리했습니다!** 🎉")
        
        # 경험치 획득 로직
        exp_gain = st.session_state.enemy["EXP_REWARD"]
        st.session_state.exp += exp_gain
        st.session_state.combat_log.append(f"🌟 경험치 {exp_gain}을 획득했습니다! (총 {st.session_state.exp})")
        
        # 📌 명성 획득 로직
        st.session_state.fame += 1
        st.session_state.combat_log.append(f"👑 명성 +1을 획득했습니다! (총 {st.session_state.fame})")
        
        # 📌 슬라임의 점액 보상 로직
        if st.session_state.enemy["type"] == "Slime":
            item_name = st.session_state.enemy["ITEM_REWARD"]
            item_count = get_slime_loot()
            st.session_state.inventory[item_name] += item_count
            st.session_state.combat_log.append(f"🧪 보상: {item_name} {item_count}개를 획득했습니다.")
        
    elif result == "lose":
        st.session_state.combat_log.append("💀 **전투에서 패배했습니다...** 💀")
        st.session_state.combat_log.append("당신은 정신을 잃고 마을로 돌아왔습니다.")
    
    go_to_location('village')

# -----------------
# 4. 화면 구성 함수 (각 위치별 화면)
# -----------------

def character_setup_screen():
    """게임 시작 전 캐릭터 이름 설정을 위한 화면입니다."""
    st.title("📜 감동적인 RPG: 여정의 시작") # 📌 타이틀 수정
    st.markdown("---")
    st.header("귀하의 이름을 입력해 주십시오.")

    # 📌 이름 입력 필드: key를 사용하여 st.session_state에 직접 연결
    st.text_input("이름", 
                  key='player_name',
                  placeholder="예: 존, 마리아...")

    st.markdown("---")

    st.button("⚔️ 모험 시작!", on_click=start_game, use_container_width=True)


def village_screen():
    """마을 (메인 게임 화면)"""
    st.title("🏘️ 고난의 마을")
    st.header("여정의 서막: 고난의 시작")
    st.markdown("---")
    
    st.write(f"**{st.session_state.player_name}** 님, 당신은 변변찮은 농노의 삶을 살고 있습니다. 주변에는 힘겹게 일하는 마을 사람들의 모습이 보입니다.")
    
    if st.session_state.combat_log:
        with st.expander("지난 모험 기록 보기"):
            for log in st.session_state.combat_log:
                st.markdown(log)
            if st.button("로그 초기화"):
                st.session_state.combat_log = []
                st.rerun()
                
    st.markdown("---")
    st.subheader("어디로 가시겠습니까?")

    st.button("🚜 농장으로 이동", on_click=go_to_location, args=('farm',), use_container_width=True)
    st.button("⚔️ 던전 가기", on_click=go_to_location, args=('dungeon_select',), use_container_width=True)
    st.button("🏠 집으로 돌아가기 (휴식)", disabled=True, use_container_width=True)


def farm_screen():
    """농장 화면"""
    st.title("🌾 공동 농장")
    st.header("밀을 수확할 시간입니다.")
    st.markdown("---")
    
    st.write("황무지 같은 밭에는 당신이 오늘 수확해야 할 밀들이 힘없이 서 있습니다.")
    st.write(f"현재 당신의 노고로 모인 밀: **{st.session_state.inventory['밀']}**개")
    
    st.markdown("---")
    
    st.button("🌾 밀 수확하기 (노동)", on_click=harvest_wheat, use_container_width=True)
    
    st.markdown("---")
    
    st.button("🏠 마을로 돌아가기", on_click=go_to_location, args=('village',), use_container_width=True)


def dungeon_select_screen():
    """던전 선택 화면"""
    st.title("⚔️ 던전 선택")
    st.header(f"**{st.session_state.player_name}** 님, 어디로 떠나시겠습니까?")
    st.markdown("---")
    
    st.write("마을 근처에서 모험을 시작할 수 있는 장소 목록입니다.")
    
    st.markdown("---")
    
    if st.button("미약한 초원의 들판 (LV.1 슬라임 등장)", key='field_dungeon', use_container_width=True):
        start_combat("Slime") 
        st.rerun() 
            
    st.markdown("---")
    st.button("🏠 마을로 돌아가기", on_click=go_to_location, args=('village',), use_container_width=True)


def combat_screen():
    """전투 진행 화면"""
    enemy = st.session_state.enemy
    
    st.title(f"🔥 전투 중: {enemy['name']}")
    st.markdown("---")
    
    # 몬스터 상태 표시 (체력바는 편의 기능으로 유지)
    st.subheader(f"몬스터: {enemy['name']}")
    hp_percent = (enemy['HP'] / enemy['MAX_HP']) if enemy['MAX_HP'] > 0 else 0
    st.progress(hp_percent, text=f"HP: {enemy['HP']} / {enemy['MAX_HP']}")
    st.text(f"힘(공격력): {enemy['STR']} | 민첩(공격속도): {enemy['DEX']}")
    
    st.markdown("---")
    
    # 전투 기록 표시
    st.subheader("전투 기록")
    for log in st.session_state.combat_log:
        st.markdown(log)
    
    st.markdown("---")
    
    # 플레이어 행동 선택
    st.subheader("당신의 행동")
    
    if st.button(f"⚔️ 공격 (피해량: 1~{st.session_state.stats['STR']})", use_container_width=True):
        player_attack()
        st.rerun()

    st.button("🛡️ 방어 (미구현)", disabled=True, use_container_width=True)
    st.button("🏃‍♂️ 도망치기 (미구현)", disabled=True, use_container_width=True)


# -----------------
# 5. 메인 루프 (화면 분기)
# -----------------

def main_game_loop():
    """게임 상태 및 위치 상태에 따라 적절한 화면을 보여줍니다."""
    
    if st.session_state.game_started:
        display_sidebar()
        
        if st.session_state.is_combat_active:
            combat_screen() 
        elif st.session_state.location == 'village':
            village_screen()
        elif st.session_state.location == 'farm':
            farm_screen()
        elif st.session_state.location == 'dungeon_select':
            dungeon_select_screen()

    else:
        character_setup_screen()

# -----------------
# 6. 앱 실행
# -----------------
main_game_loop()
