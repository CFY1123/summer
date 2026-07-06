# 商品管理模块单元测试报告

## 1. 报告说明

| 项目 | 内容 |
| --- | --- |
| 报告名称 | 商品管理模块单元测试报告 |
| 测试对象 | 后端 `GoodsService` 业务服务层 |
| 测试文件 | `backend/src/test/java/com/example/goods/service/GoodsServiceTest.java` |
| 测试框架 | JUnit 5、Mockito、Spring Test |
| 测试日期 | 2026-07-06 |
| 测试结论 | 通过 |

## 2. 测试目的

单元测试用于验证商品管理模块核心业务逻辑在隔离数据库和 Web 容器的情况下是否正确，重点检查商品新增、编辑、状态流转、库存调整、删除、分页统计、Excel 导入校验、异常处理和操作日志调用是否符合需求规约。

## 3. 测试环境

| 环境项 | 配置 |
| --- | --- |
| 操作系统 | Windows 11 |
| Java | OpenJDK 23 |
| Maven | 3.9.16 |
| 后端框架 | Spring Boot 3.3.5 |
| 测试框架 | JUnit 5、Mockito |
| 执行目录 | `C:\Users\CFY\Documents\小学期\backend` |

## 4. 测试范围

本次单元测试覆盖以下服务层能力：

- 新增商品默认状态处理；
- SPU 编码唯一性校验；
- 已下架商品编辑后重新进入待审核；
- 商品状态修改；
- 商品库存修改；
- 商品逻辑删除；
- 批量状态、库存、删除操作；
- 分页查询结果封装；
- 统计看板数据返回；
- 不存在商品的异常处理；
- Excel 导入文件类型、空文件、成功与失败明细处理；
- 操作日志记录调用。

## 5. 测试用例

| 编号 | 测试方法 | 测试内容 | 预期结果 | 执行结果 |
| --- | --- | --- | --- | --- |
| UT-001 | createShouldSetPendingStatusAndWriteLog | 新增商品 | 默认状态为待审核，写入新增日志 | 通过 |
| UT-002 | createShouldRejectDuplicatedSpuCode | 新增重复 SPU 商品 | 抛出 SPU 已存在异常，不执行插入 | 通过 |
| UT-003 | updateOffSaleGoodsShouldReturnToPending | 编辑已下架商品 | 商品状态重新变为待审核 | 通过 |
| UT-004 | updateShouldRejectDuplicatedSpuCode | 编辑时使用其他商品 SPU | 抛出 SPU 已存在异常，不执行更新 | 通过 |
| UT-005 | updateShouldKeepStatusWhenNotProvided | 编辑时未传状态 | 保持原商品状态 | 通过 |
| UT-006 | updateStatusShouldPersistAndWriteLog | 单条修改商品状态 | 调用状态更新并记录日志 | 通过 |
| UT-007 | updateStockShouldPersistAndWriteLog | 单条修改库存 | 调用库存更新并记录日志 | 通过 |
| UT-008 | deleteShouldPersistAndWriteLog | 单条删除商品 | 执行逻辑删除并记录日志 | 通过 |
| UT-009 | batchOperationsShouldCallMapper | 批量状态、库存、删除 | 调用对应批量 Mapper 方法 | 通过 |
| UT-010 | pageShouldReturnPageResult | 分页查询 | 返回分页记录、总数、页码、每页条数 | 通过 |
| UT-011 | statsShouldReturnDashboardStats | 获取统计看板 | 返回总数、上架数、待审核数、库存预警数 | 通过 |
| UT-012 | statsShouldReturnEmptyWhenNull | 统计结果为空 | 返回默认空统计对象 | 通过 |
| UT-013 | updateNonExistentGoodsShouldThrowException | 编辑不存在商品 | 抛出商品不存在异常 | 通过 |
| UT-014 | updateStatusNonExistentGoodsShouldThrowException | 修改不存在商品状态 | 抛出商品不存在异常 | 通过 |
| UT-015 | updateStockNonExistentGoodsShouldThrowException | 修改不存在商品库存 | 抛出商品不存在异常 | 通过 |
| UT-016 | deleteNonExistentGoodsShouldThrowException | 删除不存在商品 | 抛出商品不存在异常 | 通过 |
| UT-017 | importExcelShouldRejectEmptyFile | 导入空 Excel 文件 | 抛出请选择 Excel 文件异常 | 通过 |
| UT-018 | importExcelShouldRejectNonExcelFile | 导入非 Excel 文件 | 抛出仅支持 xlsx/xls 异常 | 通过 |
| UT-019 | importExcelShouldHandleSuccessAndFailure | Excel 导入部分成功部分失败 | 返回成功数、失败数和错误行明细 | 通过 |

## 6. 执行命令

```powershell
cd C:\Users\CFY\Documents\小学期\backend
mvn test -Dtest=GoodsServiceTest
```

## 7. 执行结果

```text
Tests run: 19, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

执行时间：

```text
2026-07-06 16:18:10
```

## 8. 缺陷记录

| 编号 | 缺陷描述 | 状态 |
| --- | --- | --- |
| 无 | 本次单元测试未发现失败用例 | 已关闭 |

## 9. 测试结论

商品管理模块服务层单元测试共执行 19 条，通过 19 条，失败 0 条，错误 0 条，跳过 0 条。测试结果表明商品管理核心业务逻辑、异常处理和日志调用符合需求规约，可进入系统测试和联调验证阶段。

