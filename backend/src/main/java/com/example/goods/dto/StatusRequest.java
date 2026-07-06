package com.example.goods.dto;

import jakarta.validation.constraints.NotNull;

public class StatusRequest {
    @NotNull(message = "商品状态不能为空")
    public Integer status;
}

