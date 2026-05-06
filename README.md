## 运行步骤

### 1. 创建数据库（MySQL）
进入 MySQL：
mysql -u root -p

执行：
CREATE DATABASE library_db DEFAULT CHARSET utf8mb4;

### 2. 安装依赖
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

### 3. 修改 config.py
把 DB_PASSWORD 改成你的 root 密码

### 4. 启动
python app.py

浏览器打开：
http://127.0.0.1:5000

管理员默认账号：
admin / admin123
