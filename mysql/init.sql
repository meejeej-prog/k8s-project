CREATE USER 'jiwon'@'%' IDENTIFIED WITH mysql_native_password BY '1234';
GRANT ALL PRIVILEGES ON *.* TO 'jiwon'@'%' WITH GRANT OPTION;
CREATE USER 'repl_user'@'%' IDENTIFIED WITH mysql_native_password BY '1234';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS exam;

USE exam;

CREATE TABLE IF NOT EXISTS exam_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,          -- 자격증 종류 구분
    cert_name VARCHAR(100) NOT NULL,        -- 자격증 이름
    regist_start_date DATE NOT NULL,        -- 접수 시작일
    regist_end_date DATE NOT NULL,          -- 접수 종료일
    exam_start_date DATE NOT NULL,          -- 시험 시작일
    exam_end_date DATE NOT NULL,            -- 시험 종료일
    result_start_date DATE NOT NULL,        -- 결과 확인 시작일
    result_end_date DATE NOT NULL,          -- 결과 확인 종료일
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO exam_info (category, cert_name, regist_start_date, regist_end_date, exam_start_date, exam_end_date, result_start_date, result_end_date)
VALUES
('Network', 'CCNA', '2025-12-31', '2026-01-07', '2026-01-10', '2026-01-15', '2026-01-20', '2026-01-25'),
('Network', 'Network+', '2026-01-22', '2026-01-29', '2026-02-01', '2026-02-05', '2026-02-10', '2026-02-15'),
('Network', 'CCNP', '2026-02-23', '2026-03-02', '2026-03-05', '2026-03-10', '2026-03-15', '2026-03-20'),
('Linux', 'LPIC1', '2025-12-31', '2026-01-09', '2026-01-12', '2026-01-18', '2026-01-22', '2026-01-27'),
('Linux', 'RHCSA', '2026-01-22', '2026-01-30', '2026-02-03', '2026-02-08', '2026-02-12', '2026-02-17'),
('Linux', 'Linux+', '2026-02-25', '2026-03-04', '2026-03-07', '2026-03-12', '2026-03-17', '2026-03-22'),
('Cloud', 'AWS', '2026-03-22', '2026-03-28', '2026-04-01', '2026-04-05', '2026-04-10', '2026-04-15'),
('Cloud', 'GCP', '2026-04-21', '2026-04-27', '2026-05-01', '2026-05-05', '2026-05-10', '2026-05-15'),
('Cloud', 'Azure', '2026-05-22', '2026-05-28', '2026-06-01', '2026-06-05', '2026-06-10', '2026-06-15'),
('Database', 'OCP', '2026-01-05', '2026-01-12', '2026-01-15', '2026-01-20', '2026-01-25', '2026-01-30'),
('Database', 'MySQL', '2026-01-31', '2026-02-07', '2026-02-10', '2026-02-15', '2026-02-20', '2026-02-25'),
('Database', 'Postgres', '2026-02-23', '2026-03-02', '2026-03-05', '2026-03-10', '2026-03-15', '2026-03-20'),
('Kubernetes', 'CKA', '2026-03-31', '2026-04-07', '2026-04-10', '2026-04-15', '2026-04-20', '2026-04-25'),
('Kubernetes', 'CKAD', '2026-04-21', '2026-04-27', '2026-05-01', '2026-05-05', '2026-05-10', '2026-05-15'),
('Kubernetes', 'CKS', '2026-05-22', '2026-05-28', '2026-06-01', '2026-06-05', '2026-06-10', '2026-06-15'),
('Terraform', 'TF-Associate', '2026-01-10', '2026-01-17', '2026-01-20', '2026-01-25', '2026-01-30', '2026-02-05'),
('Terraform', 'TF-Pro', '2026-02-05', '2026-02-12', '2026-02-15', '2026-02-20', '2026-02-25', '2026-03-01'),
('Terraform', 'TF-Adv', '2026-03-01', '2026-03-07', '2026-03-10', '2026-03-15', '2026-03-20', '2026-03-25'),
('CI/CD', 'Jenkins', '2026-01-15', '2026-01-22', '2026-01-25', '2026-01-30', '2026-02-05', '2026-02-10'),
('CI/CD', 'GitLab', '2026-02-10', '2026-02-17', '2026-02-20', '2026-02-25', '2026-03-02', '2026-03-07'),
('CI/CD', 'AWS-DevOps', '2026-03-05', '2026-03-12', '2026-03-15', '2026-03-20', '2026-03-25', '2026-03-30');

CREATE DATABASE IF NOT EXISTS candidate;
USE candidate;
