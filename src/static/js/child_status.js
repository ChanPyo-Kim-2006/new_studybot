 // 자녀 코드를 JavaScript 변수로 설정
 const childCode = "{{ child_code }}";

 async function updateStatus() {
     try {
         const response = await fetch(`/parent/child_status/${childCode}`, {
             headers: {
                 'Accept': 'application/json'
             }
         });
         const data = await response.json();
         
         if (data.success) {
             document.getElementById('currentStatus').textContent = data.status;
             document.getElementById('concentrationScore').textContent = data.concentration_score;
             document.getElementById('gazeStatus').textContent = data.gaze_status;
         }
     } catch (error) {
         console.error('상태 업데이트 오류:', error);
     }
 }

 function logout() {
    // 로그아웃 처리 후 로그인 페이지로 리다이렉트
    fetch('/parent/logout', {
        method: 'POST',
        credentials: 'include'
    }).then(() => {
        window.location.href = '/parent/login';
    });
}

 // 초기 상태 업데이트
 updateStatus();

 // 3초마다 상태 업데이트
 setInterval(updateStatus, 3000);

 // 비디오 스트림 에러 처리
 document.getElementById('videoFeed').onerror = function() {
     setTimeout(() => {
         this.src = `{{ video_feed_url }}`;
     }, 1000);
 };