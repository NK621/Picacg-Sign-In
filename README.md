---

# **哔咔自动签到脚本**

本项目是一个用于哔咔漫画平台的自动签到脚本。它支持多账号签到、随机设备 ID 生成、邮件通知，并优化为可在 GitHub Actions 中运行。

---

## **功能特点**
- **自动登录与签到**：自动完成账户的登录和每日打卡任务。
- **多账号支持**：支持一次配置多个账号。
- **随机设备 UUID**：避免因重复设备导致封号风险。
- **邮件通知**：将签到结果通过邮件发送到指定邮箱。
- **GitHub Actions 集成**：支持自动化运行与定时任务。

---

## **使用说明**

### **1. 克隆项目**
```bash
git clone https://github.com/your-username/pica-sign-in.git
cd pica-sign-in
```

### **2. 环境依赖**
- Python 3.7+
- 安装所需库：
  ```bash
  pip install -r requirements.txt
  ```

### **3. 配置环境变量**
#### **必需环境变量**
在运行脚本前，请配置以下环境变量：

- **`ACCOUNT_LIST`**：账号列表，格式为：
  ```
  用户名1:密码1,用户名2:密码2,用户名3:密码3
  ```
  例如：
  ```
  user1@example.com:password1,user2@example.com:password2
  ```

- **`EMAIL_CONFIG`**：邮件配置，JSON 格式，示例如下：
  ```json
  {
    "smtp_server": "smtp.example.com",
    "port": 465,
    "sender_email": "your_email@example.com",
    "password": "your_email_password",
    "receiver_email": "receiver_email@example.com"
  }
  ```

### **4. 本地运行**
运行脚本：
```bash
ACCOUNT_LIST="user1@example.com:password1,user2@example.com:password2" \
EMAIL_CONFIG='{"smtp_server":"smtp.example.com","port":465,"sender_email":"your_email@example.com","password":"your_email_password","receiver_email":"receiver_email@example.com"}' \
python script.py
```

---

## **GitHub Actions 配置**

### **1. 添加 GitHub Secrets**
在项目的 GitHub 仓库中，进入 **Settings > Secrets and variables > Actions**，添加以下 Secrets：
- `ACCOUNT_LIST`：账号列表，例如 `user1@example.com:password1,user2@example.com:password2`。
- `EMAIL_CONFIG`：邮件配置，JSON 字符串形式。

### **2. 创建工作流文件**
在项目根目录下创建 `.github/workflows/pica-sign-in.yml` 文件，内容如下：

```yaml
name: 哔咔自动签到

on:
  schedule:
    - cron: '0 6 * * *' # 定时任务，修改为你需要的时间

jobs:
  sign_in:
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v3

      - name: 设置 Python 环境
        uses: actions/setup-python@v3
        with:
          python-version: 3.9

      - name: 安装依赖
        run: pip install httpx

      - name: 执行签到脚本
        env:
          ACCOUNT_LIST: ${{ secrets.ACCOUNT_LIST }}
          EMAIL_CONFIG: ${{ secrets.EMAIL_CONFIG }}
        run: python script.py
```

---

## **自定义功能**

- **随机延迟**：脚本在每个账号间引入随机延迟（5-10秒），模拟人工操作，降低被封风险。
- **邮件通知**：可自定义 `EMAIL_CONFIG` 配置，支持大部分邮件服务提供商（如 QQ 邮箱、Gmail 等）。

---

## **常见问题**
### **1. 登录失败**
- 确保账号和密码在 `ACCOUNT_LIST` 中填写正确。
- 对于邮件服务，确认 SMTP 密码或授权码配置正确。

### **2. GitHub Actions 执行失败**
- 检查是否正确配置了 `Secrets` 中的环境变量。
- 在 Actions 日志中查看详细的错误信息。

### **3. 邮件未接收**
- 确认 `EMAIL_CONFIG` 中的 SMTP 服务器、端口及凭据正确无误。
- 检查垃圾邮件文件夹或邮箱服务商的屏蔽规则。

---

## **免责声明**
本脚本仅供个人学习和研究使用，过度使用可能导致账号封禁或其他限制。请自行承担使用风险。

---

## **贡献指南**
欢迎提交问题反馈、功能建议或 Pull Request 一起完善此项目！

---

## **许可证**
本项目采用 [MIT License](LICENSE) 开源许可证。

---

### **作者**
[Suta](https://github.com/ilhmtfmlt2)

---
