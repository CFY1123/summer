package com.example.goods.dto;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.util.List;

public class BatchStatusRequest {
    @NotEmpty(message = "商品 ID 不能为空")
    public List<Long> ids;

    @NotNull(message = "商品状态不能为空")
    public Integer status;
}

