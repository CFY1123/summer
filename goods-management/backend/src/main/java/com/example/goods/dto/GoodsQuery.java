package com.example.goods.dto;

import java.time.LocalDate;
import org.springframework.format.annotation.DateTimeFormat;

public class GoodsQuery {
    public Integer status;
    public String keyword;
    public Long categoryId;
    public String stockStatus;
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    public LocalDate startDate;
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    public LocalDate endDate;
    public Integer page = 1;
    public Integer pageSize = 10;
    public Integer warnStock = 10;

    public int offset() {
        int safePage = page == null || page < 1 ? 1 : page;
        int safePageSize = pageSize == null || pageSize < 1 ? 10 : pageSize;
        return (safePage - 1) * safePageSize;
    }

    public int limit() {
        return pageSize == null || pageSize < 1 ? 10 : pageSize;
    }

    public int getOffset() {
        return offset();
    }

    public int getLimit() {
        return limit();
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public Long getCategoryId() {
        return categoryId;
    }

    public void setCategoryId(Long categoryId) {
        this.categoryId = categoryId;
    }

    public String getStockStatus() {
        return stockStatus;
    }

    public void setStockStatus(String stockStatus) {
        this.stockStatus = stockStatus;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }

    public LocalDate getEndDate() {
        return endDate;
    }

    public void setEndDate(LocalDate endDate) {
        this.endDate = endDate;
    }

    public Integer getPage() {
        return page;
    }

    public void setPage(Integer page) {
        this.page = page;
    }

    public Integer getPageSize() {
        return pageSize;
    }

    public void setPageSize(Integer pageSize) {
        this.pageSize = pageSize;
    }

    public Integer getWarnStock() {
        return warnStock;
    }

    public void setWarnStock(Integer warnStock) {
        this.warnStock = warnStock;
    }
}
