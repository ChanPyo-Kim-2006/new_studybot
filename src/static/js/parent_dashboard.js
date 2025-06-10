console.log('parent_dashboard.js가 로드되었습니다.');

async function logout() {
    try {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/parent/login';
        }
    } catch (error) {
        console.error('로그아웃 오류:', error);
    }
}

async function addChild() {
    const childCode = document.getElementById('newChildCode').value;
    if (!childCode) {
        alert('자녀 코드를 입력해주세요.');
        return;
    }

    try {
        const response = await fetch('/parent/add-child', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ child_code: childCode })
        });

        const data = await response.json();
        if (data.success) {
            alert('자녀가 추가되었습니다.');
            window.location.reload(); // 자녀 추가 후 페이지 새로 고침
        } else {
            alert(data.message || '자녀 추가에 실패했습니다.');
        }
    } catch (error) {
        console.error('자녀 추가 오류:', error);
        alert('자녀 추가 중 오류가 발생했습니다.');
    }
}

async function viewChildStatus(childCode) {
    if (!childCode) {
        alert('자녀 코드를 입력해주세요.');
        return;
    }
    // 실시간 상태 보기 페이지로 이동
    window.location.href = `/parent/child_status/${encodeURIComponent(childCode)}`;
}
