# Socrates-AI 
fastAPI로 서빙하는 코드입니다.

1. 아래 플로우는 수정 가능한 플로우입니다.
2. 프롬프트 사항은 prompts안에 markdown으로 있습니다.
3. 2025-12-17 18:00 기준으로 langgraph 에러 발생하고 있어 수정해야 합니다.
4. 테스트

----
### 2025-12-18
- utils 문제 해결(gitignore에 추가되서 문제였음)

### 2025-12-17

- 채팅 세션 플로우
```mermaid
flowchart TD
    Start([세션 시작]) --> Init[체크포인트 설정]
    Init --> CreateSession[DB: sessions 생성]
    CreateSession --> InitPrompt[초기 평가 프롬프트 생성]
    InitPrompt --> FirstQ[첫 질문 생성<br/>Claude API]
    FirstQ --> ShowQ[사용자에게 질문 제시]
    
    ShowQ --> UserInput{사용자 응답 입력}
    
    UserInput --> Analyze[응답 분석]
    Analyze --> DetectStuck{막힘 감지}
    DetectStuck -->|Yes| IncStuck[stuck_count++]
    DetectStuck -->|No| ResetStuck[stuck_count = 0]
    
    IncStuck --> CheckCP[체크포인트 확인]
    ResetStuck --> CheckCP
    
    CheckCP -->|키워드 매칭| CPScore{70% 이상?}
    CPScore -->|Yes| Achieved[체크포인트 달성]
    CPScore -->|No| NotYet[진행 중]
    
    Achieved --> SaveAchieve[DB: checkpoint_achievements 저장]
    NotYet --> SaveRecord[DB: learning_records 저장]
    SaveAchieve --> SaveRecord
    
    SaveRecord --> CalcProgress[진도율 계산]
    CalcProgress --> SaveStuck[DB: stuck_records 저장]
    SaveStuck --> CheckEnd{종료 조건?}
    
    CheckEnd -->|진도 >= 80%| EndReason1[학습 목표 달성]
    CheckEnd -->|막힘 >= 5회| EndReason2[연속 막힘 도달]
    CheckEnd -->|모든 CP 완료| EndReason3[전체 완료]
    CheckEnd -->|계속| NextPrompt[다음 프롬프트 생성]
    
    NextPrompt -->|stuck >= 3| HintMode[힌트 제공 모드]
    NextPrompt -->|progress < 0.3| EasyMode[기초 확립 모드]
    NextPrompt -->|순조로움| NormalMode[심화 모드]
    
    HintMode --> GenQ[AI 질문 생성]
    EasyMode --> GenQ
    NormalMode --> GenQ
    GenQ --> ShowQ
    
    EndReason1 --> GenerateReport[리포트 생성]
    EndReason2 --> GenerateReport
    EndReason3 --> GenerateReport
    
    GenerateReport --> ReportPrompt[report_prompt.py 사용]
    ReportPrompt --> ClaudeReport[Claude에게 리포트 요청]
    ClaudeReport --> FinalReport[최종 리포트 출력]
    FinalReport --> UpdateSession[DB: sessions 종료 업데이트]
    UpdateSession --> End([세션 종료])
    
    style Start fill:#90EE90,color:black;
    style End fill:#FFB6C1,color:black;
    style GenerateReport fill:#FFD700,color:black;
    style CheckEnd fill:#FF6B6B,color:black;
```
