package com.example.goods.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class Goods {
    public Long id;
    public String spuCode;
    public String goodsName;
    public Long categoryId;
    public String categoryName;
    public BigDecimal price;
    public Integer stockNum;
    public Integer status;
    public String mainImg;
    public String description;
    public Integer warnStock;
    public Integer isDelete;
    public LocalDateTime createTime;
    public LocalDateTime updateTime;
}

