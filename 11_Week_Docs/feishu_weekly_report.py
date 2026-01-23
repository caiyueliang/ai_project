#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime, timedelta

class FeishuWeeklyReport:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expire_time = 0
        self.base_url = "https://open.feishu.cn/open-apis"
    
    def get_access_token(self):
        """获取飞书API访问凭证"""
        current_time = int(time.time())
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get("code") == 0:
            self.access_token = result["tenant_access_token"]
            self.token_expire_time = current_time + result["expire"] - 300  # 提前5分钟刷新
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {result}")
    
    def get_chat_history(self, chat_id, start_time, end_time):
        """获取指定时间段内的聊天记录"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "container_id": chat_id,
            "container_type": "chat",
            "start_time": start_time,
            "end_time": end_time,
            "direction": "up",
            "limit": 100
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get("code") == 0:
            return result["data"]["items"]
        else:
            raise Exception(f"获取聊天记录失败: {result}")
    
    def get_user_info(self, user_id):
        """获取用户信息"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/contact/v3/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get("code") == 0:
            return result["data"]["user"]
        else:
            raise Exception(f"获取用户信息失败: {result}")
    
    def extract_weekly_reports(self, messages):
        """从消息中提取周报内容"""
        weekly_reports = []
        
        for message in messages:
            if message["message_type"] == "text":
                content = json.loads(message["content"])
                text = content["text"]
                
                # 简单判断是否为周报（可根据实际情况调整）
                if any(keyword in text for keyword in ["周报", "工作总结", "工作汇报", "weekly report"]):
                    sender_id = message["sender"]["sender_id"]["user_id"]
                    sender_info = self.get_user_info(sender_id)
                    sender_name = sender_info["name"]
                    
                    weekly_reports.append({
                        "sender": sender_name,
                        "sender_id": sender_id,
                        "content": text,
                        "send_time": datetime.fromtimestamp(message["create_time"])
                    })
        
        return weekly_reports
    
    def create_document(self, title, content):
        """创建飞书文档"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/docx/v1/documents"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 构建文档内容
        doc_content = {
            "title": title,
            "content": [
                {
                    "header": {
                        "level": 1,
                        "content": [
                            {"text": title}
                        ]
                    }
                },
                {
                    "paragraph": {
                        "elements": [
                            {"text": f"汇总时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
                        ]
                    }
                }
            ]
        }
        
        # 添加每个周报
        for report in content:
            doc_content["content"].append({
                "header": {
                    "level": 2,
                    "content": [
                        {"text": f"{report['sender']} 的周报"}
                    ]
                }
            })
            doc_content["content"].append({
                "header": {
                    "level": 3,
                    "content": [
                        {"text": f"发送时间：{report['send_time'].strftime('%Y-%m-%d %H:%M:%S')}"}
                    ]
                }
            })
            doc_content["content"].append({
                "paragraph": {
                    "elements": [
                        {"text": report['content']}
                    ]
                }
            })
        
        response = requests.post(url, headers=headers, json=doc_content)
        result = response.json()
        
        if result.get("code") == 0:
            return result["data"]["document_id"]
        else:
            raise Exception(f"创建文档失败: {result}")
    
    def share_document(self, document_id):
        """获取文档分享链接"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/docx/v1/documents/{document_id}/permission/members/batch_create"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 设置文档为可分享
        data = {
            "members": [
                {
                    "member_type": "tenant",
                    "member_id": "all",
                    "perm": "view"
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"设置文档权限失败: {result}")
        
        # 获取分享链接
        url = f"{self.base_url}/docx/v1/documents/{document_id}/share_link"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "share_mode": "tenant"
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get("code") == 0:
            return result["data"]["share_url"]
        else:
            raise Exception(f"获取分享链接失败: {result}")
    
    def summarize_weekly_reports(self, chat_id, days=7):
        """汇总指定天数内的周报"""
        # 计算时间范围
        end_time = int(time.time())
        start_time = end_time - days * 24 * 3600
        
        # 获取聊天记录
        messages = self.get_chat_history(chat_id, start_time, end_time)
        
        # 提取周报
        weekly_reports = self.extract_weekly_reports(messages)
        
        if not weekly_reports:
            print("未找到周报")
            return None
        
        # 创建汇总文档
        title = f"周报汇总 - {datetime.now().strftime('%Y-%m-%d')}"
        document_id = self.create_document(title, weekly_reports)
        
        # 获取分享链接
        share_url = self.share_document(document_id)
        
        print(f"周报汇总完成！")
        print(f"文档ID: {document_id}")
        print(f"分享链接: {share_url}")
        
        return {
            "document_id": document_id,
            "share_url": share_url,
            "report_count": len(weekly_reports)
        }

def load_config(config_path="config.json"):
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    try:
        # 加载配置文件
        config = load_config()
        
        # 初始化飞书周报汇总工具
        feishu = FeishuWeeklyReport(config["app_id"], config["app_secret"])
        
        # 汇总指定天数内的周报
        result = feishu.summarize_weekly_reports(config["chat_id"], days=config.get("days", 7))
    except FileNotFoundError:
        print("配置文件 config.json 未找到，请根据 config_example.json 创建配置文件")
    except KeyError as e:
        print(f"配置文件缺少必要字段: {e}")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")