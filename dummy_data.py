import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# 토픽별 학습 데이터 정의
TOPIC_DATA = {
    "CNN": {
        "checkpoints": ["convolution", "filters", "feature maps", "pooling"],
        "conversations": {
            2: {
                "user": ["CNN이 뭔가요?", "이미지를 검출하는데 어떻게 쓰나요?"],
                "ai": [
                    "CNN은 Convolutional Neural Network의 줄임말로, 이미지 처리에 특화된 신경망입니다. 이미지의 특징을 찾기 위해 필터를 사용합니다.",
                    "필터가 이미지를 슬라이딩하면서 특징을 추출하고, 그 결과를 모아서 특징 맵을 만듭니다. 이를 통해 이미지의 패턴을 인식할 수 있어요."
                ]
            },
            5: {
                "user": [
                    "CNN에 대해 들어봤는데, 정확히 뭔가요?",
                    "필터가 무엇을 하는건가요?",
                    "아, 그럼 필터가 이미지를 움직이면서 특징을 찾는다는 거네요?",
                    "그럼 특징 맵이라는 게 뭐죠?",
                    "풀링은 왜 필요한가요?"
                ],
                "ai": [
                    "CNN은 이미지의 특징을 자동으로 학습하는 신경망입니다. 사람이 직접 특징을 정의하지 않아도 돼요.",
                    "필터는 작은 가중치 행렬로, 이미지 위를 움직이면서 각 위치에서 특정 패턴과 얼마나 유사한지를 계산합니다.",
                    "정확해요! 필터가 이미지 위를 슬라이딩하며 합성곱 연산을 수행하면, 그 결과들이 모여서 특징 맵을 이룹니다.",
                    "특징 맵은 필터가 추출한 특징들을 2D 형태로 표현한 것입니다. 각 픽셀 값이 그 위치에서의 특징 강도를 나타내요.",
                    "풀링은 특징 맵의 크기를 줄이면서 중요한 정보는 유지하는 작업입니다. 이를 통해 계산량을 줄이고 과적합을 방지할 수 있어요."
                ]
            },
            10: {
                "user": [
                    "CNN이라고 들었는데 뭐하는 건가요?",
                    "이미지를 처리하는 신경망이라는 게 정확히 뭐죠?",
                    "필터가 이미지에 어떻게 적용되나요?",
                    "여러 필터를 동시에 적용할 수 있나요?",
                    "그럼 결과물이 특징 맵이라는 건가요?",
                    "특징 맵을 어떻게 활용하나요?",
                    "풀링이라는 게 뭐죠?",
                    "Max pooling과 average pooling은 뭐가 다른가요?",
                    "완전 연결 층(fully connected layer)은 어디에 쓰나요?",
                    "CNN 학습은 어떻게 이루어지나요?"
                ],
                "ai": [
                    "CNN은 Convolutional Neural Network로, 이미지 인식 작업에 뛰어난 신경망입니다.",
                    "CNN은 필터라는 작은 가중치 집합을 사용해서 이미지의 지역 특징을 추출합니다.",
                    "필터가 이미지 위를 움직이면서 합성곱(convolution) 연산을 수행합니다. 각 위치에서 필터와 이미지의 내적을 계산하는 거예요.",
                    "네, 여러 필터를 동시에 적용할 수 있어요. 각 필터는 다른 패턴을 학습하고, 결과적으로 여러 개의 특징 맵이 생성됩니다.",
                    "정확해요! 필터 연산의 결과들이 모여서 특징 맵이 됩니다. 특징 맵의 각 값은 해당 위치에서의 특징 강도를 나타냅니다.",
                    "특징 맵은 다음 층의 입력으로 사용됩니다. 여러 층을 거치면서 저수준 특징에서 고수준 특징으로 점진적으로 학습돼요.",
                    "풀링(pooling)은 특징 맵의 크기를 줄이는 작업입니다. 계산량을 줄이고 중요한 정보만 유지하는 효과가 있어요.",
                    "Max pooling은 영역에서 최댓값을 선택하고, average pooling은 평균값을 계산합니다. Max pooling이 더 많이 사용돼요.",
                    "완전 연결 층은 CNN의 마지막 부분에 위치합니다. 추출된 특징을 기반으로 최종 분류나 예측을 수행해요.",
                    "CNN 학습은 역전파(backpropagation)를 통해 이루어집니다. 손실함수의 기울기를 계산해서 필터의 가중치를 업데이트하는 거예요."
                ]
            }
        }
    },
    "Python Loops": {
        "checkpoints": ["for loop", "while loop", "iteration", "break/continue"],
        "conversations": {
            2: {
                "user": ["반복문이 뭔가요?", "for 루프와 while 루프가 뭐가 다른가요?"],
                "ai": [
                    "반복문은 같은 코드를 여러 번 실행할 때 사용해요. 손으로 일일이 코드를 여러 번 쓸 필요가 없어집니다.",
                    "for 루프는 정해진 횟수만큼 반복하고, while 루프는 조건이 참인 동안 계속 반복돼요."
                ]
            },
            5: {
                "user": [
                    "반복문을 왜 써야 하나요?",
                    "for 루프의 기본 구조는 뭔가요?",
                    "변수 i는 뭐가 하는 건가요?",
                    "range(5)를 쓰면 어디서부터 어디까지 반복되나요?",
                    "break랑 continue는 뭐가 다른가요?"
                ],
                "ai": [
                    "반복문을 쓰면 코드가 짧아지고 읽기도 쉬워져요. 1부터 100까지 더할 때 더 편하죠.",
                    "for 루프는 'for i in range(5):'처럼 시작해요. i는 계속 변해가면서 각 반복마다 다른 값을 가져요.",
                    "i는 루프 변수예요. 각 반복마다 자동으로 0부터 4까지 변해가면서 루프 안의 코드가 실행돼요.",
                    "range(5)는 0부터 4까지 5번 반복해요. 마지막 숫자는 포함되지 않는다는 점이 중요해요!",
                    "break는 루프를 완전히 빠져나가고, continue는 그 턴만 건너뛰고 다음 턴으로 넘어가요."
                ]
            },
            10: {
                "user": [
                    "파이썬에서 반복문이란 뭐예요?",
                    "반복문을 배워야 하는 이유가 뭐죠?",
                    "for 루프의 문법을 설명해줄래요?",
                    "range() 함수가 정확히 뭐하는 건가요?",
                    "루프 안에 루프를 만들 수도 있나요?",
                    "이중 루프는 언제 써나요?",
                    "while 루프는 언제 쓰나요?",
                    "무한 루프는 어떻게 되는 거죠?",
                    "enumerate() 함수는 뭐 하는 거예요?",
                    "반복문을 종료하는 방법들이 뭐가 있나요?"
                ],
                "ai": [
                    "반복문은 같은 작업을 여러 번 반복할 때 사용해요. 프로그래밍에서 가장 중요한 개념 중 하나입니다.",
                    "반복문을 쓰면 코드가 훨씬 짧고 효율적이 돼요. 1부터 1000까지 더할 때 1000줄을 쓸 필요가 없어지죠.",
                    "for 루프는 'for 변수명 in 리스트:'로 시작해요. 콜론(:)은 꼭 붙여야 하고, 다음 줄은 들여쓰기를 해야 해요.",
                    "range() 함수는 숫자 범위를 생성해요. range(5)는 0, 1, 2, 3, 4를 만들어주고, range(1, 6)은 1부터 5까지 만들어요.",
                    "네, 루프 안에 루프를 만들 수 있어요. 이걸 중첩 루프라고 부르는데, 구구단 출력할 때 많이 써요.",
                    "이중 루프는 2차원 데이터를 처리할 때 자주 써요. 예를 들어 표의 모든 셀을 확인할 때처럼요.",
                    "while 루프는 조건이 참인 동안 계속 반복해요. 몇 번 반복할지 정하기 어려울 때 유용해요.",
                    "루프 조건이 항상 참이면 무한 루프가 돼요. 이 경우 프로그램이 멈추지 않으니까 피해야 해요.",
                    "enumerate() 함수는 반복할 때 원소의 인덱스와 값을 동시에 가져올 수 있어요. for i, item in enumerate(list) 이렇게요.",
                    "break는 루프를 완전히 빠져나가고, continue는 그 턴만 건너뛰고, 조건을 False로 만들면 루프가 종료돼요."
                ]
            }
        }
    },
    "Git Basics": {
        "checkpoints": ["commit", "branch", "merge", "pull request"],
        "conversations": {
            2: {
                "user": ["Git이 뭔가요?", "커밋(commit)이라는 게 뭐죠?"],
                "ai": [
                    "Git은 코드 변경 이력을 관리해주는 버전 관리 시스템이에요. 여러 명이 협력해서 개발할 때 특히 중요해요.",
                    "커밋은 코드의 스냅샷을 저장하는 거예요. 마치 게임에서 세이브 포인트를 만드는 것처럼요."
                ]
            },
            5: {
                "user": [
                    "버전 관리가 왜 필요한가요?",
                    "커밋은 어떻게 하는 건가요?",
                    "커밋 메시지는 뭐가 중요한가요?",
                    "브랜치(branch)는 뭐죠?",
                    "여러 브랜치를 합치려면 뭐 해야 하나요?"
                ],
                "ai": [
                    "코드 변경을 기록하면 나중에 필요할 때 이전 버전으로 돌아갈 수 있어요. 또 누가 뭘 바꿨는지도 알 수 있어요.",
                    "git add로 변경 사항을 준비하고, git commit으로 저장해요. 그러면 스냅샷이 만들어진다는 거죠.",
                    "좋은 커밋 메시지가 있으면 나중에 왜 이렇게 바꿨는지 쉽게 이해할 수 있어요. 명확하고 짧은 메시지가 좋아요.",
                    "브랜치는 코드의 여러 버전을 동시에 만들 수 있게 해줘요. 독립적으로 작업했다가 나중에 합칠 수 있어요.",
                    "merge 명령으로 두 브랜치를 합쳐요. 충돌(conflict)이 나면 어느 것을 선택할지 결정해야 해요."
                ]
            },
            10: {
                "user": [
                    "Git의 용도가 뭐예요?",
                    "Git과 GitHub의 차이가 뭐죠?",
                    "처음으로 저장소를 만들려면 뭐 해야 하나요?",
                    "변경 사항을 저장하는 단계가 몇 개나 되나요?",
                    "커밋 메시지를 잘 쓰려면 뭘 신경써야 하나요?",
                    "브랜치를 만드는 이유가 뭐죠?",
                    "원격 저장소에 코드를 올리려면 뭐 해야 하나요?",
                    "다른 사람이 한 변경을 받으려면 어떻게 하나요?",
                    "두 사람이 같은 파일을 바꾸면 어떻게 되나요?",
                    "Git을 배웠을 때 가장 중요한 개념이 뭐예요?"
                ],
                "ai": [
                    "Git은 프로젝트의 모든 변경 이력을 추적해요. 팀 협업에서 필수적인 도구예요.",
                    "Git은 버전 관리 시스템이고, GitHub는 Git을 사용하는 온라인 플랫폼이에요. GitHub에 저장소를 올릴 수 있어요.",
                    "git init으로 새 저장소를 만들거나, git clone으로 기존 저장소를 복제해요.",
                    "보통 3단계예요. 1) 파일 수정, 2) git add로 준비, 3) git commit으로 저장해요.",
                    "현재형으로 쓰고, 짧고 명확하게, 왜 바꿨는지를 설명하는 게 좋아요. '완료함' 같은 건 피해야 해요.",
                    "새로운 기능을 만들 때 브랜치를 만들면 main 브랜치는 안전하게 유지할 수 있어요.",
                    "git push 명령으로 원격 저장소에 업로드해요. git push origin main처럼 쓰면 돼요.",
                    "git pull이나 git fetch로 원격의 변경 사항을 가져올 수 있어요. pull은 merge도 함께 해요.",
                    "이건 충돌(conflict)이 생기는 거예요. 어느 것을 선택할지 직접 결정해야 해요. Git이 표시해줘서 찾기는 쉬워요.",
                    "커밋 메시지와 브랜칭이 가장 중요해요. 이 두 가지만 잘 해도 협업이 훨씬 수월해져요."
                ]
            }
        }
    },
    "React Hooks": {
        "checkpoints": ["useState", "useEffect", "dependencies", "cleanup"],
        "conversations": {
            2: {
                "user": ["React Hooks가 뭔가요?", "useState는 뭐 하는 건가요?"],
                "ai": [
                    "React Hooks는 함수형 컴포넌트에서 state와 다른 React 기능을 쓸 수 있게 해주는 기능이에요.",
                    "useState는 컴포넌트에 상태를 추가해줘요. 상태가 바뀌면 화면이 자동으로 업데이트된다는 장점이 있어요."
                ]
            },
            5: {
                "user": [
                    "Hooks를 쓰는 이유가 뭐예요?",
                    "useState를 어떻게 사용하나요?",
                    "state가 바뀌면 뭐가 일어나나요?",
                    "useEffect는 뭐 하는 건가요?",
                    "의존성 배열(dependency array)은 뭐죠?"
                ],
                "ai": [
                    "Hooks를 쓰면 함수형 컴포넌트에서도 클래스형처럼 강력한 기능을 쓸 수 있어요. 코드도 더 간단하고 읽기 쉬워요.",
                    "useState(초기값)을 호출하면 [상태, 상태변경함수]를 반환해요. 상태변경함수를 호출하면 상태가 바뀌고 컴포넌트가 다시 렌더링돼요.",
                    "state가 바뀌면 React가 자동으로 컴포넌트를 다시 렌더링해요. 그래서 화면에 새로운 값이 표시되는 거죠.",
                    "useEffect는 부작용(side effect)을 처리해요. API를 호출하거나 타이머를 설정할 때 사용해요.",
                    "의존성 배열은 useEffect가 언제 실행될지 결정해요. 배열 안의 값이 바뀔 때만 effect가 실행되는 거죠."
                ]
            },
            10: {
                "user": [
                    "클래스형 컴포넌트와 Hooks의 차이가 뭐예요?",
                    "useState를 여러 번 써도 되나요?",
                    "state를 업데이트할 때 주의할 점이 뭐죠?",
                    "useEffect는 정확히 언제 실행되나요?",
                    "의존성 배열을 안 쓰면 어떻게 되나요?",
                    "의존성 배열이 빈 배열이면 뭐가 다른가요?",
                    "useEffect에서 cleanup 함수는 뭐 하는 건가요?",
                    "여러 effect를 쓸 수 있나요?",
                    "Hook 규칙들이 뭐가 있나요?",
                    "자주 하는 실수가 뭐예요?"
                ],
                "ai": [
                    "클래스형은 더 복잡하고 보일러플레이트 코드가 많아요. Hooks는 함수형으로 더 간단해요.",
                    "네, 여러 번 써도 돼요. 각 상태를 따로 관리할 수 있어서 오히려 더 좋아요.",
                    "state 업데이트는 비동기라는 점이 중요해요. 또 state를 직접 수정하면 안 되고, 새로운 값을 전달해야 해요.",
                    "useEffect는 렌더링 후에 실행돼요. 의존성 배열에 따라 매번 실행되거나, 특정 상황에만 실행돼요.",
                    "의존성 배열을 안 쓰면 렌더링 될 때마다 매번 실행돼요. 이러면 무한 루프에 빠질 수 있어요.",
                    "빈 배열이면 마운트될 때만 한 번 실행돼요. 초기화 작업할 때 주로 사용해요.",
                    "cleanup 함수는 effect가 끝날 때 실행돼요. 타이머를 취소하거나 구독을 해제할 때 써요.",
                    "네, 여러 effect를 쓸 수 있어요. 각 effect가 다른 일을 하게 할 수 있으니까요.",
                    "Hook은 최상위 레벨에서만 써야 해요. 조건문이나 루프 안에서 쓰면 안 된다는 거죠.",
                    "가장 흔한 실수는 의존성 배열을 빼먹는 거예요. 또 useEffect 안에서 상태를 업데이트하면서 무한 루프가 되는 경우도 많아요."
                ]
            }
        }
    }
}

# 더미 데이터 생성 함수
def create_dummy_session(total_turns: int, topic: str):
    """테스트용 학습 세션 더미 데이터 생성"""

    topic_info = TOPIC_DATA[topic]

    session_data = {
        "session_id": str(uuid4()),
        "topic": topic,
        "created_at": datetime.now().isoformat(),
        "total_turns": total_turns,
        "attempt_count": 0,
        "checkpoints": topic_info["checkpoints"],
        "conversation": []
    }

    # 턴별 더미 대화 생성
    conv_data = topic_info["conversations"][total_turns]
    for turn in range(1, total_turns + 1):
        conversation_turn = {
            "turn": turn,
            "user_input": conv_data["user"][turn - 1],
            "ai_response": conv_data["ai"][turn - 1]
        }
        session_data["conversation"].append(conversation_turn)

    return session_data

def save_dummy_sessions():
    """더미 데이터를 파일로 저장"""

    # dummy_data 디렉토리 생성
    dummy_dir = Path("dummy_data")
    dummy_dir.mkdir(exist_ok=True)

    all_sessions = []
    topics = list(TOPIC_DATA.keys())
    session_count = 0

    # 10턴 데이터 - 각 토픽별 1개씩 (4개 토픽 × 1 = 4개)
    print("🔄 10턴 더미 데이터 생성 중 (토픽별 1개씩)...")
    for topic in topics:
        session = create_dummy_session(total_turns=10, topic=topic)
        all_sessions.append(session)
        session_count += 1

        session_file = dummy_dir / f"session_10turn_{topic}_{session['session_id'][:8]}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        print(f"  ✓ 저장됨: {session_file.name}")

    # 5턴 데이터 - 각 토픽별 1개씩 (4개 토픽 × 1 = 4개)
    print("\n🔄 5턴 더미 데이터 생성 중 (토픽별 1개씩)...")
    for topic in topics:
        session = create_dummy_session(total_turns=5, topic=topic)
        all_sessions.append(session)
        session_count += 1

        session_file = dummy_dir / f"session_5turn_{topic}_{session['session_id'][:8]}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        print(f"  ✓ 저장됨: {session_file.name}")

    # 2턴 데이터 - 각 토픽별 1개씩 (4개 토픽 × 1 = 4개)
    print("\n🔄 2턴 더미 데이터 생성 중 (토픽별 1개씩)...")
    for topic in topics:
        session = create_dummy_session(total_turns=2, topic=topic)
        all_sessions.append(session)
        session_count += 1

        session_file = dummy_dir / f"session_2turn_{topic}_{session['session_id'][:8]}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        print(f"  ✓ 저장됨: {session_file.name}")

    # 모든 세션을 하나의 파일로 저장
    summary_file = dummy_dir / "all_sessions.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_sessions": len(all_sessions),
            "sessions": [
                {
                    "session_id": s["session_id"],
                    "topic": s["topic"],
                    "total_turns": s["total_turns"],
                    "created_at": s["created_at"]
                }
                for s in all_sessions
            ]
        }, f, indent=2, ensure_ascii=False)
    print(f"\n✓ 전체 세션 요약: {summary_file.name}")

    print(f"\n✅ 더미 데이터 생성 완료!")
    print(f"   - 10턴: {len(topics)}개 ({', '.join(topics)})")
    print(f"   - 5턴: {len(topics)}개 ({', '.join(topics)})")
    print(f"   - 2턴: {len(topics)}개 ({', '.join(topics)})")
    print(f"   - 총: {session_count}개 세션")

if __name__ == "__main__":
    save_dummy_sessions()
