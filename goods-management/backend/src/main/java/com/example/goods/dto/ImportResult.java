package com.example.goods.dto;

import java.util.ArrayList;
import java.util.List;

public class ImportResult {
    public int successCount;
    public int failCount;
    public List<String> errors = new ArrayList<>();
}

