import os
import json
import requests
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()

class AIService:
    """大模型服务接口类，用于与不同的AI服务提供商交互"""
    
    def __init__(self):
        """初始化AI服务"""
        self.api_type = os.getenv('AI_API_TYPE', 'zhipu')  # 默认使用智谱AI
        
        # 加载API密钥
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY')
        
        # 初始化智谱AI客户端
        if self.api_type == 'zhipu' and self.zhipu_api_key:
            self.zhipu_client = ZhipuAI(api_key=self.zhipu_api_key)
        
        # 初始化对话历史
        self.conversation_history = []
        
        # 初始化HR面试官提示词
        self.hr_system_prompt = """
        你是一位经验丰富的HR招聘专员，名叫Jesse范，就职于淘天集团。
        你在人才库中发现了一位技术背景匹配的前端开发工程师候选人，准备主动联系并邀请他/她参加面试。
        
        以下是你正在招聘的职位详情：
        
        【职位名称】资深前端开发工程师
        【工作地点】北京/上海/杭州
        【薪资范围】25K-50K，14薪，年终奖金

        【职位描述】
        作为淘天集团技术部前端团队的核心成员，您将参与建设下一代用户交互框架，优化电商和云计算产品的用户体验。主要工作包括：
        - 参与"灵动引擎"前端架构的设计与开发，提升终端渲染性能与用户体验
        - 负责淘天主要业务线产品的前端架构优化和技术选型
        - 开发高性能、可复用的UI组件和数据可视化模块
        - 与产品、设计和后端团队协作，打造行业领先的用户体验
        - 推动前端技术创新，参与内部技术分享和开源项目建设

        【任职要求】
        - 本科及以上学历，计算机相关专业，3年以上前端开发经验
        - 精通HTML5、CSS3、JavaScript，熟悉ES6+规范及特性
        - 熟练掌握React/Vue等主流前端框架，有大型项目实践经验
        - 具备良好的TypeScript开发能力，能够构建类型安全的应用
        - 熟悉前端工程化工具(Webpack/Vite/Rollup等)和自动化测试
        - 了解Node.js服务端开发，有SSR实践经验者优先
        - 对性能优化、跨端开发、微前端架构有深入理解
        - 具备良好的学习能力、沟通能力和团队协作精神

        【加分项】
        - 主导过大型前端项目的架构设计和技术选型
        - 有开源项目贡献或技术社区影响力
        - 熟悉低代码平台、WebGL或3D渲染技术
        - 有跨端开发经验(ReactNative/Flutter等)
        - 了解云原生、微服务等后端技术栈
        
        作为主动邀约的HR：
        1. 你的目标是根据上述JD吸引候选人对公司和职位产生兴趣，并初步评估其技术背景是否匹配职位要求
        2. 保持友好、专业的交流氛围，表现出对候选人的重视
        3. 提问应该围绕JD中提到的技术栈和要求展开，特别关注React/Vue、TypeScript、前端性能优化等方面的经验
        4. 适当给予积极反馈，表达对候选人回答的认可
        5. 避免连续提问多个技术问题，保持对话的自然流动性
        
        关于面试邀约：
        1. 你需要在对话中判断候选人的兴趣度
        2. 如果候选人表现出明显的兴趣（通过积极提问、主动分享经验、表达对职位的兴趣等），应在2-3轮对话后主动发出面试邀约
        3. 面试邀约应该明确具体，提供多个可选的面试时间段，并说明面试流程（如：线上技术面试 + HR面试）
        4. 面试邀约示例："看到您对我们的职位很感兴趣，我想邀请您参加我们的面试流程。我们可以安排下周二上午10点或周四下午2点进行一次视频技术面试，面试时长约为1小时。请问这两个时间您哪个更方便？"
        5. 如果候选人同意面试，应表示感谢并确认具体时间，同时提供一些面试准备建议
        
        注意：
        - 每次回复控制在150字以内，保持简洁
        - 不要一次性提出多个问题，每次只问一个问题
        - 以主动招聘方的身份发言，而不是被动接收申请
        - 回答要符合HR的身份和专业度，不需要展示深度技术知识
        - 如果候选人提到了JD中的关键技术或经验，应给予积极回应并进一步询问相关细节
        """
    
    def add_message(self, role, content):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        # 添加系统提示词
        self.add_message("system", self.hr_system_prompt)
    
    def get_ai_response(self, user_message):
        """获取AI回复"""
        # 添加用户消息到历史
        self.add_message("user", user_message)
        
        if self.api_type == 'openai':
            response = self._call_openai_api()
        elif self.api_type == 'zhipu':
            response = self._call_zhipu_api()
        else:
            # 如果需要，可以添加其他API的调用方法
            response = "当前API类型不支持，请检查配置。"
        
        # 添加AI回复到历史
        self.add_message("assistant", response)
        
        return response
        
    def evaluate_interest(self) -> dict:
        """评估候选人的兴趣度
        返回包含兴趣度评估结果的字典
        """
        # 提取用户的所有消息
        user_messages = [msg['content'] for msg in self.conversation_history if msg['role'] == 'user']
        
        if not user_messages:
            return {
                'interest_level': '未知',
                'confidence': 0,
                'reasons': ['对话尚未开始或没有用户消息']
            }
        
        # 积极关键词
        positive_keywords = [
            '感兴趣', '想了解', '可以聊聊', '愿意', '希望', '期待', 
            '什么时候', '如何面试', '面试时间', '面试流程',
            '详细介绍', '薪资', '待遇', '职责', '要求',
            '公司情况', '团队', '项目', '技术栈', '发展'
        ]
        
        # 消极关键词
        negative_keywords = [
            '不感兴趣', '没空', '再看看', '考虑一下', '暂时不', 
            '不合适', '不符合', '其他机会', '没有打算', '忙',
            '时间不合适', '拒绝', '抱歉', '不好意思'
        ]
        
        # 计算关键词匹配
        positive_matches = 0
        negative_matches = 0
        
        for message in user_messages:
            for keyword in positive_keywords:
                if keyword in message:
                    positive_matches += 1
            
            for keyword in negative_keywords:
                if keyword in message:
                    negative_matches += 1
        
        # 评估对话长度因素
        conversation_length_factor = min(len(user_messages) / 5, 1.0)  # 最多5条消息达到满分
        
        # 计算积极度得分 (0-100)
        positivity_score = min(100, max(0, 
            50 + (positive_matches * 10) - (negative_matches * 15) + (conversation_length_factor * 20)
        ))
        
        # 确定兴趣级别
        interest_level = '未知'
        reasons = []
        
        if positivity_score >= 70:
            interest_level = '高度感兴趣'
            reasons.append(f'积极相关词汇出现{positive_matches}次')
            if conversation_length_factor > 0.6:
                reasons.append('持续保持对话')
            if positive_matches > negative_matches:
                reasons.append('表达了进一步了解的意愿')
        elif positivity_score >= 40:
            interest_level = '可能感兴趣'
            reasons.append('态度中性偏积极')
            if negative_matches > 0:
                reasons.append('有一些犹豫或保留')
            if conversation_length_factor > 0.3:
                reasons.append('愿意继续对话')
        else:
            interest_level = '不太感兴趣'
            if negative_matches > 0:
                reasons.append(f'消极相关词汇出现{negative_matches}次')
            if conversation_length_factor < 0.3:
                reasons.append('对话简短')
            if positive_matches == 0:
                reasons.append('未表达积极兴趣')
        
        # 计算评估的置信度 (0-1)
        confidence = min(1.0, 0.3 + (len(user_messages) * 0.1) + (positive_matches + negative_matches) * 0.05)
        
        return {
            'interest_level': interest_level,
            'score': round(positivity_score, 1),
            'confidence': round(confidence, 2),
            'reasons': reasons,
            'message_count': len(user_messages)
        }
    
    def _call_openai_api(self):
        """调用OpenAI API获取回复"""
        if not self.openai_api_key:
            return "请在.env文件中配置OPENAI_API_KEY"
        
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",  # 可以替换为gpt-4等其他模型
            "messages": self.conversation_history,
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response_data = response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content'].strip()
            else:
                return f"API调用出错: {json.dumps(response_data)}"
        except Exception as e:
            return f"API调用异常: {str(e)}"
    
    def _call_zhipu_api(self):
        """调用智谱AI API获取回复"""
        if not self.zhipu_api_key:
            return "请在.env文件中配置ZHIPU_API_KEY"
        
        try:
            # 使用智谱AI的SDK调用API
            response = self.zhipu_client.chat.completions.create(
                model="glm-4-plus",  # 使用GLM-4系列模型
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=150
            )
            
            # 提取回复内容
            if hasattr(response.choices[0], 'message') and response.choices[0].message is not None:
                return response.choices[0].message.content.strip()
            else:
                return "智谱AI回复内容为空，请检查API调用。"
                
        except Exception as e:
            return f"智谱AI API调用异常: {str(e)}"
    
    def start_interview(self):
        """启动面试会话，返回初始问候语"""
        # 清空历史对话
        self.clear_history()
        
        # 构建初始问候语
        initial_greeting = """
        您好！我是淘天集团的招聘专员Jesse范。我们正在寻找优秀的前端开发工程师，通过人才库看到您的技术背景非常匹配我们的需求。
        
        淘天是一家快速成长的科技公司，专注于电商和云计算领域，我们的前端团队正在开发新一代的用户界面框架。
        
        我们的团队正在寻找一位资深前端开发工程师，负责淘天主要业务线产品的前端架构优化和技术选型。您是否对这个职位感兴趣？或者您想了解更多关于这个职位的信息？
        """
        
        # 添加系统消息
        self.add_message("system", self.hr_system_prompt)
        
        # 添加首条HR消息（不使用AI生成，确保第一条消息的可控性）
        self.add_message("assistant", initial_greeting.strip())
        
        return initial_greeting.strip()

# 创建全局AI服务实例
ai_service = AIService()
