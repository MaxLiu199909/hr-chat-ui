# HR聊天应用

这是一个基于Flask和智谱AI的HR聊天应用，用于评估候选人对职位的兴趣并进行初步交流。

## 功能特点

- 候选人兴趣评估：基于关键词分析评估候选人对职位的兴趣水平
- 聊天记录存储：保存完整的对话历史
- 自动面试邀请：根据候选人的兴趣水平，自动发出面试邀请
- 响应式界面：适应不同设备的屏幕尺寸

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Flask (Python)
- AI模型：智谱AI SDK
- 数据存储：JSON文件系统

## 环境变量配置

项目需要以下环境变量：
- `ZHIPU_API_KEY`：智谱AI API密钥

## 部署说明

1. 安装依赖：`pip install -r requirements.txt`
2. 设置环境变量
3. 运行应用：`python app.py` 或 `gunicorn wsgi:app`
