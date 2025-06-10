let statusCheckInterval;
let lastStatus = {};  // 마지막 상태 저장
let errorCount = 0;   // 연속 에러 카운트
const MAX_ERRORS = 3; // 최대 허용 에러 횟수
// 상태 메시지 번역 매핑
const STATUS_TRANSLATION = {
    "Focusing": "집중",
    "Partially focusing": "부분 집중",
    "Not focusing": "주의 산만",
    "No Face": "얼굴 없음",
    "Unknown": "알 수 없음",
    "Center": "정면",
    "Left": "왼쪽",
    "Right": "오른쪽",
    "Up": "위쪽",
    "Down": "아래쪽"
};


async function checkStatus() {
    try {
        const response = await fetch('/child/status', {
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        if (response.status === 401) {
            console.log('인증 만료, 로그인 페이지로 이동');
            window.location.href = '/';
            return;
        }
        
        if (!response.ok) {
            throw new Error('상태 확인 실패');
        }
        
        const data = await response.json();
        
        if (data.success) {
            errorCount = 0; // 에러 카운트 리셋
            
            // 상태가 변경된 경우에만 업데이트
            if (statusHasChanged(data)) {
                updateStatus(data);
                lastStatus = data; // 마지막 상태 업데이트
            }
        }
    } catch (error) {
        console.error('상태 확인 오류:', error);
        errorCount++;
        
        if (errorCount >= MAX_ERRORS) {
            showError();
            resetStatusCheck(3000); // 3초로 늘림
        }
    }
}

function statusHasChanged(newData) {
    return !lastStatus.status || 
           lastStatus.status !== newData.status ||
           lastStatus.concentration_score !== newData.concentration_score ||
           lastStatus.gaze_status !== newData.gaze_status ||
           lastStatus.face_detected !== newData.face_detected;
}

function updateStatus(data) {
    // 집중 상태
    const statusElement = document.getElementById('concentration-status');
    const newStatusText = getStatusText(data.status);
    if (statusElement.textContent !== newStatusText) {
        statusElement.textContent = newStatusText;
        statusElement.className = 'status-value ' + getStatusClass(data.status);
        // 상태 변경 애니메이션
        statusElement.classList.add('status-changed');
        setTimeout(() => statusElement.classList.remove('status-changed'), 500);
    }

    // 집중도 점수
    const score = data.concentration_score;
    const scoreElement = document.getElementById('concentration-score');
    if (scoreElement.textContent !== score.toString()) {
        scoreElement.textContent = score;
        document.getElementById('concentration-progress').style.width = `${score}%`;
    }

    // 시선 상태
    const gazeElement = document.getElementById('gaze-status');
    const newGazeText = getGazeStatusText(data.gaze_status);
    if (gazeElement.textContent !== newGazeText) {
        gazeElement.textContent = newGazeText;
        gazeElement.classList.add('status-changed');
        setTimeout(() => gazeElement.classList.remove('status-changed'), 500);
    }

    // 얼굴 감지 상태
    const faceElement = document.getElementById('face-detected');
    const newFaceText = data.face_detected ? "감지됨" : "감지되지 않음";
    if (faceElement.textContent !== newFaceText) {
        faceElement.textContent = newFaceText;
        faceElement.className = data.face_detected ? 'status-focusing' : 'status-not-focusing';
    }
}

function getStatusText(status) {
    return STATUS_TRANSLATION[status] || "상태 확인 중...";
}

function getGazeStatusText(status) {
    return STATUS_TRANSLATION[status] || "확인 중...";
}

function getStatusClass(status) {
    switch(status) {
        case "Focusing": return "status-focusing";
        case "Partially focusing": return "status-partial";
        case "Not focusing": return "status-not-focusing";
        default: return "";
    }
}

function showError() {
    document.getElementById('concentration-status').textContent = "오류 발생";
    document.getElementById('concentration-score').textContent = "0";
    document.getElementById('concentration-progress').style.width = "0%";
    document.getElementById('gaze-status').textContent = "오류 발생";
    document.getElementById('face-detected').textContent = "확인 불가";
}

function resetStatusCheck(interval = 1000) {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    statusCheckInterval = setInterval(checkStatus, interval);
}

async function logout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('로그아웃 오류:', error);
    }
}

// 페이지 로드 시 상태 확인 시작
window.onload = function() {
    checkStatus();
    resetStatusCheck();
};

// 페이지 가시성 변경 감지
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        resetStatusCheck(3000);
    } else {
        checkStatus();
        resetStatusCheck();
    }
});

// 스타일 추가
const style = document.createElement('style');
style.textContent = `
    .status-changed {
        animation: highlight 0.5s ease-in-out;
    }

    @keyframes highlight {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);