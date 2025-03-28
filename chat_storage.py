import os
import json
import datetime
import uuid
from typing import List, Dict, Any, Optional

class ChatStorage:
    """聊天记录存储类，负责保存和检索聊天记录"""
    
    def __init__(self):
        """初始化存储系统"""
        self.storage_dir = 'chat_history'
        self.ensure_storage_dir()
        self.current_session_id = None
        
    def ensure_storage_dir(self):
        """确保存储目录存在"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            
    def create_session(self) -> str:
        """创建新的聊天会话，返回会话ID"""
        session_id = str(uuid.uuid4())
        self.current_session_id = session_id
        session_data = {
            'session_id': session_id,
            'created_at': datetime.datetime.now().isoformat(),
            'messages': [],
            'interest_evaluation': {
                'interest_level': '未知',
                'score': 0,
                'confidence': 0,
                'reasons': ['对话尚未开始'],
                'message_count': 0,
                'updated_at': datetime.datetime.now().isoformat()
            }
        }
        self.save_session(session_id, session_data)
        return session_id
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]):
        """保存会话数据到文件"""
        file_path = os.path.join(self.storage_dir, f"{session_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
            
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """加载会话数据"""
        file_path = os.path.join(self.storage_dir, f"{session_id}.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_message(self, session_id: str, sender: str, content: str, timestamp=None):
        """添加新消息到会话"""
        if not timestamp:
            timestamp = datetime.datetime.now().isoformat()
            
        session_data = self.load_session(session_id)
        if not session_data:
            return False
            
        message = {
            'sender': sender,
            'content': content,
            'timestamp': timestamp
        }
        
        session_data['messages'].append(message)
        session_data['updated_at'] = datetime.datetime.now().isoformat()
        
        self.save_session(session_id, session_data)
        return True
    
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话的所有消息"""
        session_data = self.load_session(session_id)
        if not session_data:
            return []
            
        return session_data['messages']
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话的基本信息"""
        sessions = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        'session_id': data.get('session_id'),
                        'created_at': data.get('created_at'),
                        'updated_at': data.get('updated_at', data.get('created_at')),
                        'message_count': len(data.get('messages', []))
                    })
        
        # 按更新时间排序，最新的在前
        sessions.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return sessions
    
    def get_current_session_id(self) -> str:
        """获取当前会话ID，如果没有则创建新会话"""
        if not self.current_session_id:
            self.current_session_id = self.create_session()
        return self.current_session_id
    
    def update_interest_evaluation(self, session_id: str, evaluation_data: dict):
        """更新会话的兴趣度评估结果"""
        session_data = self.load_session(session_id)
        if not session_data:
            return False
        
        # 添加更新时间
        evaluation_data['updated_at'] = datetime.datetime.now().isoformat()
        
        # 更新评估结果
        session_data['interest_evaluation'] = evaluation_data
        
        # 保存会话数据
        self.save_session(session_id, session_data)
        return True
    
    def get_interest_evaluation(self, session_id: str) -> dict:
        """获取会话的兴趣度评估结果"""
        session_data = self.load_session(session_id)
        if not session_data or 'interest_evaluation' not in session_data:
            return {
                'interest_level': '未知',
                'score': 0,
                'confidence': 0,
                'reasons': ['未找到评估数据'],
                'message_count': 0
            }
        
        return session_data['interest_evaluation']

# 创建全局实例
chat_storage = ChatStorage()
