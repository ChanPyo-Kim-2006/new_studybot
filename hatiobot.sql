studybot-- 기존 데이터베이스가 있다면 삭제
DROP DATABASE IF EXISTS studybot;

-- 데이터베이스 생성
CREATE DATABASE studybot;
USE studybot;

-- 사용자(자녀) 테이블
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_username (username),
    UNIQUE KEY unique_email (email)
);

-- 얼굴 특징점 테이블 수정
CREATE TABLE face_landmarks (
    landmark_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    landmarks TEXT NOT NULL,
    child_code VARCHAR(20) NOT NULL UNIQUE,  -- 자녀 코드
    region VARCHAR(100) NOT NULL,  -- 지역명 추가
    school_name VARCHAR(100) NOT NULL,  -- 학교명 추가
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_face_landmarks_user (user_id),
    INDEX idx_child_code (child_code),
    INDEX idx_region (region),  -- 지역 검색을 위한 인덱스
    INDEX idx_school_name (school_name)  -- 학교 검색을 위한 인덱스
);


-- 로그인 기록 테이블
CREATE TABLE login_history (
    login_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    login_success BOOLEAN NOT NULL,
    login_method ENUM('FACE', 'OTHER') DEFAULT 'FACE',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_login_history_user (user_id)
);

-- 부모 테이블
CREATE TABLE parents (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_parent_username (username),
    UNIQUE KEY unique_parent_email (email)
);

-- 부모-자녀 연결 테이블 수정
CREATE TABLE parent_child (
    parent_id INT,
    child_code VARCHAR(20),  -- landmark_id 대신 child_code 사용
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (parent_id, child_code),
    FOREIGN KEY (parent_id) REFERENCES parents(parent_id),
    FOREIGN KEY (child_code) REFERENCES face_landmarks(child_code),
    INDEX idx_parent_child (parent_id, child_code)
);

-- 집중도 기록 테이블
CREATE TABLE concentration_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    concentration_score INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    gaze_status VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_concentration_user (user_id)
);

-- 학습 세션 테이블
CREATE TABLE study_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    total_duration INT,  -- 분 단위
    avg_concentration FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_study_sessions_user (user_id)
);