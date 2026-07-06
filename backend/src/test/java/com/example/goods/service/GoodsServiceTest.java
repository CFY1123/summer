package com.example.goods.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

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
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;

class GoodsServiceTest {
    private GoodsMapper goodsMapper;
    private LogService logService;
    private GoodsService goodsService;

    @BeforeEach
    void setUp() {
        goodsMapper = org.mockito.Mockito.mock(GoodsMapper.class);
        logService = org.mockito.Mockito.mock(LogService.class);
        goodsService = new GoodsService(goodsMapper, logService);
        ReflectionTestUtils.setField(goodsService, "defaultWarnStock", 10);
    }

    @Test
    void createShouldSetPendingStatusAndWriteLog() {
        GoodsSaveRequest request = sampleRequest();
        when(goodsMapper.selectBySpuCode("SPU001")).thenReturn(null);
        when(goodsMapper.selectById(100L)).thenReturn(sampleGoods(100L));
        doAnswer(invocation -> {
            Goods goods = invocation.getArgument(0);
            goods.id = 100L;
            return 1;
        }).when(goodsMapper).insert(any(Goods.class));

        Goods result = goodsService.create(request);

        ArgumentCaptor<Goods> captor = ArgumentCaptor.forClass(Goods.class);
        verify(goodsMapper).insert(captor.capture());
        Goods inserted = captor.getValue();
        assertEquals(0, inserted.status);
        assertEquals("SPU001", inserted.spuCode);
        verify(logService).record(any(Goods.class), eq("CREATE"), eq("新增商品：测试商品"));
        assertEquals(100L, result.id);
    }

    @Test
    void createShouldRejectDuplicatedSpuCode() {
        when(goodsMapper.selectBySpuCode("SPU001")).thenReturn(sampleGoods(1L));

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> goodsService.create(sampleRequest()));
        assertEquals("SPU 编码已存在", exception.getMessage());

        verify(goodsMapper, never()).insert(any(Goods.class));
    }

    @Test
    void updateOffSaleGoodsShouldReturnToPending() {
        Goods exists = sampleGoods(1L);
        exists.status = 2;
        GoodsSaveRequest request = sampleRequest();
        request.status = 1;
        when(goodsMapper.selectById(1L)).thenReturn(exists);
        when(goodsMapper.selectBySpuCode("SPU001")).thenReturn(exists);

        goodsService.update(1L, request);

        ArgumentCaptor<Goods> captor = ArgumentCaptor.forClass(Goods.class);
        verify(goodsMapper).update(captor.capture());
        assertEquals(0, captor.getValue().status);
        verify(logService).record(any(Goods.class), eq("UPDATE"), eq("编辑商品：测试商品"));
    }

    @Test
    void updateShouldRejectDuplicatedSpuCode() {
        Goods exists = sampleGoods(1L);
        Goods another = sampleGoods(2L);
        another.spuCode = "SPU002";
        GoodsSaveRequest request = sampleRequest();
        request.spuCode = "SPU002";
        when(goodsMapper.selectById(1L)).thenReturn(exists);
        when(goodsMapper.selectBySpuCode("SPU002")).thenReturn(another);

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> goodsService.update(1L, request));
        assertEquals("SPU 编码已存在", exception.getMessage());

        verify(goodsMapper, never()).update(any(Goods.class));
    }

    @Test
    void updateShouldKeepStatusWhenNotProvided() {
        Goods exists = sampleGoods(1L);
        exists.status = 1;
        GoodsSaveRequest request = sampleRequest();
        request.status = null;
        when(goodsMapper.selectById(1L)).thenReturn(exists);
        when(goodsMapper.selectBySpuCode("SPU001")).thenReturn(exists);

        goodsService.update(1L, request);

        ArgumentCaptor<Goods> captor = ArgumentCaptor.forClass(Goods.class);
        verify(goodsMapper).update(captor.capture());
        assertEquals(1, captor.getValue().status);
    }

    @Test
    void updateStatusShouldPersistAndWriteLog() {
        when(goodsMapper.selectById(1L)).thenReturn(sampleGoods(1L));

        goodsService.updateStatus(1L, 2);

        verify(goodsMapper).updateStatus(1L, 2);
        verify(logService).record(any(Goods.class), eq("STATUS"), eq("修改商品状态为：已下架"));
    }

    @Test
    void updateStockShouldPersistAndWriteLog() {
        when(goodsMapper.selectById(1L)).thenReturn(sampleGoods(1L));

        goodsService.updateStock(1L, 88);

        verify(goodsMapper).updateStock(1L, 88);
        verify(logService).record(any(Goods.class), eq("STOCK"), eq("调整库存为：88"));
    }

    @Test
    void deleteShouldPersistAndWriteLog() {
        when(goodsMapper.selectById(1L)).thenReturn(sampleGoods(1L));

        goodsService.delete(1L);

        verify(goodsMapper).logicalDelete(1L);
        verify(logService).record(any(Goods.class), eq("DELETE"), eq("删除商品：测试商品"));
    }

    @Test
    void batchOperationsShouldCallMapper() {
        BatchStatusRequest statusRequest = new BatchStatusRequest();
        statusRequest.ids = List.of(1L, 2L);
        statusRequest.status = 2;
        goodsService.updateStatusBatch(statusRequest);
        verify(goodsMapper).updateStatusBatch(statusRequest.ids, 2);

        BatchStockRequest stockRequest = new BatchStockRequest();
        stockRequest.ids = List.of(1L, 2L);
        stockRequest.stockNum = 66;
        goodsService.updateStockBatch(stockRequest);
        verify(goodsMapper).updateStockBatch(stockRequest.ids, 66);

        BatchDeleteRequest deleteRequest = new BatchDeleteRequest();
        deleteRequest.ids = List.of(1L, 2L);
        goodsService.deleteBatch(deleteRequest);
        verify(goodsMapper).logicalDeleteBatch(deleteRequest.ids);
    }

    @Test
    void pageShouldReturnPageResult() {
        GoodsQuery query = new GoodsQuery();
        query.page = 1;
        query.pageSize = 10;
        List<Goods> goodsList = List.of(sampleGoods(1L), sampleGoods(2L));
        when(goodsMapper.selectPage(any(GoodsQuery.class))).thenReturn(goodsList);
        when(goodsMapper.countPage(any(GoodsQuery.class))).thenReturn(100L);

        PageResult<Goods> result = goodsService.page(query);

        assertNotNull(result);
        assertEquals(2, result.records.size());
        assertEquals(100L, result.total);
        assertEquals(1, result.page);
        assertEquals(10, result.pageSize);
        assertEquals(10, query.warnStock);
    }

    @Test
    void statsShouldReturnDashboardStats() {
        DashboardStats expected = new DashboardStats();
        expected.total = 10;
        expected.onSale = 5;
        expected.pending = 3;
        expected.stockWarning = 2;
        when(goodsMapper.selectStats(10)).thenReturn(expected);

        DashboardStats result = goodsService.stats();

        assertNotNull(result);
        assertEquals(10, result.total);
        assertEquals(5, result.onSale);
        assertEquals(3, result.pending);
        assertEquals(2, result.stockWarning);
    }

    @Test
    void statsShouldReturnEmptyWhenNull() {
        when(goodsMapper.selectStats(10)).thenReturn(null);

        DashboardStats result = goodsService.stats();

        assertNotNull(result);
        assertEquals(0L, result.total);
        assertEquals(0L, result.onSale);
        assertEquals(0L, result.pending);
        assertEquals(0L, result.stockWarning);
    }

    @Test
    void updateNonExistentGoodsShouldThrowException() {
        when(goodsMapper.selectById(999L)).thenReturn(null);

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> goodsService.update(999L, sampleRequest()));
        assertEquals("商品不存在", exception.getMessage());
    }

    @Test
    void updateStatusNonExistentGoodsShouldThrowException() {
        when(goodsMapper.selectById(999L)).thenReturn(null);

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> goodsService.updateStatus(999L, 1));
        assertEquals("商品不存在", exception.getMessage());
    }

    @Test
    void updateStockNonExistentGoodsShouldThrowException() {
        when(goodsMapper.selectById(999L)).thenReturn(null);

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> goodsService.updateStock(999L, 10));
        assertEquals("商品不存在", exception.getMessage());
    }

    @Test
    void deleteNonExistentGoodsShouldThrowException() {
        when(goodsMapper.selectById(999L)).thenReturn(null);

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> goodsService.delete(999L));
        assertEquals("商品不存在", exception.getMessage());
    }

    @Test
    void importExcelShouldRejectEmptyFile() {
        MockMultipartFile emptyFile = new MockMultipartFile("file", "test.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", new byte[0]);

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            try {
                goodsService.importExcel(emptyFile);
            } catch (Exception e) {
                throw new IllegalArgumentException(e.getMessage());
            }
        });
        assertEquals("请选择 Excel 文件", exception.getMessage());
    }

    @Test
    void importExcelShouldRejectNonExcelFile() {
        MockMultipartFile csvFile = new MockMultipartFile("file", "test.csv", "text/csv", "test content".getBytes());

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            try {
                goodsService.importExcel(csvFile);
            } catch (Exception e) {
                throw new IllegalArgumentException(e.getMessage());
            }
        });
        assertEquals("仅支持 xlsx 或 xls 文件", exception.getMessage());
    }

    @Test
    void importExcelShouldHandleSuccessAndFailure() throws Exception {
        byte[] excelBytes = createSampleExcel();
        MockMultipartFile file = new MockMultipartFile("file", "test.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", excelBytes);

        when(goodsMapper.selectBySpuCode("SPU001")).thenReturn(null);
        when(goodsMapper.selectBySpuCode("SPU002")).thenReturn(sampleGoods(1L));
        doAnswer(invocation -> {
            Goods goods = invocation.getArgument(0);
            goods.id = 100L;
            return 1;
        }).when(goodsMapper).insert(any(Goods.class));

        ImportResult result = goodsService.importExcel(file);

        assertEquals(1, result.successCount);
        assertEquals(1, result.failCount);
        assertEquals(1, result.errors.size());
        assertEquals("第 3 行：SPU 编码重复", result.errors.get(0));
    }

    private byte[] createSampleExcel() throws Exception {
        try (XSSFWorkbook workbook = new XSSFWorkbook()) {
            var sheet = workbook.createSheet("商品数据");
            var headerRow = sheet.createRow(0);
            String[] headers = { "SPU 编码", "商品名称", "分类 ID", "价格", "库存", "预警库存", "主图地址", "商品详情" };
            for (int i = 0; i < headers.length; i++) {
                headerRow.createCell(i).setCellValue(headers[i]);
            }

            var row1 = sheet.createRow(1);
            row1.createCell(0).setCellValue("SPU001");
            row1.createCell(1).setCellValue("商品1");
            row1.createCell(2).setCellValue(1);
            row1.createCell(3).setCellValue(99.99);
            row1.createCell(4).setCellValue(100);
            row1.createCell(5).setCellValue(10);

            var row2 = sheet.createRow(2);
            row2.createCell(0).setCellValue("SPU002");
            row2.createCell(1).setCellValue("商品2");
            row2.createCell(2).setCellValue(2);
            row2.createCell(3).setCellValue(199.99);
            row2.createCell(4).setCellValue(50);
            row2.createCell(5).setCellValue(5);

            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            workbook.write(outputStream);
            return outputStream.toByteArray();
        }
    }

    private GoodsSaveRequest sampleRequest() {
        GoodsSaveRequest request = new GoodsSaveRequest();
        request.spuCode = "SPU001";
        request.goodsName = "测试商品";
        request.categoryId = 2L;
        request.price = new BigDecimal("99.00");
        request.stockNum = 20;
        request.warnStock = 10;
        return request;
    }

    private Goods sampleGoods(Long id) {
        Goods goods = new Goods();
        goods.id = id;
        goods.spuCode = "SPU001";
        goods.goodsName = "测试商品";
        goods.categoryId = 2L;
        goods.price = new BigDecimal("99.00");
        goods.stockNum = 20;
        goods.status = 1;
        return goods;
    }
}
