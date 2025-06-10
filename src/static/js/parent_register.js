function validateForm() {
    const password = document.querySelector('input[name="password"]').value;
    const passwordConfirm = document.querySelector('input[name="password_confirm"]').value;
    const childCode = document.querySelector('input[name="child_code"]').value;
    
    if (password !== passwordConfirm) {
        alert('비밀번호가 일치하지 않습니다.');
        return false;
    }
    
const codePattern = /^STU-[a-z0-9]{4}-[a-z0-9]{4}$/;
if (!codePattern.test(childCode)) {
    alert('올바른 자녀 코드 형식이 아닙니다. (예: STU-40fb-c5ff)');
    return false;
}

return true;
}