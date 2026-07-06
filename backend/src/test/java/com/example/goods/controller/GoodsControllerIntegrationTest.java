package com.example.goods.controller;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.goods.GoodsManagementApplication;
import com.example.goods.dto.BatchDeleteRequest;
import com.example.goods.dto.BatchStatusRequest;
import com.example.goods.dto.BatchStockRequest;
import com.example.goods.dto.GoodsSaveRequest;
import com.example.goods.dto.StatusRequest;
import com.example.goods.dto.StockRequest;
import com.example.goods.mapper.GoodsMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(classes = GoodsManagementApplication.class)
@AutoConfigureMockMvc
class GoodsControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private GoodsMapper goodsMapper;

    private Long createdGoodsId;

    @BeforeEach
    void setUp() {
    }

    @AfterEach
    void tearDown() {
        if (createdGoodsId != null) {
            try {
                goodsMapper.logicalDelete(createdGoodsId);
            } catch (Exception e) {
            }
        }
    }

    @Test
    void pageShouldReturnPagedGoods() throws Exception {
        mockMvc.perform(get("/goods")
                        .param("page", "1")
                        .param("pageSize", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.records").isArray())
                .andExpect(jsonPath("$.data.total").isNumber())
                .andExpect(jsonPath("$.data.page").value(1))
                .andExpect(jsonPath("$.data.pageSize").value(10));
    }

    @Test
    void statsShouldReturnDashboardStats() throws Exception {
        mockMvc.perform(get("/goods/stats"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.total").isNumber())
                .andExpect(jsonPath("$.data.onSale").isNumber())
                .andExpect(jsonPath("$.data.pending").isNumber())
                .andExpect(jsonPath("$.data.stockWarning").isNumber());
    }

    @Test
    void createShouldReturnCreatedGoods() throws Exception {
        GoodsSaveRequest request = new GoodsSaveRequest();
        request.spuCode = "SPU_TEST_" + System.currentTimeMillis();
        request.goodsName = "测试商品";
        request.categoryId = 2L;
        request.price = new BigDecimal("99.99");
        request.stockNum = 50;
        request.warnStock = 10;

        String response = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.spuCode").value(request.spuCode))
                .andExpect(jsonPath("$.data.goodsName").value(request.goodsName))
                .andExpect(jsonPath("$.data.categoryId").value(request.categoryId))
                .andExpect(jsonPath("$.data.status").value(0))
                .andExpect(jsonPath("$.data.id").isNumber())
                .andReturn()
                .getResponse()
                .getContentAsString();

        createdGoodsId = objectMapper.readTree(response).get("data").get("id").asLong();
    }

    @Test
    void createShouldRejectEmptySpuCode() throws Exception {
        GoodsSaveRequest request = new GoodsSaveRequest();
        request.spuCode = "";
        request.goodsName = "测试商品";
        request.categoryId = 2L;

        mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void createShouldRejectEmptyGoodsName() throws Exception {
        GoodsSaveRequest request = new GoodsSaveRequest();
        request.spuCode = "SPU_TEST_" + System.currentTimeMillis();
        request.goodsName = "";
        request.categoryId = 2L;

        mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void createShouldRejectDuplicatedSpuCode() throws Exception {
        GoodsSaveRequest request = new GoodsSaveRequest();
        request.spuCode = "SPU202607020001";
        request.goodsName = "重复商品";
        request.categoryId = 2L;

        mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void updateShouldReturnUpdatedGoods() throws Exception {
        GoodsSaveRequest createRequest = new GoodsSaveRequest();
        createRequest.spuCode = "SPU_UPDATE_" + System.currentTimeMillis();
        createRequest.goodsName = "原始商品";
        createRequest.categoryId = 2L;
        createRequest.price = new BigDecimal("99.00");

        String createResponse = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        createdGoodsId = objectMapper.readTree(createResponse).get("data").get("id").asLong();

        GoodsSaveRequest updateRequest = new GoodsSaveRequest();
        updateRequest.spuCode = createRequest.spuCode;
        updateRequest.goodsName = "更新商品";
        updateRequest.categoryId = 3L;
        updateRequest.price = new BigDecimal("199.00");

        mockMvc.perform(put("/goods/{id}", createdGoodsId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.goodsName").value("更新商品"))
                .andExpect(jsonPath("$.data.categoryId").value(3))
                .andExpect(jsonPath("$.data.price").value(199.0));
    }

    @Test
    void updateShouldRejectNonExistentGoods() throws Exception {
        GoodsSaveRequest request = new GoodsSaveRequest();
        request.spuCode = "SPU_NONEXIST_" + System.currentTimeMillis();
        request.goodsName = "不存在商品";
        request.categoryId = 2L;

        mockMvc.perform(put("/goods/{id}", 999999L)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void updateStatusShouldUpdateGoodsStatus() throws Exception {
        GoodsSaveRequest createRequest = new GoodsSaveRequest();
        createRequest.spuCode = "SPU_STATUS_" + System.currentTimeMillis();
        createRequest.goodsName = "状态测试商品";
        createRequest.categoryId = 2L;

        String createResponse = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        createdGoodsId = objectMapper.readTree(createResponse).get("data").get("id").asLong();

        StatusRequest statusRequest = new StatusRequest();
        statusRequest.status = 1;

        mockMvc.perform(patch("/goods/{id}/status", createdGoodsId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(statusRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    void updateStockShouldUpdateGoodsStock() throws Exception {
        GoodsSaveRequest createRequest = new GoodsSaveRequest();
        createRequest.spuCode = "SPU_STOCK_" + System.currentTimeMillis();
        createRequest.goodsName = "库存测试商品";
        createRequest.categoryId = 2L;
        createRequest.stockNum = 100;

        String createResponse = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        createdGoodsId = objectMapper.readTree(createResponse).get("data").get("id").asLong();

        StockRequest stockRequest = new StockRequest();
        stockRequest.stockNum = 200;

        mockMvc.perform(patch("/goods/{id}/stock", createdGoodsId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(stockRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    void deleteShouldRemoveGoods() throws Exception {
        GoodsSaveRequest createRequest = new GoodsSaveRequest();
        createRequest.spuCode = "SPU_DELETE_" + System.currentTimeMillis();
        createRequest.goodsName = "删除测试商品";
        createRequest.categoryId = 2L;

        String createResponse = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        createdGoodsId = objectMapper.readTree(createResponse).get("data").get("id").asLong();

        mockMvc.perform(delete("/goods/{id}", createdGoodsId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));

        createdGoodsId = null;
    }

    @Test
    void batchUpdateStatusShouldUpdateMultipleGoods() throws Exception {
        GoodsSaveRequest createRequest1 = new GoodsSaveRequest();
        createRequest1.spuCode = "SPU_BATCH1_" + System.currentTimeMillis();
        createRequest1.goodsName = "批量商品1";
        createRequest1.categoryId = 2L;

        GoodsSaveRequest createRequest2 = new GoodsSaveRequest();
        createRequest2.spuCode = "SPU_BATCH2_" + System.currentTimeMillis();
        createRequest2.goodsName = "批量商品2";
        createRequest2.categoryId = 2L;

        String response1 = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest1)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        String response2 = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest2)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        Long id1 = objectMapper.readTree(response1).get("data").get("id").asLong();
        Long id2 = objectMapper.readTree(response2).get("data").get("id").asLong();

        BatchStatusRequest batchRequest = new BatchStatusRequest();
        batchRequest.ids = List.of(id1, id2);
        batchRequest.status = 2;

        mockMvc.perform(patch("/goods/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(batchRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));

        goodsMapper.logicalDelete(id1);
        goodsMapper.logicalDelete(id2);
    }

    @Test
    void batchUpdateStockShouldUpdateMultipleGoods() throws Exception {
        GoodsSaveRequest createRequest1 = new GoodsSaveRequest();
        createRequest1.spuCode = "SPU_BSTOCK1_" + System.currentTimeMillis();
        createRequest1.goodsName = "批量库存商品1";
        createRequest1.categoryId = 2L;

        GoodsSaveRequest createRequest2 = new GoodsSaveRequest();
        createRequest2.spuCode = "SPU_BSTOCK2_" + System.currentTimeMillis();
        createRequest2.goodsName = "批量库存商品2";
        createRequest2.categoryId = 2L;

        String response1 = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest1)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        String response2 = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest2)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        Long id1 = objectMapper.readTree(response1).get("data").get("id").asLong();
        Long id2 = objectMapper.readTree(response2).get("data").get("id").asLong();

        BatchStockRequest batchRequest = new BatchStockRequest();
        batchRequest.ids = List.of(id1, id2);
        batchRequest.stockNum = 999;

        mockMvc.perform(patch("/goods/stock")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(batchRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));

        goodsMapper.logicalDelete(id1);
        goodsMapper.logicalDelete(id2);
    }

    @Test
    void batchDeleteShouldRemoveMultipleGoods() throws Exception {
        GoodsSaveRequest createRequest1 = new GoodsSaveRequest();
        createRequest1.spuCode = "SPU_BDEL1_" + System.currentTimeMillis();
        createRequest1.goodsName = "批量删除商品1";
        createRequest1.categoryId = 2L;

        GoodsSaveRequest createRequest2 = new GoodsSaveRequest();
        createRequest2.spuCode = "SPU_BDEL2_" + System.currentTimeMillis();
        createRequest2.goodsName = "批量删除商品2";
        createRequest2.categoryId = 2L;

        String response1 = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest1)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        String response2 = mockMvc.perform(post("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest2)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        Long id1 = objectMapper.readTree(response1).get("data").get("id").asLong();
        Long id2 = objectMapper.readTree(response2).get("data").get("id").asLong();

        BatchDeleteRequest batchRequest = new BatchDeleteRequest();
        batchRequest.ids = List.of(id1, id2);

        mockMvc.perform(delete("/goods")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(batchRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    void searchByKeywordShouldFilterGoods() throws Exception {
        mockMvc.perform(get("/goods")
                        .param("keyword", "手机"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.records").isArray());
    }

    @Test
    void filterByStatusShouldFilterGoods() throws Exception {
        mockMvc.perform(get("/goods")
                        .param("status", "1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.records").isArray());
    }

    @Test
    void filterByCategoryShouldFilterGoods() throws Exception {
        mockMvc.perform(get("/goods")
                        .param("categoryId", "2"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.records").isArray());
    }
}