from flask import Flask, render_template, request, jsonify
import datetime
from ai_service import ai_service  # 导入AI服务
from chat_storage import chat_storage  # 导入聊天记录存储服务

app = Flask(__name__)

# 存储消息的列表（内存中临时存储）
messages = []

# 面试状态
interview_started = False

@app.route('/')
def index():
    # 获取当前时间，格式化为HH:MM
    current_time = datetime.datetime.now().strftime('%H:%M')
    
    # 创建新会话或获取当前会话ID
    session_id = chat_storage.get_current_session_id()
    
    # 清空消息列表，确保初始状态只显示系统消息
    messages.clear()
    
    # 返回渲染模板
    return render_template('index.html', 
                          messages=messages, 
                          current_time=current_time,
                          interview_started=interview_started)

@app.route('/send_message', methods=['POST'])
def send_message():
    global interview_started
    data = request.json
    message = data.get('message', '')
    session_id = chat_storage.get_current_session_id()
    
    # 添加用户消息到列表，记录时间戳
    user_timestamp = datetime.datetime.now()
    messages.append({
        'sender': 'user',
        'content': message,
        'timestamp': user_timestamp
    })
    
    # 保存到持久化存储
    chat_storage.add_message(
        session_id,
        'user',
        message,
        user_timestamp.isoformat()
    )
    
    # 获取AI回复
    if interview_started:
        hr_reply = ai_service.get_ai_response(message)
    else:
        # 如果面试未开始，使用默认回复
        hr_reply = "感谢您的回复！我们会尽快处理您的问题。"
    
    # 添加HR回复到列表，确保时间戳比用户消息晚1秒
    hr_timestamp = user_timestamp + datetime.timedelta(seconds=1)
    messages.append({
        'sender': 'hr',
        'content': hr_reply,
        'timestamp': hr_timestamp
    })
    
    # 保存到持久化存储
    chat_storage.add_message(
        session_id,
        'hr',
        hr_reply,
        hr_timestamp.isoformat()
    )
    
    # 每次回复后评估候选人兴趣度并保存
    if interview_started:
        interest_evaluation = ai_service.evaluate_interest()
        chat_storage.update_interest_evaluation(session_id, interest_evaluation)
    
    return jsonify({'status': 'success', 'reply': hr_reply})

@app.route('/accept_interview', methods=['POST'])
def accept_interview():
    global interview_started
    
    # 清空之前的消息
    messages.clear()
    
    # 创建新的会话
    session_id = chat_storage.create_session()
    
    # 用户接受面试的消息，记录时间戳
    user_timestamp = datetime.datetime.now()
    user_message = {
        'sender': 'user',
        'content': "我同意沟通，请告诉我更多关于这个职位的信息。",
        'timestamp': user_timestamp
    }
    
    # 将用户消息添加到消息列表
    messages.append(user_message)
    
    # 保存用户消息到持久化存储
    chat_storage.add_message(
        session_id,
        'user',
        "我同意沟通，请告诉我更多关于这个职位的信息。",
        user_timestamp.isoformat()
    )
    
    # 启动面试模式
    interview_started = True
    
    # 获取AI的初始问候语
    hr_welcome_message = ai_service.start_interview()
    hr_timestamp = datetime.datetime.now()
    
    # HR消息对象
    hr_message = {
        'sender': 'hr',
        'content': hr_welcome_message,
        'timestamp': hr_timestamp
    }
    
    # 保存HR消息到持久化存储
    chat_storage.add_message(
        session_id,
        'hr',
        hr_welcome_message,
        hr_timestamp.isoformat()
    )
    
    # 返回两条消息给前端
    return jsonify({
        'status': 'success', 
        'messages': [user_message, hr_message]
    })

@app.route('/history', methods=['GET'])
def get_history():
    """获取历史会话列表"""
    sessions = chat_storage.list_sessions()
    
    # 为每个会话添加兴趣度评估信息
    for session in sessions:
        session_id = session['session_id']
        interest_evaluation = chat_storage.get_interest_evaluation(session_id)
        session['interest_level'] = interest_evaluation['interest_level']
        session['interest_score'] = interest_evaluation['score']
    
    return jsonify(sessions)

@app.route('/history/<session_id>', methods=['GET'])
def get_session_messages(session_id):
    """获取指定会话的消息记录"""
    messages = chat_storage.get_messages(session_id)
    interest_evaluation = chat_storage.get_interest_evaluation(session_id)
    
    if not messages:
        return jsonify({'error': '找不到指定的会话记录'}), 404
    
    return jsonify({
        'messages': messages,
        'interest_evaluation': interest_evaluation
    })

if __name__ == '__main__':
    app.run(debug=True)
