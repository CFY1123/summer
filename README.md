# 电商后台商品管理模块

本项目采用前后端分离模式实现电商后台商品管理功能。

- 前端：Vue 3 + TypeScript + Vite + Element Plus + axios + Pinia
- 后端：Spring Boot 3 + MyBatis + MySQL + Apache POI
- 文档：需求规约、数据库设计、界面 UI 设计
- 编辑器：已提供 VS Code 推荐插件、任务和调试配置

## 目录结构

```text
.
├── docs                         # 需求与设计文档
├── backend                      # Spring Boot 后端
├── frontend                     # Vue3 前端
└── .vscode                      # VS Code 配置
```

## 后端启动

1. 在 MySQL 中创建数据库：

```sql
CREATE DATABASE ecommerce_goods DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 默认数据库连接为 `localhost:3306`，账号 `root`，密码 `123456`。如本机不同，请修改 `backend/src/main/resources/application.yml`。

3. 执行初始化脚本：

```bash
mysql -u root -p ecommerce_goods < backend/src/main/resources/schema.sql
```

4. 启动后端：

```bash
cd backend
powershell -ExecutionPolicy Bypass -File run-dev.ps1
```

后端接口地址默认为 `http://localhost:8080/api`。

如果使用打包方式启动，也可以执行：

```bash
cd backend
mvn clean package
java -jar target/goods-management-backend-1.0.0.jar
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端地址默认为 `http://localhost:5173`。

## VS Code 使用

打开当前文件夹后：

- 推荐安装弹出的 Java、Vue、ESLint 等插件；
- 使用 `终端 -> 运行任务` 可启动前端或后端；
- 使用 `运行和调试 -> Spring Boot: GoodsManagementApplication` 可调试后端。

## 测试与部署文档

- 需求规约：[docs/requirements.md](docs/requirements.md)
- 数据库设计：[docs/database-design.md](docs/database-design.md)
- 界面 UI 设计：[docs/ui-design.md](docs/ui-design.md)
- 测试用例：[docs/test-cases.md](docs/test-cases.md)
- 测试报告：[docs/test-report.md](docs/test-report.md)
- 单元测试报告：[docs/unit-test-report.md](docs/unit-test-report.md)
- 系统测试报告：[docs/system-test-report.md](docs/system-test-report.md)
- Linux 部署说明：[deploy/linux-deploy.md](deploy/linux-deploy.md)
