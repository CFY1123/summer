package com.example.goods.model;

import java.time.LocalDateTime;

public class Category {
    public Long id;
    public Long parentId;
    public String categoryName;
    public Integer sortNo;
    public Integer status;
    public LocalDateTime createTime;
    public LocalDateTime updateTime;
}

