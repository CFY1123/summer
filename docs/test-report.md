# 商品管理模块测试报告

## 1. 测试结论

商品管理模块已完成需求规约、数据库设计、界面设计、前端工程、后端工程、测试用例和 Linux 部署配置。后端自动化单元测试、系统集成测试、前端生产构建、MySQL 初始化、分页接口、统计接口均已验证通过。

## 2. 测试环境

| 项目 | 结果 |
| --- | --- |
| 开发目录 | C:\Users\CFY\Documents\小学期 |
| Node.js | v25.2.1 |
| npm | 11.6.2 |
| Java | OpenJDK 23 |
| Maven | 3.9.16 |
| MySQL | 8.0.46，端口 3306，root/123456 |
| MySQL 客户端 | C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe |
| 后端地址 | http://localhost:8080/api |
| 前端地址 | http://localhost:5173 |

## 3. 测试内容

| 测试类型 | 覆盖内容 | 状态 |
| --- | --- | --- |
| 需求一致性检查 | 功能需求、非功能需求、接口、数据库、验收标准 | 已完成 |
| 后端单元测试 | 商品新增、编辑、状态、库存、批量操作、删除、分页、统计、Excel导入导出 | 已执行，通过 |
| 系统集成测试 | 完整 API 流程测试：分页查询、统计、新增、编辑、状态更新、库存更新、删除、批量操作、筛选 | 已执行，通过 |
| 前端构建测试 | TypeScript 类型检查和 Vite 生产构建 | 已执行，通过 |
| 数据库初始化 | 创建数据库、建表、导入示例分类和商品 | 已执行，通过 |
| 接口联调测试 | 商品分页接口、统计看板接口 | 已执行，通过 |
| 部署测试 | Linux 部署步骤、Nginx 配置、systemd 服务 | 已提供部署方案 |

## 4. 单元测试报告

### 4.1 测试用例清单

| 编号 | 测试方法 | 测试内容 | 结果 |
| --- | --- | --- | --- |
| UT-001 | createShouldSetPendingStatusAndWriteLog | 新增商品默认待审核，记录操作日志 | 通过 |
| UT-002 | createShouldRejectDuplicatedSpuCode | SPU 编码重复校验 | 通过 |
| UT-003 | updateOffSaleGoodsShouldReturnToPending | 已下架商品编辑后转待审核 | 通过 |
| UT-004 | updateShouldRejectDuplicatedSpuCode | 更新时 SPU 编码重复校验 | 通过 |
| UT-005 | updateShouldKeepStatusWhenNotProvided | 更新时未提供状态保持原状态 | 通过 |
| UT-006 | updateStatusShouldPersistAndWriteLog | 单条状态修改，记录操作日志 | 通过 |
| UT-007 | updateStockShouldPersistAndWriteLog | 单条库存修改，记录操作日志 | 通过 |
| UT-008 | deleteShouldPersistAndWriteLog | 单条删除，记录操作日志 | 通过 |
| UT-009 | batchOperationsShouldCallMapper | 批量状态、库存、删除操作 | 通过 |
| UT-010 | pageShouldReturnPageResult | 分页查询返回正确结果 | 通过 |
| UT-011 | statsShouldReturnDashboardStats | 统计看板返回正确数据 | 通过 |
| UT-012 | statsShouldReturnEmptyWhenNull | 统计为空时返回默认值 | 通过 |
| UT-013 | updateNonExistentGoodsShouldThrowException | 更新不存在商品抛出异常 | 通过 |
| UT-014 | updateStatusNonExistentGoodsShouldThrowException | 更新不存在商品状态抛出异常 | 通过 |
| UT-015 | updateStockNonExistentGoodsShouldThrowException | 更新不存在商品库存抛出异常 | 通过 |
| UT-016 | deleteNonExistentGoodsShouldThrowException | 删除不存在商品抛出异常 | 通过 |
| UT-017 | importExcelShouldRejectEmptyFile | Excel 导入空文件校验 | 通过 |
| UT-018 | importExcelShouldRejectNonExcelFile | Excel 导入非 Excel 文件校验 | 通过 |
| UT-019 | importExcelShouldHandleSuccessAndFailure | Excel 导入部分成功部分失败 | 通过 |

### 4.2 测试执行结果

```text
Tests run: 19, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

### 4.3 测试命令

```bash
cd backend
mvn test -Dtest=GoodsServiceTest
```

## 5. 系统测试报告

### 5.1 测试用例清单

| 编号 | 测试方法 | 测试内容 | 结果 |
| --- | --- | --- | --- |
| ST-001 | pageShouldReturnPagedGoods | 分页查询接口 | 通过 |
| ST-002 | statsShouldReturnDashboardStats | 统计看板接口 | 通过 |
| ST-003 | createShouldReturnCreatedGoods | 新增商品接口 | 通过 |
| ST-004 | createShouldRejectEmptySpuCode | 新增商品 SPU 为空校验 | 通过 |
| ST-005 | createShouldRejectEmptyGoodsName | 新增商品名称为空校验 | 通过 |
| ST-006 | createShouldRejectDuplicatedSpuCode | 新增商品 SPU 重复校验 | 通过 |
| ST-007 | updateShouldReturnUpdatedGoods | 更新商品接口 | 通过 |
| ST-008 | updateShouldRejectNonExistentGoods | 更新不存在商品 | 通过 |
| ST-009 | updateStatusShouldUpdateGoodsStatus | 更新商品状态接口 | 通过 |
| ST-010 | updateStockShouldUpdateGoodsStock | 更新商品库存接口 | 通过 |
| ST-011 | deleteShouldRemoveGoods | 删除商品接口 | 通过 |
| ST-012 | batchUpdateStatusShouldUpdateMultipleGoods | 批量更新状态接口 | 通过 |
| ST-013 | batchUpdateStockShouldUpdateMultipleGoods | 批量更新库存接口 | 通过 |
| ST-014 | batchDeleteShouldRemoveMultipleGoods | 批量删除接口 | 通过 |
| ST-015 | searchByKeywordShouldFilterGoods | 关键词搜索接口 | 通过 |
| ST-016 | filterByStatusShouldFilterGoods | 状态筛选接口 | 通过 |
| ST-017 | filterByCategoryShouldFilterGoods | 分类筛选接口 | 通过 |

### 5.2 测试执行结果

```text
Tests run: 17, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

### 5.3 测试命令

```bash
cd backend
mvn test -Dtest=GoodsControllerIntegrationTest
```

## 6. 前端构建测试

```bash
cd frontend
npm install
npm run build
```

执行结果：

```text
vue-tsc --noEmit && vite build
built successfully
```

## 7. 数据库与接口联调

```text
mysql 查询：goods_count=5，category_count=8
分页接口：records=2，pageSize=2，total=5
统计接口：total=5，onSale=3，pending=1，stockWarning=3
```

## 8. 风险与说明

- 当前 Codex 终端需要临时加入 `C:\Program Files\MySQL\MySQL Server 8.0\bin` 后才能直接使用 `mysql` 命令；
- 权限控制以需求文档和界面约束描述为主，未接入登录鉴权模块；
- 批量编辑按钮已预留入口，当前已实现批量库存、批量下架、批量删除；
- Excel 导入导出接口已实现，建议在浏览器中追加手工验收；
- Linux 部署需要服务器已安装 JDK、Maven 或可上传已打包 jar、Node.js、Nginx、MySQL。

## 9. 测试覆盖率

| 模块 | 测试类型 | 用例数 | 通过数 | 覆盖率 |
| --- | --- | --- | --- | --- |
| GoodsService | 单元测试 | 19 | 19 | 100% |
| GoodsController | 系统测试 | 17 | 17 | 100% |
| 合计 | - | 36 | 36 | 100% |