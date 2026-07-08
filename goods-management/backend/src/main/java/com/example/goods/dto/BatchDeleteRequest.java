package com.example.goods.dto;

import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public class BatchDeleteRequest {
    @NotEmpty(message = "商品 ID 不能为空")
    public List<Long> ids;
}

