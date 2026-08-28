# -*- coding: utf-8 -*-
"""index.html(한국어)에서 en.html(영어)을 생성한다.
사용법: python tools/build-en.py
번역은 아래 T 테이블(긴 문자열 우선 적용)로 단순 치환한다.
새 한국어 문자열을 추가했다면 이 테이블에도 추가한 뒤 다시 실행할 것.
남은 한글이 주석 이외에서 발견되면 경고를 출력한다."""
import io, os, re, sys

SRC = os.path.join(os.path.dirname(__file__), '..', 'index.html')
DST = os.path.join(os.path.dirname(__file__), '..', 'en.html')

T = {
  # ---- 메타/타이틀 ----
  '부장님이 잠드셨다 v0.7.0': "DON’T DROP HIM v0.7.0",
  '부장님이 잠드셨다 — 30개 고유 맵 캠페인': "DON’T DROP HIM — 30 unique map campaign",
  '부장님이 잠드셨다': "DON’T DROP HIM",
  '회식엔딩': 'AFTER-WORK',
  '만취해 잠든 부장님을 둘이서 들고 집까지 배달하는 눈치 게임. 깨우는 순간, 월요일이 지옥이 된다.': 'Carry your blackout-drunk boss home without waking him. The moment he wakes, Monday becomes hell.',
  'v0.7.0 — 420m부터 900m까지, 30개 고유 지형 PC·모바일 캠페인': 'v0.7.0 — 420m to 900m, 30 unique maps, PC & mobile',
  '[V] 실제 마이크 ': '[V] Real microphone ',
  ' (선택 기능 · 기본 OFF)': ' (optional · default OFF)',
  '🌐 English': '🌐 한국어',
  "location.href='./en.html'": "location.href='./index.html'",
  '[1]  혼자': '[1]  Solo',
  '[2]  둘이서': '[2]  Local 2P',
  '🌐 [3]  온라인': '🌐 [3]  Online',
  '👆 혼자': '👆 Solo',
  '👆 둘이서': '👆 Local 2P',
  '왼손=뒷사람(WASD+F) · 오른손=앞사람(방향키+Shift/L)': 'Left hand = Back (WASD+F) · Right = Front (Arrows+Shift/L)',
  '키보드 반씩 나눠 잡기 · 서로 탓할 준비 필수': 'Share one keyboard · Prepare to blame each other',
  '공개 방 목록에서 골라 원격 2인 협동': 'Pick a public room, play co-op remotely',
  '양쪽 엄지로 두 사람을 동시에 조작': 'Both thumbs control both carriers',
  '화면 양쪽을 한 사람씩 맡아 조작': 'One player per half of the screen',
  '간판 아래선 숙이고(대신 부장님이 끌린다), 턱에선 둘이 박자 맞춰 점프. 고양이 앞에선 천천히.': 'Crouch under signs (the Boss drags), jump ledges in sync. Go slow near the cat.',
  '🟦 뒷사람 정보': '🟦 Back carrier',
  '🟩 앞사람 정보': '🟩 Front carrier',
  '🟦 뒷사람': '🟦 Back',
  '🟩 앞사람': '🟩 Front',
  'A / D 이동     W 점프     S 숙이기     F 그립 잡기·놓기': 'A / D move     W jump     S crouch     F grip / release',
  '← / → 이동     ↑ 점프     ↓ 숙이기     Shift(양쪽) 또는 L 그립 잡기·놓기': '← / → move     ↑ jump     ↓ crouch     Shift (either) or L grip / release',
  '왼쪽 파란 스틱     좌우로 밀어 이동 · 위로 점프 · 아래로 숙이기 · 그립 버튼': 'Left blue stick — push to move, up to jump, down to crouch · Grip button',
  '오른쪽 초록 스틱   좌우로 밀어 이동 · 위로 점프 · 아래로 숙이기 · 그립 버튼': 'Right green stick — push to move, up to jump, down to crouch · Grip button',

  # ---- 터치 UI / DOM ----
  '📱 가로로 돌리면 더 편하게 플레이할 수 있습니다': '📱 Rotate to landscape for a better view',
  '뒷사람 스틱: 밀어서 이동, 위로 점프, 아래로 숙이기': 'Back stick: push to move, up to jump, down to crouch',
  '앞사람 스틱: 밀어서 이동, 위로 점프, 아래로 숙이기': 'Front stick: push to move, up to jump, down to crouch',
  '뒷사람 그립': 'Back grip',
  '앞사람 그립': 'Front grip',
  '모바일 게임 조작부': 'Mobile controls',
  '그립': 'GRIP',

  # ---- 온라인 로비 ----
  '🌐 온라인 협동': '🌐 Online Co-op',
  '중계 서버 주소 (Cloudflare Worker)': 'Relay server address (Cloudflare Worker)',
  '방 이름 (예: 부장님 구조대)': 'Room name (e.g. Boss Rescue Squad)',
  '방 만들기': 'Create room',
  '열린 방 목록': 'Open rooms',
  '게임 시작': 'Start game',
  '닫기 / 나가기': 'Close / Leave',
  '입장': 'Join',
  '서버 주소를 입력하면 방 목록이 표시됩니다': 'Enter a server address to see rooms',
  '열린 방이 없습니다 — 첫 방을 만들어보세요!': 'No open rooms — create the first one!',
  '빈 방': 'Empty slot',
  '방 목록을 불러올 수 없습니다 — 서버 주소를 확인하세요': "Can’t load rooms — check the server address",
  '서버 주소를 먼저 입력하세요 (wss://…workers.dev)': 'Enter the server address first (wss://…workers.dev)',
  '방 만드는 중…': 'Creating room…',
  '서버에 연결할 수 없습니다 — 잠시 후 다시 시도해주세요': 'Cannot reach the server — try again shortly',
  '서버에 연결할 수 없습니다: ': "Can’t reach the server: ",
  '주소가 올바르지 않습니다': 'Invalid address',
  '접속 중…': 'Connecting…',
  '접속됨 · 상대를 기다리는 중': 'Connected · waiting for a partner',
  '접속 실패 — 서버 주소와 방 코드를 확인하세요': 'Connection failed — check the server address',
  '연결이 끊어졌습니다': 'Connection lost',
  '상대가 나갔습니다 — 대기 중…': 'Partner left — waiting…',
  '부장님 운반조 ': 'Boss Carry Crew ',
  '플레이어 ': 'Player ',
  ' (나)': ' (you)',
  '역할 미정': 'no role yet',
  '상대 대기 중… 로비 목록에 이 방이 공개되어 있습니다': 'Waiting for a partner… this room is listed in the public lobby',
  '2명이 역할을 고르면 시작': 'Start when both pick roles',
  '방장이 시작하길 기다리는 중…': 'Waiting for the host to start…',
  '역할을 선택하세요': 'Pick your role',
  '대기 중…': 'Waiting…',
  '🌐 온라인 협동 시작 — 나는 ': "🌐 Online co-op — I’m the ",
  ' (방장)': ' (host)',
  '방에서 나감': 'Left the room',

  # ---- 이탈 모달 ----
  '⚠ 상대방이 이탈했습니다': '⚠ Your partner left',
  '진행 상황은 그대로 남아 있습니다. 어떻게 할까요?': 'Your progress is intact. What now?',
  '서버와의 연결이 끊어졌습니다. 진행 상황은 그대로 남아 있습니다.': 'Lost connection to the server. Your progress is intact.',
  '🕹 혼자 이어하기 (양쪽 조작)': '🕹 Continue solo (both roles)',
  '👥 새 상대 기다리기 (방 다시 공개)': '👥 Wait for a new partner (relist room)',
  '⌂ 타이틀로': '⌂ Back to title',
  '🔌 서버와 연결이 끊어졌습니다': '🔌 Lost connection to the server',
  '👋 상대방이 게임을 이탈했습니다': '👋 Your partner left the game',
  '🕹 혼자 이어하기 — 왼손 뒷사람(WASD+F), 오른손 앞사람(방향키+Shift/L)': '🕹 Continuing solo — left hand Back (WASD+F), right hand Front (Arrows+Shift/L)',
  '방이 다시 공개되었습니다 — 새 상대를 기다리는 중 (시작하면 LEVEL ': 'Room relisted — waiting for a new partner (restart begins at LEVEL ',
  '부터)': ')',

  # ---- 레벨 이름 ----
  '회식 탈출': 'Dinner Escape', '골목의 턱': 'Alley Ledges', '간판 지옥': 'Signboard Hell',
  '고양이 골목': 'Cat Alley', '숙취 육교': 'Hangover Overpass', '택시 거부': 'Taxi Refusal',
  '새벽 세 시': '3 A.M.', '인사평가 전야': 'Review Eve', '임원 관문': 'Executive Gate',
  '월요일 예행연습': 'Monday Rehearsal', '막차 끊김': 'Last Train Gone', '편의점 불빛': 'Convenience Glow',
  '공사장 우회': 'Construction Detour', '배달 오토바이': 'Delivery Bikes', '경찰 검문': 'Police Checkpoint',
  '비상계단': 'Fire Stairs', '취객의 합창': 'Drunken Chorus', '폭우 전조': 'Coming Storm',
  '새벽 시장': 'Dawn Market', '강남대로 결승': 'Gangnam Finals', '대리기사 실종': 'Missing Driver',
  '지하도 역풍': 'Underpass Wind', '인사팀 전화': 'HR Call', '회장님 목격': 'Chairman Sighting',
  '동틀 무렵': 'Daybreak', '월요일 출근길': 'Monday Commute', '감사팀 관문': 'Audit Gate',
  '승진 심사대': 'Promotion Board', '대표이사 앞': "CEO’s Doorstep", '전설의 귀가': 'Legendary Homecoming',

  # ---- 레벨 설명 ----
  '원본 귀갓길. 기본기를 익히세요.': 'The original walk home. Learn the basics.',
  '낮은 턱이 운반 박자를 흔듭니다.': 'Low ledges break your carrying rhythm.',
  '낮은 천장과 단차가 동시에 옵니다.': 'Low ceilings and steps hit at once.',
  '속도를 내면 사고가 연쇄됩니다.': 'Speed turns mistakes into chain accidents.',
  '오르막과 천장이 그립을 뜯어냅니다.': 'Climbs and ceilings tear at your grip.',
  '회복 구간이 줄고 뒤척임이 빨라집니다.': 'Fewer safe zones, faster tossing.',
  '부장님이 얕은 잠에서 시작합니다.': 'The Boss starts in light sleep.',
  '실수 한 번이 숙면도를 크게 깎습니다.': 'One mistake carves deep into his sleep.',
  '체크포인트는 출발점 하나뿐입니다.': 'Only one checkpoint: the start.',
  '첫 번째 관문. 이제 진짜 귀가가 시작됩니다.': 'First gate. The real trip home begins.',
  '택시도 막차도 없습니다. 발밑만 믿으세요.': 'No taxi, no train. Trust your feet.',
  '좁은 통로에서 부장님이 더 자주 뒤척입니다.': 'He tosses more in narrow passages.',
  '턱과 자재가 안전한 보폭을 빼앗습니다.': 'Ledges and debris steal your footing.',
  '급하게 움직일수록 손이 더 빨리 미끄러집니다.': 'The faster you rush, the faster hands slip.',
  '낮은 구조물 아래에서 호흡을 맞추세요.': 'Sync your breathing under low structures.',
  '연속 단차가 앞뒤 사람의 박자를 시험합니다.': 'Stair chains test both carriers’ rhythm.',
  '소음 한 번이 연쇄 사고로 이어집니다.': 'One noise cascades into disaster.',
  '그립 한계가 줄어들어 짧게 잡아야 합니다.': 'Grip limit shrinks — hold in short bursts.',
  '골목 전체가 장애물이 되기 시작합니다.': 'The whole alley becomes an obstacle.',
  '두 번째 관문. 실수할 여유가 거의 없습니다.': 'Second gate. Almost no room for error.',
  '시작부터 얕은 잠입니다. 천천히 전진하세요.': 'Light sleep from the start. Move slowly.',
  '낮은 천장과 턱이 번갈아 덮칩니다.': 'Ceilings and ledges alternate endlessly.',
  '눈을 뜨는 구간이 길어지고 잦아집니다.': 'Eye-opening spells grow longer, more frequent.',
  '고양이 앞에서는 거의 멈춰야 합니다.': 'Near the cat you must almost stop.',
  '남은 숙면도와 시간이 동시에 줄어듭니다.': 'Sleep and time run out together.',
  '귀가 행렬과 출근 행렬이 충돌합니다.': 'Homebound meets the morning commute.',
  '작은 충격도 치명적입니다. 놓지 마세요.': "Even small impacts are fatal. Don’t let go.",
  '모든 구간에서 완벽한 합이 필요합니다.': 'Every section demands perfect sync.',
  '마지막 문턱. 한 번의 방심도 허용하지 않습니다.': 'The final threshold. Zero lapses allowed.',
  '30단계 최종전. 부장님을 집까지 배달하세요.': 'Stage 30 finale. Deliver the Boss home.',

  # ---- 테마 ----
  '회식 골목': 'Bar Alley', '공사 구간': 'Construction', '지하도': 'Underpass',
  '강남대로': 'Gangnam Blvd', '아파트 언덕': 'Apartment Hill', '명진마을': 'Myeongjin Village',
  '명진아파트 ': 'Myeongjin Apt ',

  # ---- 미션 ----
  '쉿!': 'Shh!', '소음을 3회 이하로': 'Keep noise to 3 or less', '소음 ≤ 3': 'Noise ≤ 3',
  '무사 귀환': 'Safe Return', '머리를 바닥에 부딪히지 않기': "Don’t bang his head", '머리 충격 0': 'Head hits 0',
  '빠른 귀가': 'Speedy Trip', '3분 안에 도착': 'Arrive within 3 minutes', '03:00 이내': 'Under 03:00',
  '공동 책임': 'Shared Blame', '과실 차이 10% 이하': 'Blame gap within 10%', '과실 차 ≤ 10%': 'Blame gap ≤ 10%',
  '철벽 경호': 'Iron Grip', '누구도 손을 놓지 않기': 'Nobody lets go', '그립 해제 0': 'Releases 0',
  '오늘의 미션 — ': "Tonight’s mission — ",
  '✓ 미션 성공  ': '✓ Mission complete  ',
  '✕ 미션 실패  ': '✕ Mission failed  ',

  # ---- 과실/구조 ----
  '손을 스스로 놓아버림': 'Let go on purpose', '무리하게 당겨 손이 미끄러짐': 'Overstretched and slipped',
  '낙하 충격 유발': 'Caused a fall impact', '부장님을 바닥에 끌고 다님': 'Dragged the Boss on the ground',
  '고양이를 놀라게 함': 'Startled the cat', '소주병을 걷어참': 'Kicked a soju bottle',
  '부장님을 길에 방치함': 'Abandoned the Boss', '고함으로 숙면을 방해함': 'Yelled him awake',
  '손놓음': 'Let go', '과신전': 'Overreach', '충격': 'Impact', '끌기': 'Dragging',
  '환경사고': 'Env. accident', '방치': 'Abandoned', '소음': 'Noise',
  '특이 혐의 없음': 'No notable charges',
  '혐의는 없으나 어쩐지 수상함': 'No charges, yet somehow suspicious',
  '앞사람 주요 혐의: ': 'Front carrier main charge: ',
  '기사회생': 'Clutch Save', '극한의 눈치': 'Nerves of Steel', '팀워크 구조': 'Teamwork Rescue',
  '눈치 만점': 'Perfect Read', '무음 통과': 'Silent Pass', '간발의 차': 'Narrow Escape',
  '함께 만든 기적': 'Miracle Together', '독박 운반': 'Solo Burden', '택시 탑승 성공': 'Taxi Boarded',
  '최장 단독 운반 ': 'Longest solo carry ',

  # ---- 수면 단계/보스 ----
  '숙면': 'Deep sleep', '얕은 잠': 'Light sleep', '반수면': 'Half-awake', '기상 직전': 'About to wake',
  '부장님 숙면도 · ': "Boss’s sleep · ",
  '머리': 'Head', '상체': 'Torso', '하체': 'Legs', '팔·어깨': 'Arms',
  '⚠ 사고 발생 · ': '⚠ Incident · ',
  '부장님 ': 'Boss ', ' 충돌': ' impact',

  # ---- 잠꼬대/기상 대사 ----
  '으음… 김대리… 그 보고서는…': 'Mmm… Kim… that report…',
  '한 잔만… 딱 한 잔만 더…': 'One more… just one more drink…',
  '우리 팀은… 가족이야…': 'Our team… is family…',
  '라떼는… 말이야…': 'Back in my day…',
  '으어… 2차… 2차 가야지…': 'Ugh… round two… round two…',
  '…내가 다 책임진다니까…': "…I’ll take full responsibility…",
  '야!! 여기가 어디야!!': 'HEY!! Where am I?!',
  '김대리… 자네 지금 뭐 하는 건가…': 'Kim… what exactly are you doing…',
  '내 구두!! 내 구두 어디 갔어!!': 'My shoes!! Where are my shoes?!',
  '자네들, 내일 아침에 보자.': 'You two. My office, tomorrow morning.',
  '이게 지금 몇 시야!!': 'What time is it right now?!',
  '으음… 시끄러…': 'Mmm… too loud…',
  '…읏, 시끄러…': '…ugh, noisy…',
  '으으음…': 'Mmmm…', '으윽…!': 'Urgh…!', '드르륵…': 'Rattle…', '데구르르!': 'Roll!',
  '부스럭…!!': 'Rustle…!!', '쿵!': 'Thud!',

  # ---- 이벤트/토스트 ----
  '⚠ 3초 뒤 크게 뒤척입니다': '⚠ Big toss in 3 seconds',
  '⚠ 앞에 낮은 간판이 있습니다': '⚠ Low signboard ahead',
  '⚠ 앞에 소주병 구간이 있습니다': '⚠ Soju bottles ahead',
  '🤫 부장님이 선잠에 들었습니다 — 서로 다른 정보를 확인하세요': '🤫 The Boss is dozing — you each see different intel',
  '🤫 조용히 하세요!': '🤫 Keep quiet!',
  '🔊 너무 시끄럽습니다!': '🔊 Too loud!',
  '👀 들켰습니다! 움직이지 마세요': "👀 He’s looking! Freeze!",
  '👀 움직이지 마세요.': "👀 Don’t move.",
  '🐈 고양이가 기겁했다!! (': '🐈 The cat freaked out!! (',
  ' 과실)': ' at fault)',
  '📍 체크포인트! 부장님이 편안해 보인다': '📍 Checkpoint! The Boss looks comfortable',
  '체크포인트에서 재정비! 숙면도는 회복되지 않습니다': "Regrouped at checkpoint! Sleep doesn’t recover",
  '🚕 뒷문에 조심히 내려놓으면 ': '🚕 Set him gently by the rear door to skip ',
  'm 단축!': 'm!',
  '🚕 거리 -': '🚕 Distance -',
  'm! 기사님, 명진아파트로요': 'm! Driver, to Myeongjin Apartments',
  '🚕 “손님, 그냥 내려주세요.”': '🚕 "Sir, please just get out."',
  '🚕 택시 출발 5초 전! 서두르세요': '🚕 Taxi leaves in 5 seconds! Hurry',
  '🚕 택시가 떠났다… 조금만 빨랐다면': '🚕 The taxi left… if only you were faster',
  '“어디까지 가세요?”': '"Where to?"',
  '뒷문에 내려놓으세요!': 'Set him down by the rear door!',
  '⏱ 출발까지 ': '⏱ Leaves in ',
  '초': 's',
  ' 손이 미끄러졌다!': ' hand slipped!',
  '가 손을 놓았다!': ' let go!',
  '놓음!': 'Released!',
  '잡는 중': 'Gripping',
  '연습 모드: 왼손이 뒷사람, 오른손이 앞사람!': 'Practice: left hand is Back, right hand is Front!',
  '협동 모드: 서로 탓할 준비 되셨습니까': 'Co-op: ready to blame each other?',
  '마이크를 켜지 못했습니다': "Couldn’t enable the microphone",
  '이 브라우저는 마이크를 지원하지 않습니다': "This browser doesn’t support microphone",
  '🎙 실제 마이크 OFF': '🎙 Real microphone OFF',
  '🎙 실제 마이크 ON — 놀라도 소리 지르지 마세요': "🎙 Real microphone ON — don’t scream",
  '🎙 [V] 마이크 ': '🎙 [V] Mic ',
  '권한 거부': 'Denied', '권한 확인 중': 'Checking', '지원 안 됨': 'Unsupported',

  # ---- HUD/화면 ----
  'MAP ': 'MAP ',
  'm · 장애물 ': 'm · Obstacles ',
  '난이도 ': 'Difficulty ',
  '   소음 ': '   Noise ',
  '회   기상 ': '   Wakes ',
  '회   클립 ': '   Clips ',
  '회   ·   기상 ': '   ·   Wakes ',
  '% 생존   ·   소음 ': '% left   ·   Noise ',
  '터치 스틱 조작 · 상단 메뉴에서 재정비·일시정지': 'Touch sticks · menu top-right for pause/regroup',
  'R 체크포인트 재시작 · P 일시정지 · M 음소거': 'R restart checkpoint · P pause · M mute',
  '◀▶ 이동 · ▲ 점프 · ▼ 숙이기 · 그립': '◀▶ move · ▲ jump · ▼ crouch · grip',
  '←→ 이동 · ↑ 점프 · ↓ 숙이기 · Shift/L 그립': '←→ move · ↑ jump · ↓ crouch · Shift/L grip',
  'A D 이동 · W 점프 · S 숙이기 · F 그립': 'A D move · W jump · S crouch · F grip',
  '놓칠 것 같아!!': "I’m losing him!!",
  '[Shift/L] 다시 잡기': '[Shift/L] Regrab',
  '[F] 다시 잡기': '[F] Regrab',
  '[그립] 다시 잡기': '[GRIP] Regrab',
  ' (오른손)': ' (right hand)', ' (왼손)': ' (left hand)',
  '뒷사람 (': 'Back (', '앞사람 (': 'Front (',
  ' 출발': ' START',
  'm 남기고…': 'm to go…',
  ' 실패 · 부장님이 깨어났다': ' FAILED · The Boss woke up',
  ' 다시 시작': ' restart',
  'R  체크포인트에서 계속     ·     T  LEVEL ': 'R  continue from checkpoint     ·     T  restart LEVEL ',
  '상단 메뉴에서 계속 또는 LEVEL ': 'Use the top menu to continue or restart LEVEL ',
  ' 통과': ' CLEAR',
  '다음 레벨은 더 어렵습니다.': 'The next level is harder.',
  '개 레벨을 전부 살아남았습니다.': ' levels — you survived them all.',
  ' 귀가 보고서 · ': ' Homecoming Report · ',
  '🏁 ': '🏁 ',
  '월요일 출근 생존 확정. 전설이 되셨습니다.': "You’ll survive Monday. You’re a legend.",
  '다음 관문: LEVEL ': 'Next gate: LEVEL ',
  '[Enter] 다음 레벨      [T] 현재 레벨 다시      [Esc] 타이틀로': '[Enter] next level      [T] retry level      [Esc] title',
  '[T] LEVEL 1부터 다시      [Esc] 타이틀로': '[T] restart from LEVEL 1      [Esc] title',
  '상단 메뉴에서 다음 단계·다시하기·타이틀 선택': 'Use the top menu: next / retry / title',
  '과실  뒷사람 ': 'Blame  Back ',
  '% 앞사람   ·   클립 점수 ': '% Front   ·   Clip score ',
  '% 앞사람': '% Front',
  '   ·   수동 재정비 ': '   ·   manual regroups ',
  '   ·   숙면도 ': '   ·   sleep ',
  '배달 ': 'Delivery ',
  '차기 임원감. 부장님이 아침에 해장국을 쏜다.': 'Executive material. The Boss buys hangover soup.',
  '"자네만 믿네." — 두터운 신임을 얻었다.': '“I’m counting on you.” — Deep trust earned.',
  '무난한 직장생활이 이어진다.': 'Office life continues, uneventfully.',
  '월요일 아침, 어쩐지 눈치가 보인다.': 'Monday morning feels… tense.',
  '사내에 팀 이동설이 돈다.': 'Rumors of a team transfer circulate.',
  '지방 발령. 조용히 짐을 싸자.': 'Transferred to the countryside. Pack quietly.',
  '일시정지': 'PAUSED',
  '⏸ 일시정지': '⏸ Paused',
  'P 계속 · R 재정비 · Esc 타이틀': 'P resume · R regroup · Esc title',
  '계속': 'Resume', '재정비': 'Regroup', '음소거': 'Mute', '다시하기': 'Retry', '타이틀': 'Title',
  '다음 단계': 'Next level', 'LEVEL 1부터': 'From LEVEL 1',

  # ---- 리포트/이벤트 화면 (2차 추가) ----
  '뒷사람 주요 혐의: ': 'Back carrier main charge: ',
  'P 계속 · R 체크포인트 재시작 · Esc 타이틀': 'P resume · R restart checkpoint · Esc title',
  '계정명': 'youraccount',
  '※ 본 판정에 대한 이의신청은 받지 않습니다.': '※ No appeals will be accepted for this ruling.',
  '─ 낙하 사고 과실 판정 ─': '─ Fall Incident Fault Ruling ─',
  '▼ 여기 내려놓기 (그립 F / Shift·L 해제)': '▼ Set him down here (F / Shift·L to release)',
  '▼ 여기 내려놓기 (양쪽 그립 해제)': '▼ Set him down here (both release grip)',
  '⚠ 부장님이 뒤척인다…!': '⚠ The Boss is tossing…!',
  '경축! 제 47회 명진마을 척사대회': 'The 47th Myeongjin Village Yut Festival!',
  '공동 수상': 'Shared award',
  '구조 점수 ': 'Rescue score ',
  '부장님이 크게 뒤척였다!': 'The Boss tossed hard!',
  '사유 · ': 'Cause · ',
  '상단 메뉴에서 계속·재정비·타이틀 선택': 'Use the top menu: resume / regroup / title',
  '오늘의 미션 · ': "Tonight’s mission · ",
  '육교 조명': 'Overpass Light',
  '집까지 겨우 ': 'So close — ',
  '총 과실 ': 'Total blame ',
  '최근 1.5초 이동·당김·그립·거리·충돌 부위로 판정': 'Ruled by the last 1.5s of movement, pulling, grip, distance, impact point',
  '혼자 버티는 중!  ': 'Holding on alone!  ',
  '🏆 오늘의 사고왕': '🏆 Blunder MVP',
  '👀 움직이지 마세요': "👀 Don’t move",
  '📊 기록': '📊 Stats',
  '🔊 소리': '🔊 Sound',
  '🗑 쓰레기봉투 → 고양이 → 택시 경적!': '🗑 Trash bag → cat → taxi horn!',
  '🛟 오늘의 구조왕': '🛟 Rescue MVP',
  '🤫 선잠 · 말 대신 신호로  ': "🤫 Dozing · signal, don’t speak  ",

  # ---- 조사/잔여 카운터 ----
  '뒷사람 ': 'Back ',
  '앞사람 ': 'Front ',
  ' / 앞사람 ': ' / Front ',
  '뒷사람': 'Back', '앞사람': 'Front',
  '개': '', '회': '', '동': '',
}

BARE = {'개', '회', '동'}  # 카운터 접미사: 맨 마지막에만 치환

def main():
    s = io.open(SRC, encoding='utf-8').read()
    for k in sorted(T.keys(), key=len, reverse=True):
        if k in BARE:
            continue
        s = s.replace(k, T[k])
    # 단일 문자 치환 전에: 아직 남은 사용자 노출 문자열(리터럴/HTML 텍스트) 수집
    leftovers = set()
    for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'", s):
        if re.search(r'[가-힣]', m.group(1)):
            leftovers.add(m.group(1))
    for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"', s):
        if re.search(r'[가-힣]', m.group(1)):
            leftovers.add(m.group(1))
    for m in re.finditer(r'>([^<>{}]*[가-힣][^<>{}]*)<', s):
        t = m.group(1).strip()
        if t:
            leftovers.add(t)
    for k in BARE:
        s = s.replace(k, T[k])
    s = s.replace('lang="ko"', 'lang="en"')
    io.open(DST, 'w', encoding='utf-8', newline='').write(s)
    out_path = os.path.join(os.path.dirname(__file__), 'en-leftovers.txt')
    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(sorted(leftovers)))
    print('en.html written; %d untranslated user-facing strings -> tools/en-leftovers.txt' % len(leftovers))

if __name__ == '__main__':
    main()
