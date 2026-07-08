# AI 学习助手 Python 后端

这是学习平台任务的 Python 后端，使用 FastAPI + SQLAlchemy + MySQL。

## 本机版本

- Python: 3.14.0
- Node: v25.2.1
- npm: 11.6.2
- MySQL: 8.0.46

## 数据库

默认连接本地 MySQL：

- 地址：`localhost:3306`
- 数据库：`learning_platform`
- 用户：`root`
- 密码：`123456`

配置在 `.env` 里，提交代码时可参考 `.env.example`。

初始化表结构：

```powershell
$env:MYSQL_PWD='123456'
Get-Content -Raw learning-platform/backend-python/db/schema.sql | mysql -u root --default-character-set=utf8mb4 learning_platform
```

## 启动

从总目录启动：

```powershell
cd learning-platform/backend-python
powershell -ExecutionPolicy Bypass -File run-dev.ps1
```

启动后接口地址：

- 健康检查：`http://localhost:8080/api/health`
- 接口文档：`http://localhost:8080/docs`

## 当前功能范围

先做这些：

- 本地知识库：PDF、DOCX、TXT 文档上传、解析、分块、向量索引。
- 课程大纲：基于知识库生成章/节两级大纲。
- 学习进度：记录未开始、学习中、已完成，提供进度看板。
- 在线测验：按章节自动出题、答题批改、考试历史、错题本。
- 学习工作台：前端提供知识库、章节、测验、错题的一体化操作入口。
- 人脸识别：摄像头采集两帧，保存本地特征模板，提供简单活体检测和备用密码登录。
- 语音交互：浏览器语音识别指令、语音播报反馈、语音开关。

## AI 依赖

基础后端依赖在 `requirements.txt`。当前知识库默认使用本地轻量向量索引原型，便于离线验收；LangChain 和 Chroma 放在 `requirements-ai.txt`，后续可以平滑替换为真实向量数据库：

```powershell
cd learning-platform/backend-python
.\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt
```
