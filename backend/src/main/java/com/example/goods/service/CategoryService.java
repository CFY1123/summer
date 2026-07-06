package com.example.goods.service;

import com.example.goods.mapper.CategoryMapper;
import com.example.goods.model.Category;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class CategoryService {
    private final CategoryMapper categoryMapper;

    public CategoryService(CategoryMapper categoryMapper) {
        this.categoryMapper = categoryMapper;
    }

    public List<Category> listEnabled() {
        return categoryMapper.selectEnabled();
    }
}

