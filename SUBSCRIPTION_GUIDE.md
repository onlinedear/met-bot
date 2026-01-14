# 📧 邮件订阅服务部署指南

如果你想让更多人订阅这个医疗情报服务，有以下几种方案：

## 方案一：使用 Google Groups（推荐，免费）

### 优点
- ✅ 完全免费
- ✅ 用户可以自助订阅/退订
- ✅ 支持无限订阅者
- ✅ 自动管理订阅列表

### 部署步骤

1. **创建 Google Groups**
   - 访问 [groups.google.com](https://groups.google.com)
   - 点击"创建群组"
   - 填写信息：
     - 群组名称：`幼年皮肌炎医疗情报订阅`
     - 群组邮箱：`jdm-medical-intel@googlegroups.com`（示例）
     - 群组类型：选择"邮件列表"

2. **配置群组设置**
   - 进入群组设置
   - "谁可以加入群组"：选择"任何人都可以申请"
   - "谁可以查看对话"：选择"群组成员"
   - "谁可以发帖"：选择"群组所有者"（只有你能发送）

3. **修改机器人配置**
   - 在 GitHub Secrets 中设置：
   ```
   EMAIL_RECEIVER=jdm-medical-intel@googlegroups.com
   ```

4. **用户订阅方式**
   - 用户发送邮件到：`jdm-medical-intel+subscribe@googlegroups.com`
   - 或访问群组页面点击"加入群组"

---

## 方案二：使用 Mailchimp（适合大规模）

### 优点
- ✅ 专业的邮件营销平台
- ✅ 免费版支持 500 订阅者
- ✅ 提供订阅表单和管理后台
- ✅ 详细的统计数据

### 部署步骤

1. **注册 Mailchimp**
   - 访问 [mailchimp.com](https://mailchimp.com)
   - 注册免费账号

2. **创建受众列表**
   - 创建新的 Audience（受众）
   - 设置列表名称和默认发件信息

3. **获取 API 集成**
   - 需要修改代码，通过 Mailchimp API 发送邮件
   - 或使用 Mailchimp 的 SMTP 服务器

---

## 方案三：使用文件管理订阅列表

如果订阅人数不多（<100人），可以用文件管理：

### 实现方式

1. **创建订阅列表文件**
   在仓库中创建 `subscribers.txt`：
   ```
   user1@example.com
   user2@example.com
   user3@example.com
   ```

2. **修改代码读取文件**
   ```python
   # 读取订阅列表
   with open('subscribers.txt', 'r') as f:
       subscribers = [line.strip() for line in f if line.strip()]
   
   EMAIL_RECEIVER = ','.join(subscribers)
   ```

3. **添加新订阅者**
   - 用户提交 Issue 或 PR 添加自己的邮箱
   - 或者你手动添加到文件中

---

## 方案四：使用 Telegram 频道（最简单）

### 优点
- ✅ 完全免费
- ✅ 用户自助订阅（点击加入即可）
- ✅ 支持无限订阅者
- ✅ 推送更及时

### 部署步骤

1. **创建 Telegram 公开频道**
   - 打开 Telegram
   - 创建新频道
   - 设置为公开频道
   - 设置频道链接，如：`@jdm_medical_intel`

2. **将 Bot 添加为管理员**
   - 将你的 Bot 添加到频道
   - 给予发送消息权限

3. **获取频道 ID**
   - 在频道发送消息
   - 访问 `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - 找到频道 ID（通常是 `-100` 开头的负数）

4. **修改配置**
   ```
   TELEGRAM_CHAT_ID=-1001234567890  # 你的频道 ID
   ```

5. **分享频道链接**
   - 用户访问 `https://t.me/jdm_medical_intel` 即可订阅

---

## 推荐方案对比

| 方案 | 免费额度 | 易用性 | 自助订阅 | 推荐指数 |
|------|---------|--------|---------|---------|
| Google Groups | 无限 | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ |
| Telegram 频道 | 无限 | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ |
| Mailchimp | 500人 | ⭐⭐⭐ | ✅ | ⭐⭐⭐ |
| 文件管理 | 无限 | ⭐⭐ | ❌ | ⭐⭐ |

## 最佳实践建议

**如果订阅者主要在国内：**
- 使用 **Telegram 频道** + **邮件列表** 双渠道
- Telegram 更及时，邮件作为备份

**如果订阅者主要在国外：**
- 使用 **Google Groups**，最简单方便

**如果需要详细统计：**
- 使用 **Mailchimp**，可以看到打开率、点击率等数据
