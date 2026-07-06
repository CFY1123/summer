package com.example.goods.controller;

import com.example.goods.common.ApiResponse;
import com.example.goods.common.PageResult;
import com.example.goods.dto.BatchDeleteRequest;
import com.example.goods.dto.BatchStatusRequest;
import com.example.goods.dto.BatchStockRequest;
import com.example.goods.dto.DashboardStats;
import com.example.goods.dto.GoodsQuery;
import com.example.goods.dto.GoodsSaveRequest;
import com.example.goods.dto.ImportResult;
import com.example.goods.dto.StatusRequest;
import com.example.goods.dto.StockRequest;
import com.example.goods.model.Goods;
import com.example.goods.service.GoodsService;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/goods")
public class GoodsController {
    private final GoodsService goodsService;

    public GoodsController(GoodsService goodsService) {
        this.goodsService = goodsService;
    }

    @GetMapping
    public ApiResponse<PageResult<Goods>> page(GoodsQuery query) {
        return ApiResponse.ok(goodsService.page(query));
    }

    @GetMapping("/stats")
    public ApiResponse<DashboardStats> stats() {
        return ApiResponse.ok(goodsService.stats());
    }

    @PostMapping
    public ApiResponse<Goods> create(@Valid @RequestBody GoodsSaveRequest request) {
        return ApiResponse.ok(goodsService.create(request));
    }

    @PutMapping("/{id}")
    public ApiResponse<Goods> update(@PathVariable Long id, @Valid @RequestBody GoodsSaveRequest request) {
        return ApiResponse.ok(goodsService.update(id, request));
    }

    @PatchMapping("/{id}/status")
    public ApiResponse<Void> updateStatus(@PathVariable Long id, @Valid @RequestBody StatusRequest request) {
        goodsService.updateStatus(id, request.status);
        return ApiResponse.ok(null);
    }

    @PatchMapping("/status")
    public ApiResponse<Void> updateStatusBatch(@Valid @RequestBody BatchStatusRequest request) {
        goodsService.updateStatusBatch(request);
        return ApiResponse.ok(null);
    }

    @PatchMapping("/{id}/stock")
    public ApiResponse<Void> updateStock(@PathVariable Long id, @Valid @RequestBody StockRequest request) {
        goodsService.updateStock(id, request.stockNum);
        return ApiResponse.ok(null);
    }

    @PatchMapping("/stock")
    public ApiResponse<Void> updateStockBatch(@Valid @RequestBody BatchStockRequest request) {
        goodsService.updateStockBatch(request);
        return ApiResponse.ok(null);
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        goodsService.delete(id);
        return ApiResponse.ok(null);
    }

    @DeleteMapping
    public ApiResponse<Void> deleteBatch(@Valid @RequestBody BatchDeleteRequest request) {
        goodsService.deleteBatch(request);
        return ApiResponse.ok(null);
    }

    @GetMapping("/export")
    public void exportExcel(GoodsQuery query, HttpServletResponse response) throws IOException {
        goodsService.exportExcel(query, response);
    }

    @GetMapping("/import-template")
    public void downloadTemplate(HttpServletResponse response) throws IOException {
        goodsService.downloadTemplate(response);
    }

    @PostMapping("/import")
    public ApiResponse<ImportResult> importExcel(@RequestParam("file") MultipartFile file) throws IOException {
        return ApiResponse.ok(goodsService.importExcel(file));
    }
}

