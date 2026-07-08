# 小学期任务

这个目录按两个任务内容拆分：

```text
.
├── goods-management      # 商品管理模块
└── learning-platform     # AI 学习助手
```

## goods-management

商品管理模块保留原来的完整工程：

- `goods-management/backend`：Spring Boot + MyBatis 后端
- `goods-management/frontend`：Vue 3 + Vite 前端
- `goods-management/docs`：商品管理需求、数据库设计、测试文档
- `goods-management/deploy`：部署配置

启动商品前端：

```powershell
cd goods-management/frontend
npm run dev
```

启动商品 Java 后端：

```powershell
cd goods-management/backend
powershell -ExecutionPolicy Bypass -File run-dev.ps1
```

## learning-platform

AI 学习助手引用了地球OL初级玩家的 `Earth-OL-Player/ai_learn_project.git` 项目中的 `ai-learn-web` 前端，并接入本项目的 Python 后端兼容接口。

- `learning-platform/frontend`：ai-learn-web 前端
- `learning-platform/backend-python`：Python + FastAPI 后端
- `learning-platform/docs`：学习平台需求文档

数据库使用本地 MySQL 新库：

```text
learning_platform
```

启动学习平台 Python 后端：

```powershell
cd learning-platform/backend-python
powershell -ExecutionPolicy Bypass -File run-dev.ps1
```

启动学习平台前端：

```powershell
cd learning-platform/frontend
pnpm run dev
```

当前学习平台已保留/实现：

- 目标仓库前端：首页、路线、刷题、面试题、互动、个人中心
- 学习工作台：知识库上传、章节学习、进度、测验、错题复盘的一体化验收入口
- Python 后端 `/api/v1` 兼容接口
- PDF、DOCX、TXT 三种课程资料解析
- 本地知识库、章节、进度、测验、错题相关后端接口
- 文档分块、轻量向量索引、相似度检索原型
- 人脸识别登录/注册、简单活体检测、密码备用登录
- 语音指令、语音播报、语音开关
