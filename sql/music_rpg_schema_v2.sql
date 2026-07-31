-- 
CREATE DATABASE IF NOT EXISTS music_rpg_v2
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE music_rpg_v2;

-- ============================================
-- 老師
-- ============================================
CREATE TABLE teacher (
    teacher_id   	INT AUTO_INCREMENT PRIMARY KEY, # 老師id
    teacher_name    VARCHAR(50) NOT NULL, # 老師姓名
    email        	VARCHAR(100) NOT NULL UNIQUE, # 老師email = 帳號
	password_hash 	VARCHAR(255) NOT NULL, # 老師的密碼
    created_at   	TIMESTAMP DEFAULT CURRENT_TIMESTAMP #創建時間
);

-- ============================================
-- 學生
-- ============================================
CREATE TABLE student (
    student_id 			INT AUTO_INCREMENT PRIMARY KEY, #學生id
    teacher_id 			INT NOT NULL, #綁定的老師id
    username 			VARCHAR(50) NOT NULL UNIQUE, #學生帳號
    password_hash 		VARCHAR(255) NOT NULL, #學生密碼
    student_name 		VARCHAR(50)  NOT NULL, #學生的姓名
    password_changed 	BOOLEAN DEFAULT FALSE, #確認密碼是否修改過
    total_xp 			INT UNSIGNED DEFAULT 0,#學生累積經驗
	total_coin 		INT UNSIGNED DEFAULT 0,#學生持有貨幣
    created_at   		TIMESTAMP DEFAULT CURRENT_TIMESTAMP, #標註創立時間
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id) # 要有teacher.teacher_id 才能建立資料
);

-- ============================================
-- 寵物進化階段定義（先有規則資料才能建立寵物）
-- ============================================
CREATE TABLE pet_stage (
    stage_id     	INT AUTO_INCREMENT PRIMARY KEY,# 寵物進化階段的id
    stage_name   	VARCHAR(50) NOT NULL,# 寵物階段名稱
    xp_threshold 	INT NOT NULL,# 累積XP達此值時進化到此階段
    image_url    	VARCHAR(255),# 寵物階段照片路徑
    stage_order  	INT NOT NULL # 要輸入下一階段名稱來確定進化資料
);

-- ============================================
-- 寵物（每位學生一隻）
-- ============================================
CREATE TABLE pet (
    pet_id       INT AUTO_INCREMENT PRIMARY KEY,# 寵物的id，在思考有沒有需要，因為寵物綁定學生，那學生的id不是就都跟寵物id一樣
    student_id   INT NOT NULL UNIQUE,# 綁定的學生id
    stage_id     INT NOT NULL,# 對應進化階段的id
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,# 更新時間，隨著更動時間修改
    FOREIGN KEY (student_id) REFERENCES student(student_id),# 要有學生id才能建立資料，並且參考student(student_id)
    FOREIGN KEY (stage_id) REFERENCES pet_stage(stage_id)# 要有寵物階段id才能建立資料，並且參考pet_stage(stage_id)
);

-- ============================================
-- 練習錄音上傳紀錄（純紀錄上傳次數）
-- ============================================
CREATE TABLE practice_upload (
    upload_id    	INT AUTO_INCREMENT PRIMARY KEY,# 上傳紀錄流水號
    student_id   	INT NOT NULL,# 綁定的學生id
    audio_url    	VARCHAR(255) NOT NULL,# 上傳錄音的路徑
    song_name    	VARCHAR(255) NOT NULL,# 上傳檔案的曲名
    audio_duration 	INT UNSIGNED NOT NULL COMMENT '秒數', # 紀錄上傳檔案秒數供老師判斷
    created_at  	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,# 資料新增日期
    FOREIGN KEY (student_id) REFERENCES student(student_id),# 要有學生id才能建立資料，並且參考student(student_id)
    INDEX idx_student_created (student_id, created_at)# 增加複合索引
);
# UNSIGNED不能為負數
-- ============================================
-- 任務清單（所有任務資料）
-- ============================================
CREATE TABLE quest_list (
    quest_id INT AUTO_INCREMENT PRIMARY KEY, # 任務流水號
    teacher_id INT NOT NULL, # 建立任務者
    quest_name VARCHAR(100) NOT NULL, # 任務名稱
    quest_type ENUM(
        'DAILY',#每日任務
        'WEEKLY',#每週任務
        'HIDDEN'#隱藏成就
    ) NOT NULL, # 任務類型
    
    condition_type ENUM(
        'PRACTICE_COUNT',#練習次數
        'PRACTICE_DAYS',#練習天數
        'DISTINCT_SONGS',#不同歌曲
        'CONSECUTIVE_DAYS',#連續天數
        'TOTAL_UPLOADS',#上傳總數
        'RETURN_AFTER_GAP'#回歸上傳
    ) NOT NULL, # 任務條件類型
    
    condition_value INT NOT NULL, # 任務條件數值
    reward_xp INT NOT NULL DEFAULT 0, # 完成任務獎勵 XP
    reward_coin INT NOT NULL DEFAULT 0, # 完成任務獎勵貨幣
    is_repeatable BOOLEAN DEFAULT TRUE, # 是否可重複完成
    is_active BOOLEAN DEFAULT TRUE, # 任務是否啟用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, # 建立時間
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
);

-- ============================================
-- 學生任務進度（每週分配）
-- ============================================
CREATE TABLE student_quest (
    student_quest_id INT AUTO_INCREMENT PRIMARY KEY, # 學生任務紀錄流水號
    student_id INT NOT NULL, # 綁定學生 ID
    quest_id INT NOT NULL, # 綁定任務 ID
    period_key VARCHAR(20) NOT NULL, # 任務期間，例如 2026-07-13 / 2026-W29 / ONCE
    progress_value INT NOT NULL DEFAULT 0, # 目前完成進度
    completed BOOLEAN DEFAULT FALSE, # 是否完成
    completed_at TIMESTAMP NULL, # 完成時間
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, # 建立時間
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (quest_id) REFERENCES quest_list(quest_id),
    UNIQUE KEY uk_student_quest_period (student_id, quest_id, period_key),
    INDEX idx_student_period (student_id, period_key)
);


-- ============================================
-- 商城
-- ============================================
CREATE TABLE shop_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,#商品流水號
    teacher_id INT NOT NULL,#商品由哪位老師建立
    item_name VARCHAR(100) NOT NULL,#商品名稱
    item_type ENUM('VIRTUAL', 'PHYSICAL') NOT NULL,#虛擬商品或實體商品
    price INT UNSIGNED NOT NULL,#商品價格
    stock INT UNSIGNED NULL,#商品庫存
    description VARCHAR(255),#商品說明
    image_url VARCHAR(255) COMMENT '商品圖片',
    is_active BOOLEAN DEFAULT TRUE,#是否上架
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,#建立時間
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
);

-- ============================================
-- 購買記錄
-- ============================================
CREATE TABLE purchase_record (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,#異動流水號
    student_id INT NOT NULL,#學生id
    item_id INT NOT NULL,#商品id
    price INT UNSIGNED NOT NULL,#購買當下價格
    status ENUM('OWNED','PURCHASED', 'REDEEMED') DEFAULT 'OWNED',#購買狀態:OWNED虛擬商品已兌換、PURCHASED已購買、REDEEMED已兌換
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,#購買時間
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (item_id) REFERENCES shop_item(item_id)
);


-- ============================================
-- 經驗值XP異動紀錄
-- ============================================
CREATE TABLE xp_source (
    xp_source_id   INT AUTO_INCREMENT PRIMARY KEY,#異動流水號
    student_id   		INT NOT NULL,# 綁定學生id
    upload_id    		INT NULL COMMENT '由練習上傳觸發時記錄 upload_id；隱藏任務可為 NULL', #可為NULL(例如任務獎勵觸發，非上傳觸發)
    xp_amount    		INT NOT NULL,#本次變動經驗值
    source_type ENUM(
        'PRACTICE_UPLOAD',#上傳獲得
        'QUEST_REWARD',#一般任務獲得
        'HIDDEN_QUEST',#隱藏任務
        'TEACHER_ADJUST'#老師執行
    ) NOT NULL,#經驗異動原因，指定為這三種
    created_at   		TIMESTAMP DEFAULT CURRENT_TIMESTAMP,#變動時間
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (upload_id) REFERENCES practice_upload(upload_id) ON DELETE SET NULL
);

-- ============================================
-- 貨幣異動紀錄
-- ============================================
CREATE TABLE coin_transaction (
    coin_transaction_id   INT AUTO_INCREMENT PRIMARY KEY,#異動流水號
    student_id   INT          NOT NULL,#綁定學生id
    source_type ENUM(
        'PRACTICE_UPLOAD',#上傳獲得
        'QUEST_REWARD',#一班任務獲得
        'HIDDEN_QUEST',#隱藏任務
        'SHOP_PURCHASE',#商店購物
        'TEACHER_ADJUST'#老師給予
    ) NOT NULL,# 貨幣異動原因
    amount       INT          NOT NULL,#貨幣計算正數增加負數減少
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,#異動時間
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);

-- ============================================
-- 預設資料輸入
-- ============================================
INSERT INTO pet_stage (stage_name, xp_threshold, stage_order, image_url) VALUES
('蛋',      0,   1, NULL),
('幼體',    100, 2, NULL),
('成體',    500, 3, NULL),
('稀有型態', 1500, 4, NULL);

select * from teacher;

INSERT INTO quest_list
(
    teacher_id,
    quest_name,
    quest_type,
    condition_type,
    condition_value,
    reward_xp,
    reward_coin,
    is_repeatable
)
VALUES
(1,'今日初次練習','DAILY','PRACTICE_COUNT',1,20,5,TRUE),
(1,'今日練習三次','DAILY','PRACTICE_COUNT',3,50,10,TRUE),
(1,'本週練習三天','WEEKLY','PRACTICE_DAYS',3,100,20,TRUE),
(1,'本週挑戰三首曲目','WEEKLY','DISTINCT_SONGS',3,100,20,TRUE),
(1,'持之以恆','HIDDEN','CONSECUTIVE_DAYS',7,200,50,FALSE),
(1,'練習達人','HIDDEN','TOTAL_UPLOADS',30,300,100,FALSE),
(1,'歡迎回來','HIDDEN','RETURN_AFTER_GAP',7,100,30,TRUE);