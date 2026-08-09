-- Railway 用建表檔（無 CREATE DATABASE / USE，無 # 行內註解）
-- 請整份貼到 MySQL Query 或 Console 執行

CREATE TABLE teacher (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    student_name VARCHAR(50) NOT NULL,
    password_changed BOOLEAN DEFAULT FALSE,
    total_xp INT UNSIGNED DEFAULT 0,
    total_coin INT UNSIGNED DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
);

CREATE TABLE pet_stage (
    stage_id INT AUTO_INCREMENT PRIMARY KEY,
    stage_name VARCHAR(50) NOT NULL,
    xp_threshold INT NOT NULL,
    image_url VARCHAR(255),
    stage_order INT NOT NULL
);

CREATE TABLE pet (
    pet_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    stage_id INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (stage_id) REFERENCES pet_stage(stage_id)
);

CREATE TABLE practice_upload (
    upload_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    audio_url VARCHAR(255) NOT NULL,
    song_name VARCHAR(255) NOT NULL,
    audio_duration INT UNSIGNED NOT NULL COMMENT 'seconds',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    INDEX idx_student_created (student_id, created_at)
);

CREATE TABLE quest_list (
    quest_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    quest_name VARCHAR(100) NOT NULL,
    quest_type ENUM('DAILY', 'WEEKLY', 'HIDDEN') NOT NULL,
    condition_type ENUM(
        'PRACTICE_COUNT',
        'PRACTICE_DAYS',
        'DISTINCT_SONGS',
        'CONSECUTIVE_DAYS',
        'TOTAL_UPLOADS',
        'RETURN_AFTER_GAP'
    ) NOT NULL,
    condition_value INT NOT NULL,
    reward_xp INT NOT NULL DEFAULT 0,
    reward_coin INT NOT NULL DEFAULT 0,
    is_repeatable BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
);

CREATE TABLE student_quest (
    student_quest_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    quest_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL,
    period_key VARCHAR(20) NOT NULL,
    progress_value INT NOT NULL DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (quest_id) REFERENCES quest_list(quest_id),
    UNIQUE KEY uk_student_quest_period (student_id, quest_id, period_key),
    INDEX idx_student_period (student_id, period_key)
);

CREATE TABLE shop_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    item_type ENUM('VIRTUAL', 'PHYSICAL') NOT NULL,
    price INT UNSIGNED NOT NULL,
    stock INT UNSIGNED NULL,
    description VARCHAR(255),
    image_url VARCHAR(255) COMMENT 'item image',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
);

CREATE TABLE purchase_record (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    item_id INT NOT NULL,
    price INT UNSIGNED NOT NULL,
    status ENUM('OWNED', 'PURCHASED', 'REDEEMED') DEFAULT 'OWNED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (item_id) REFERENCES shop_item(item_id)
);

CREATE TABLE xp_source (
    xp_source_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    upload_id INT NULL COMMENT 'nullable when not from upload',
    xp_amount INT NOT NULL,
    source_type ENUM(
        'PRACTICE_UPLOAD',
        'QUEST_REWARD',
        'HIDDEN_QUEST',
        'TEACHER_ADJUST'
    ) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (upload_id) REFERENCES practice_upload(upload_id) ON DELETE SET NULL
);

CREATE TABLE coin_transaction (
    coin_transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    source_type ENUM(
        'PRACTICE_UPLOAD',
        'QUEST_REWARD',
        'HIDDEN_QUEST',
        'SHOP_PURCHASE',
        'TEACHER_ADJUST'
    ) NOT NULL,
    amount INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);

INSERT INTO pet_stage (stage_name, xp_threshold, stage_order, image_url) VALUES
('蛋', 0, 1, NULL),
('幼體', 100, 2, NULL),
('成體', 500, 3, NULL),
('稀有型態', 1500, 4, NULL);
