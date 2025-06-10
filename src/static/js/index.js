 // 폼 전환 함수
 function showRegisterForm() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
}

// 얼굴 로그인 함수
async function login() {
    const username = document.getElementById('loginUsername').value;
    
    if (!username) {
        showStatus('사용자 이름을 입력해주세요.', 'error');
        return;
    }

    try {
        showStatus('얼굴 인식 중...', 'info');
        const response = await fetch('/child/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username })
        });

        const data = await response.json();
        
        if (response.ok && data.success) {
            showStatus('얼굴 인식 성공!', 'success');
            window.location.href = '/child/main';
        } else {
            showStatus(data.message || '얼굴 인식 실패', 'error');
        }
    } catch (error) {
        console.error('로그인 오류:', error);
        showStatus('서버 오류가 발생했습니다.', 'error');
    }
}

// register 함수 수정
async function register() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const region = document.getElementById('region').value;
    const school_name = document.getElementById('school_name').value;

    if (!username || !email || !region || !school_name) {
        showStatus('모든 필드를 입력해주세요.', 'error');
        return;
    }

try {
showStatus('얼굴 등록 중...', 'info');

const response = await fetch('/child/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username,
        email,
        region,
        school_name
    })
});

const rawText = await response.text();  // ✅ 먼저 raw 텍스트로 읽기

let data;
try {
    data = JSON.parse(rawText);  // ✅ JSON 파싱 시도
} catch (err) {
    console.error("JSON 파싱 실패, 응답 텍스트:", rawText);
    showStatus('서버 오류 발생: ' + rawText, 'error');
    return;
}


if (response.ok && data.success) {
    // 성공 메시지와 자녀 코드 표시
    document.getElementById('childId').textContent = data.child_code;
    document.getElementById('registrationSuccess').style.display = 'block';
    
    // 입력 폼 숨기기
    document.getElementById('username').style.display = 'none';
    document.getElementById('email').style.display = 'none';
    document.querySelector('#registerForm .primary-btn').style.display = 'none';
    document.getElementById('region').style.display = 'none';
    document.getElementById('school_name').style.display = 'none';
    showStatus('얼굴 등록이 완료되었습니다!', 'success');
    
    // 5초 후 로그인 폼으로 전환
    setTimeout(() => {
        document.getElementById('registrationSuccess').style.display = 'none';
        showLoginForm();
        // 입력 폼 초기화 및 다시 표시
        document.getElementById('username').value = '';
        document.getElementById('email').value = '';
        document.getElementById('username').style.display = 'block';
        document.getElementById('email').style.display = 'block';
        document.getElementById('region').style.display = 'block';
        document.getElementById('school_name').style.display = 'block';
        document.querySelector('#registerForm .primary-btn').style.display = 'block';
    }, 5000);
} else {
    showStatus(data.message || '얼굴 등록에 실패했습니다.', 'error');
}
} catch (error) {
console.error('등록 오류:', error);
showStatus('서버 오류가 발생했습니다.', 'error');
}
}

// 상태 메시지 표시 함수 수정
function showStatus(message, type = 'info') {
const statusElement = document.getElementById('status');
statusElement.textContent = message;
statusElement.className = `status-message ${type}`;
statusElement.style.display = 'block';

if (type === 'success' || type === 'error') {
setTimeout(() => {
    statusElement.style.display = 'none';
}, 3000);
}
}

// CSS 스타일 추가
const styles = `
.status-message {
padding: 10px;
border-radius: 5px;
margin: 10px 0;
text-align: center;
}

.status-message.info {
background-color: #e3f2fd;
color: #1976d2;
}

.status-message.success {
background-color: #e8f5e9;
color: #2e7d32;
}

.status-message.error {
background-color: #ffebee;
color: #c62828;
}

.success-message {
animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
from { opacity: 0; transform: translateY(-10px); }
to { opacity: 1; transform: translateY(0); }
}
`;

// 스타일 태그 추가
const styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);