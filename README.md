# 📘 집중봇 프로젝트 계획서

---

## 1. 프로젝트 이름  
**집중봇**

---

## 2. 프로젝트 목표  
**비대면 학습 감독 프로그램 개발**

- 학생의 **집중도 및 학습 환경을 자동으로 분석**하여 비대면 환경에서도 학습자의 상태를 실시간으로 모니터링합니다.  
- 학습 관리자는 **원격에서 집중 상태를 시각적으로 확인**하고, 즉각적인 피드백 제공을 통해 **학습 효율 향상**을 도모합니다.

---

## 3. 주요 기능  

1. **집중도 측정**
   - **시선 추적**을 통해 사용자가 **화면이나 책을 바라보는지 여부**를 실시간 분석
   - 일정 시간 동안 학습 대상에서 시선이 벗어나면 **집중도 점수 하락**, 시각화 제공

2. **얼굴 등록 및 인증**
   - **얼굴 인식 기반 등록 및 로그인 인증**
   - 새로운 사용자는 이름과 함께 얼굴을 등록하여 인증된 사용자만 학습 환경 접근 가능

3. **학습 환경 사물 인식**
   - **책/노트 등 필수 물품 인식**, 학습 환경이 적절한지 자동 확인
   - 불필요한 물품이 자주 인식되면 **집중도에 부정적 영향** 경고 제공

4. **관리자 대시보드**
   - **Node.js 기반 실시간 대시보드**로 사용자별 집중도, 얼굴 인증 상태, 실시간 영상 확인
   - 실시간 피드백 제공으로 학습 감독 가능

---

## 4. 개발자  
**김찬표 (Kim Chan-Pyo)**

---

## 5. 개발 기간  
**2024년** (고등학교 3학년 개발 프로젝트)

---

## 6. 기술 스택  

| 영역       | 사용 기술 |
|------------|-----------|
| 프론트엔드 | HTML, CSS, JavaScript, Node.js |
| 백엔드     | Python (Flask or FastAPI), Socket.IO |
| AI/ML      | MediaPipe (얼굴 인식 및 시선 추적) |
| DB         | SQLite 또는 PostgreSQL |
| 배포       | 추후 결정 예정 |

---

## 7. 기능 상세 및 구현 계획

### 1. 집중도 측정
- MediaPipe Face Mesh를 활용하여 **시선 방향과 눈 위치 분석**
- 기준 각도 벗어나면 집중도 점수 하락, 수치화 후 사용자/관리자에게 제공

### 2. 얼굴 등록 및 인증
- 등록 시 얼굴 특징점 추출 → DB 저장
- 로그인 시 등록된 얼굴과 실시간 비교하여 인증

### 3. 학습 환경 사물 인식
- 학습 필수 물품만 인식
- 불필요한 물품 감지 시 **경고 메시지 출력**

### 4. 관리자 대시보드
- Node.js 기반 웹 UI
- 사용자 목록, 집중도 그래프, 인증 여부, 실시간 시선 상태 표시

---

## 8. 개발 일정

| 단계              | 기간           | 주요 작업 |
|-------------------|----------------|-----------|
| 요구사항 분석      | 1주차          | 프로젝트 목표 및 기술 스택 확정 |
| 초기 설계         | 2주차          | DB 및 API 설계, UI 목업 제작 |
| 기능 구현         | 3~6주차        | 얼굴 인식, 시선 추적, 사물 인식 등 |
| 대시보드 구현     | 7~8주차        | Node.js 기반 실시간 대시보드 구현 |
| 테스트 및 배포     | 9~10주차       | 통합 테스트 및 배포 준비 |
| 유지 보수         | 10주차 이후    | 피드백 반영 및 기능 개선 |

---

## 9. 예상되는 어려움 및 해결 방안

| 이슈 | 해결 방안 |
|------|------------|
| 시선 추적 정확도 | 다양한 환경에서 테스트, 알고리즘 임계값 조정 |
| 실시간 처리 지연 | Socket.IO 비동기 처리로 최적화 |
| 서버 간 연동 | Flask ↔ Node.js 간 REST API 및 Socket 연동 |
| 개인정보 보안 | 얼굴 특징점 암호화, HTTPS 적용 |

---

## 10. 기대 효과

- 원격 환경에서 **집중력 분석 기반 학습 감독** 가능
- 학생의 **학습 태도 자각 및 개선 유도**
- 학습 관리자/교사의 피드백을 통해 **비대면 학습 품질 향상**

---

> 이 프로젝트는 고등학교 3학년 당시 시작된 개인 연구 기반이며, 향후 AI 기반 학습 관리 시스템으로 확장될 수 있습니다.