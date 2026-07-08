package com.example.goods.common;

import java.util.List;

public class PageResult<T> {
    public List<T> records;
    public long total;
    public int page;
    public int pageSize;

    public PageResult() {
    }

    public PageResult(List<T> records, long total, int page, int pageSize) {
        this.records = records;
        this.total = total;
        this.page = page;
        this.pageSize = pageSize;
    }
}

