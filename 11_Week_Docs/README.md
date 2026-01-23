# 飞书周报汇总工具

这是一个使用Python编写的飞书周报汇总工具，可以自动获取同事发给你的周报消息，并将其汇总生成到飞书文档中。

## 功能特点

- ✅ 自动获取指定时间段内的飞书聊天记录
- ✅ 智能识别周报内容（支持关键词过滤）
- ✅ 自动汇总周报内容到飞书文档
- ✅ 生成可分享的文档链接
- ✅ 支持配置文件，无需修改代码

## 环境要求

- Python 3.6+
- requests库

## 安装依赖

```bash
pip install requests
```

## 使用步骤

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录后，点击「创建企业自建应用」
3. 填写应用基本信息，点击「创建」
4. 在应用详情页，记录下「App ID」和「App Secret」

### 2. 配置应用权限

1. 在应用详情页，点击「权限管理」
2. 添加以下权限：
   - 消息与群组 > 获取与发送单聊、群组消息
   - 消息与群组 > 以应用身份读取消息
   - 通讯录 > 获取用户信息
   - 文档 > 文档内容读写
   - 文档 > 文档权限管理

### 3. 获取Chat ID

1. 在飞书中，打开你要获取消息的聊天窗口
2. 点击右上角「设置」图标
3. 点击「查看聊天信息」
4. 复制「聊天ID」

### 4. 配置应用

1. 复制 `config_example.json` 为 `config.json`
2. 编辑 `config.json` 文件，填写以下信息：
   - `app_id`: 你的飞书应用App ID
   - `app_secret`: 你的飞书应用App Secret
   - `chat_id`: 你要获取消息的聊天ID
   - `days`: 要获取的天数（默认为7天）

### 5. 运行代码

```bash
python feishu_weekly_report.py
```

## 配置说明

| 配置项 | 说明 | 必填 | 默认值 |
|-------|------|------|--------|
| app_id | 飞书应用App ID | 是 | 无 |
| app_secret | 飞书应用App Secret | 是 | 无 |
| chat_id | 聊天ID | 是 | 无 |
| days | 要获取的天数 | 否 | 7 |

## 注意事项

1. 确保你的飞书应用已经获得了所有必要的权限
2. 确保你有足够的权限访问指定的聊天记录
3. 周报识别是基于关键词的简单匹配，你可以根据实际情况修改代码中的关键词列表
4. 生成的文档默认对租户内所有用户可见，你可以根据需要修改文档权限

## 代码结构

```
feishu_weekly_report.py
├── FeishuWeeklyReport 类
│   ├── get_access_token() - 获取访问凭证
│   ├── get_chat_history() - 获取聊天记录
│   ├── get_user_info() - 获取用户信息
│   ├── extract_weekly_reports() - 提取周报内容
│   ├── create_document() - 创建飞书文档
│   ├── share_document() - 获取分享链接
│   └── summarize_weekly_reports() - 汇总周报
└── load_config() - 加载配置文件
```

## 常见问题

### Q: 如何修改周报识别的关键词？
A: 在 `extract_weekly_reports()` 方法中，修改关键词列表：
```python
if any(keyword in text for keyword in ["周报", "工作总结", "工作汇报", "weekly report"]):
```

### Q: 如何修改文档的权限？
A: 在 `share_document()` 方法中，修改权限设置：
```python
data = {
    "members": [
        {
            "member_type": "tenant",
            "member_id": "all",
            "perm": "view"
        }
    ]
}
```

### Q: 如何获取更多的聊天记录？
A: 当前代码默认每次获取100条消息，你可以修改 `get_chat_history()` 方法中的 `limit` 参数，或添加分页逻辑获取更多消息。

## 许可证

MIT License
