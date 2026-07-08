package com.example.goods.dto;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.util.List;

public class BatchStockRequest {
    @NotEmpty(message = "商品 ID 不能为空")
    public List<Long> ids;

    @NotNull(message = "库存不能为空")
    public Integer stockNum;
}

