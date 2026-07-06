package com.example.goods.dto;

import jakarta.validation.constraints.NotNull;

public class StockRequest {
    @NotNull(message = "库存不能为空")
    public Integer stockNum;
}

