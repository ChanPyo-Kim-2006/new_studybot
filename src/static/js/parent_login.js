document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 입력값 검증
        if (!usernameInput.value.trim()) {
            showError('아이디를 입력해주세요.');
            usernameInput.focus();
            return;
        }

        if (!passwordInput.value.trim()) {
            showError('비밀번호를 입력해주세요.');
            passwordInput.focus();
            return;
        }

        // 폼 제출
        this.submit();
    });

    // 에러 메시지 표시 함수
    function showError(message) {
        let errorDiv = document.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            loginForm.insertBefore(errorDiv, loginForm.firstChild);
        }
        errorDiv.textContent = message;
        
        // 3초 후 에러 메시지 삭제
        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }

    // 입력 필드 포커스시 에러 메시지 제거
    [usernameInput, passwordInput].forEach(input => {
        input.addEventListener('focus', function() {
            const errorDiv = document.querySelector('.error-message');
            if (errorDiv) {
                errorDiv.remove();
            }
        });
    });

    // Enter 키로 다음 입력 필드로 이동
    usernameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            passwordInput.focus();
        }
    });
});