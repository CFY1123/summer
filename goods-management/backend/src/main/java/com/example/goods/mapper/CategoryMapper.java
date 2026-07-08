package com.example.goods.mapper;

import com.example.goods.model.Category;
import java.util.List;

public interface CategoryMapper {
    List<Category> selectEnabled();
}

