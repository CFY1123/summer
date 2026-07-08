# 商品管理模块系统测试报告

## 1. 报告说明

| 项目 | 内容 |
| --- | --- |
| 报告名称 | 商品管理模块系统测试报告 |
| 测试对象 | 商品管理后端接口与系统业务流程 |
| 测试文件 | `backend/src/test/java/com/example/goods/controller/GoodsControllerIntegrationTest.java` |
| 测试框架 | Spring Boot Test、MockMvc、JUnit 5 |
| 测试日期 | 2026-07-06 |
| 测试结论 | 通过 |

## 2. 测试目的

系统测试用于验证商品管理模块在 Spring Boot 应用上下文、Controller、Service、Mapper、MySQL 数据库协同工作时的正确性，重点检查接口返回格式、业务流程、参数校验、筛选查询、批量操作和数据持久化是否符合需求规约。

## 3. 测试环境

| 环境项 | 配置 |
| --- | --- |
| 操作系统 | Windows 11 |
| Java | OpenJDK 23 |
| Maven | 3.9.16 |
| 后端框架 | Spring Boot 3.3.5、MyBatis |
| 数据库 | MySQL 8.0.46 |
| 数据库端口 | 3306 |
| 数据库账号 | root |
| 数据库密码 | 123456 |
| 测试工具 | Spring MockMvc |
| 执行目录 | `C:\Users\CFY\Documents\小学期\backend` |

## 4. 测试范围

本次系统测试覆盖以下接口和业务流程：

- 商品分页查询接口；
- 商品统计看板接口；
- 新增商品接口；
- 新增商品参数校验；
- SPU 重复校验；
- 编辑商品接口；
- 编辑不存在商品异常处理；
- 单条状态修改；
- 单条库存修改；
- 单条删除；
- 批量状态修改；
- 批量库存修改；
- 批量删除；
- 关键词筛选；
- 状态筛选；
- 分类筛选。

## 5. 测试用例

| 编号 | 测试方法 | 测试内容 | 预期结果 | 执行结果 |
| --- | --- | --- | --- | --- |
| ST-001 | pageShouldReturnPagedGoods | 分页查询商品列表 | 返回 200、records 数组、total、page、pageSize | 通过 |
| ST-002 | statsShouldReturnDashboardStats | 获取统计看板 | 返回 total、onSale、pending、stockWarning | 通过 |
| ST-003 | createShouldReturnCreatedGoods | 新增商品 | 返回新增商品 ID，状态默认为待审核 | 通过 |
| ST-004 | createShouldRejectEmptySpuCode | 新增商品 SPU 为空 | 返回 400 参数校验失败 | 通过 |
| ST-005 | createShouldRejectEmptyGoodsName | 新增商品名称为空 | 返回 400 参数校验失败 | 通过 |
| ST-006 | createShouldRejectDuplicatedSpuCode | 新增重复 SPU 商品 | 返回 400 业务校验失败 | 通过 |
| ST-007 | updateShouldReturnUpdatedGoods | 编辑商品 | 返回更新后的名称、分类、价格 | 通过 |
| ST-008 | updateShouldRejectNonExistentGoods | 编辑不存在商品 | 返回 400 商品不存在 | 通过 |
| ST-009 | updateStatusShouldUpdateGoodsStatus | 修改商品状态 | 返回 200，状态修改成功 | 通过 |
| ST-010 | updateStockShouldUpdateGoodsStock | 修改商品库存 | 返回 200，库存修改成功 | 通过 |
| ST-011 | deleteShouldRemoveGoods | 删除商品 | 返回 200，商品被逻辑删除 | 通过 |
| ST-012 | batchUpdateStatusShouldUpdateMultipleGoods | 批量修改状态 | 返回 200，多个商品状态更新成功 | 通过 |
| ST-013 | batchUpdateStockShouldUpdateMultipleGoods | 批量修改库存 | 返回 200，多个商品库存更新成功 | 通过 |
| ST-014 | batchDeleteShouldRemoveMultipleGoods | 批量删除商品 | 返回 200，多个商品被逻辑删除 | 通过 |
| ST-015 | searchByKeywordShouldFilterGoods | 关键词搜索 | 返回 200，records 为数组 | 通过 |
| ST-016 | filterByStatusShouldFilterGoods | 按状态筛选 | 返回 200，records 为数组 | 通过 |
| ST-017 | filterByCategoryShouldFilterGoods | 按分类筛选 | 返回 200，records 为数组 | 通过 |

## 6. 执行命令

```powershell
cd C:\Users\CFY\Documents\小学期\backend
mvn test -Dtest=GoodsControllerIntegrationTest
```

## 7. 执行结果

```text
Tests run: 17, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

执行时间：

```text
2026-07-06 16:18:16
```

## 8. 系统联调状态

| 项目 | 验证结果 |
| --- | --- |
| Spring Boot 应用上下文加载 | 通过 |
| MockMvc 接口调用 | 通过 |
| MySQL 数据库连接 | 通过 |
| 商品新增、编辑、删除链路 | 通过 |
| 商品状态、库存修改链路 | 通过 |
| 商品筛选查询链路 | 通过 |
| 统一响应结构 | 通过 |
| 参数校验和异常返回 | 通过 |

## 9. 缺陷记录

| 编号 | 缺陷描述 | 状态 |
| --- | --- | --- |
| 无 | 本次系统测试未发现失败用例 | 已关闭 |

## 10. 测试结论

商品管理模块系统测试共执行 17 条，通过 17 条，失败 0 条，错误 0 条，跳过 0 条。测试结果表明商品管理模块接口层、业务层、持久层和数据库协同正常，核心业务流程满足商品管理功能验收要求。

