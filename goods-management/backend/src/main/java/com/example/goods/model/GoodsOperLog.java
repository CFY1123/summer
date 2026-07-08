package com.example.goods.model;

import java.time.LocalDateTime;

public class GoodsOperLog {
    public Long id;
    public Long goodsId;
    public String spuCode;
    public String operType;
    public String operContent;
    public String operator;
    public LocalDateTime operTime;
}

