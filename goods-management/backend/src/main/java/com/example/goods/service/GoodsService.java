package com.example.goods.service;

import com.example.goods.common.PageResult;
import com.example.goods.dto.BatchDeleteRequest;
import com.example.goods.dto.BatchStatusRequest;
import com.example.goods.dto.BatchStockRequest;
import com.example.goods.dto.DashboardStats;
import com.example.goods.dto.GoodsQuery;
import com.example.goods.dto.GoodsSaveRequest;
import com.example.goods.dto.ImportResult;
import com.example.goods.mapper.GoodsMapper;
import com.example.goods.model.Goods;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.math.BigDecimal;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.ss.usermodel.WorkbookFactory;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class GoodsService {
    private final GoodsMapper goodsMapper;
    private final LogService logService;

    @Value("${goods.default-warn-stock:10}")
    private Integer defaultWarnStock;

    public GoodsService(GoodsMapper goodsMapper, LogService logService) {
        this.goodsMapper = goodsMapper;
        this.logService = logService;
    }

    public PageResult<Goods> page(GoodsQuery query) {
        query.warnStock = defaultWarnStock;
        List<Goods> records = goodsMapper.selectPage(query);
        long total = goodsMapper.countPage(query);
        return new PageResult<>(records, total, query.page == null ? 1 : query.page, query.limit());
    }

    public DashboardStats stats() {
        DashboardStats stats = goodsMapper.selectStats(defaultWarnStock);
        if (stats == null) {
            return new DashboardStats();
        }
        return stats;
    }

    @Transactional
    public Goods create(GoodsSaveRequest request) {
        if (goodsMapper.selectBySpuCode(request.spuCode) != null) {
            throw new IllegalArgumentException("SPU 编码已存在");
        }
        Goods goods = toGoods(request);
        goods.status = 0;
        goodsMapper.insert(goods);
        logService.record(goods, "CREATE", "新增商品：" + goods.goodsName);
        return goodsMapper.selectById(goods.id);
    }

    @Transactional
    public Goods update(Long id, GoodsSaveRequest request) {
        Goods exists = mustFind(id);
        Goods sameSpu = goodsMapper.selectBySpuCode(request.spuCode);
        if (sameSpu != null && !sameSpu.id.equals(id)) {
            throw new IllegalArgumentException("SPU 编码已存在");
        }
        Goods goods = toGoods(request);
        goods.id = id;
        goods.status = request.status == null ? exists.status : request.status;
        if (exists.status != null && exists.status == 2) {
            goods.status = 0;
        }
        goodsMapper.update(goods);
        logService.record(goods, "UPDATE", "编辑商品：" + goods.goodsName);
        return goodsMapper.selectById(id);
    }

    @Transactional
    public void updateStatus(Long id, Integer status) {
        Goods goods = mustFind(id);
        goodsMapper.updateStatus(id, status);
        goods.status = status;
        logService.record(goods, "STATUS", "修改商品状态为：" + statusName(status));
    }

    @Transactional
    public void updateStatusBatch(BatchStatusRequest request) {
        goodsMapper.updateStatusBatch(request.ids, request.status);
        logService.record(null, "STATUS", "批量修改商品状态为：" + statusName(request.status) + "，数量：" + request.ids.size());
    }

    @Transactional
    public void updateStock(Long id, Integer stockNum) {
        Goods goods = mustFind(id);
        goodsMapper.updateStock(id, stockNum);
        goods.stockNum = stockNum;
        logService.record(goods, "STOCK", "调整库存为：" + stockNum);
    }

    @Transactional
    public void updateStockBatch(BatchStockRequest request) {
        goodsMapper.updateStockBatch(request.ids, request.stockNum);
        logService.record(null, "STOCK", "批量调整库存为：" + request.stockNum + "，数量：" + request.ids.size());
    }

    @Transactional
    public void delete(Long id) {
        Goods goods = mustFind(id);
        goodsMapper.logicalDelete(id);
        logService.record(goods, "DELETE", "删除商品：" + goods.goodsName);
    }

    @Transactional
    public void deleteBatch(BatchDeleteRequest request) {
        goodsMapper.logicalDeleteBatch(request.ids);
        logService.record(null, "DELETE", "批量删除商品，数量：" + request.ids.size());
    }

    public void exportExcel(GoodsQuery query, HttpServletResponse response) throws IOException {
        query.page = 1;
        query.pageSize = 10000;
        query.warnStock = defaultWarnStock;
        List<Goods> records = goodsMapper.selectPage(query);

        try (Workbook workbook = new XSSFWorkbook()) {
            Sheet sheet = workbook.createSheet("商品数据");
            writeHeader(sheet.createRow(0));
            for (int i = 0; i < records.size(); i++) {
                writeGoodsRow(sheet.createRow(i + 1), records.get(i));
            }
            for (int i = 0; i < 9; i++) {
                sheet.autoSizeColumn(i);
            }
            String fileName = URLEncoder.encode("商品数据.xlsx", StandardCharsets.UTF_8);
            response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + fileName);
            workbook.write(response.getOutputStream());
        }
        logService.record(null, "EXPORT", "导出商品数据，数量：" + records.size());
    }

    public void downloadTemplate(HttpServletResponse response) throws IOException {
        try (Workbook workbook = new XSSFWorkbook()) {
            Sheet sheet = workbook.createSheet("商品导入模板");
            writeHeader(sheet.createRow(0));
            Row example = sheet.createRow(1);
            example.createCell(0).setCellValue("SPU202607020999");
            example.createCell(1).setCellValue("示例商品");
            example.createCell(2).setCellValue(2);
            example.createCell(3).setCellValue(99.99);
            example.createCell(4).setCellValue(100);
            example.createCell(5).setCellValue(10);
            example.createCell(6).setCellValue("https://example.com/goods.jpg");
            example.createCell(7).setCellValue("商品详情");
            example.createCell(8).setCellValue("状态导入时默认待审核");
            for (int i = 0; i < 9; i++) {
                sheet.autoSizeColumn(i);
            }
            String fileName = URLEncoder.encode("商品导入模板.xlsx", StandardCharsets.UTF_8);
            response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + fileName);
            workbook.write(response.getOutputStream());
        }
    }

    @Transactional
    public ImportResult importExcel(MultipartFile file) throws IOException {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("请选择 Excel 文件");
        }
        String name = file.getOriginalFilename() == null ? "" : file.getOriginalFilename().toLowerCase();
        if (!name.endsWith(".xlsx") && !name.endsWith(".xls")) {
            throw new IllegalArgumentException("仅支持 xlsx 或 xls 文件");
        }

        ImportResult result = new ImportResult();
        try (Workbook workbook = WorkbookFactory.create(file.getInputStream())) {
            Sheet sheet = workbook.getSheetAt(0);
            for (int i = 1; i <= sheet.getLastRowNum(); i++) {
                Row row = sheet.getRow(i);
                if (row == null) {
                    continue;
                }
                try {
                    Goods goods = parseImportRow(row);
                    if (goodsMapper.selectBySpuCode(goods.spuCode) != null) {
                        throw new IllegalArgumentException("SPU 编码重复");
                    }
                    goods.status = 0;
                    goodsMapper.insert(goods);
                    result.successCount++;
                } catch (Exception ex) {
                    result.failCount++;
                    result.errors.add("第 " + (i + 1) + " 行：" + ex.getMessage());
                }
            }
        }
        logService.record(null, "IMPORT", "导入商品成功 " + result.successCount + " 条，失败 " + result.failCount + " 条");
        return result;
    }

    private Goods mustFind(Long id) {
        Goods goods = goodsMapper.selectById(id);
        if (goods == null) {
            throw new IllegalArgumentException("商品不存在");
        }
        return goods;
    }

    private Goods toGoods(GoodsSaveRequest request) {
        Goods goods = new Goods();
        goods.spuCode = request.spuCode;
        goods.goodsName = request.goodsName;
        goods.categoryId = request.categoryId;
        goods.price = request.price;
        goods.stockNum = request.stockNum == null ? 0 : request.stockNum;
        goods.status = request.status == null ? 0 : request.status;
        goods.mainImg = request.mainImg;
        goods.description = request.description;
        goods.warnStock = request.warnStock;
        return goods;
    }

    private Goods parseImportRow(Row row) {
        Goods goods = new Goods();
        goods.spuCode = text(row.getCell(0));
        goods.goodsName = text(row.getCell(1));
        goods.categoryId = longValue(row.getCell(2));
        goods.price = decimalValue(row.getCell(3));
        goods.stockNum = intValue(row.getCell(4));
        goods.warnStock = intValue(row.getCell(5));
        goods.mainImg = text(row.getCell(6));
        goods.description = text(row.getCell(7));
        if (goods.spuCode.isBlank() || goods.goodsName.isBlank() || goods.categoryId == null) {
            throw new IllegalArgumentException("SPU、商品名称、分类 ID 为必填项");
        }
        return goods;
    }

    private void writeHeader(Row row) {
        String[] headers = {"SPU 编码", "商品名称", "分类 ID/名称", "价格", "库存", "预警库存", "主图地址", "商品详情", "状态"};
        for (int i = 0; i < headers.length; i++) {
            row.createCell(i).setCellValue(headers[i]);
        }
    }

    private void writeGoodsRow(Row row, Goods goods) {
        row.createCell(0).setCellValue(goods.spuCode);
        row.createCell(1).setCellValue(goods.goodsName);
        row.createCell(2).setCellValue(goods.categoryName == null ? String.valueOf(goods.categoryId) : goods.categoryName);
        row.createCell(3).setCellValue(goods.price == null ? "" : goods.price.toPlainString());
        row.createCell(4).setCellValue(goods.stockNum == null ? 0 : goods.stockNum);
        row.createCell(5).setCellValue(goods.warnStock == null ? defaultWarnStock : goods.warnStock);
        row.createCell(6).setCellValue(goods.mainImg == null ? "" : goods.mainImg);
        row.createCell(7).setCellValue(goods.description == null ? "" : goods.description);
        row.createCell(8).setCellValue(statusName(goods.status));
    }

    private String text(Cell cell) {
        if (cell == null) {
            return "";
        }
        return switch (cell.getCellType()) {
            case STRING -> cell.getStringCellValue().trim();
            case NUMERIC -> String.valueOf((long) cell.getNumericCellValue());
            case BOOLEAN -> String.valueOf(cell.getBooleanCellValue());
            default -> "";
        };
    }

    private Long longValue(Cell cell) {
        String value = text(cell);
        return value.isBlank() ? null : Long.parseLong(value);
    }

    private Integer intValue(Cell cell) {
        String value = text(cell);
        return value.isBlank() ? null : Integer.parseInt(value);
    }

    private BigDecimal decimalValue(Cell cell) {
        if (cell == null) {
            return null;
        }
        return switch (cell.getCellType()) {
            case NUMERIC -> BigDecimal.valueOf(cell.getNumericCellValue());
            case STRING -> cell.getStringCellValue().isBlank() ? null : new BigDecimal(cell.getStringCellValue().trim());
            default -> null;
        };
    }

    private String statusName(Integer status) {
        if (status == null) {
            return "未知";
        }
        return switch (status) {
            case 0 -> "待审核";
            case 1 -> "已上架";
            case 2 -> "已下架";
            default -> "未知";
        };
    }
}
