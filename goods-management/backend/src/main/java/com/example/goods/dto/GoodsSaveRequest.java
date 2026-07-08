package com.example.goods.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

public class GoodsSaveRequest {
    @NotBlank(message = "SPU 编码不能为空")
    public String spuCode;

    @NotBlank(message = "商品名称不能为空")
    public String goodsName;

    @NotNull(message = "商品分类不能为空")
    public Long categoryId;

    public BigDecimal price;
    public Integer stockNum = 0;
    public Integer status = 0;
    public String mainImg;
    public String description;
    public Integer warnStock;
}

