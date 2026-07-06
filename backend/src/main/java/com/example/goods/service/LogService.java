package com.example.goods.service;

import com.example.goods.mapper.GoodsOperLogMapper;
import com.example.goods.model.Goods;
import com.example.goods.model.GoodsOperLog;
import org.springframework.stereotype.Service;

@Service
public class LogService {
    private final GoodsOperLogMapper logMapper;

    public LogService(GoodsOperLogMapper logMapper) {
        this.logMapper = logMapper;
    }

    public void record(Goods goods, String type, String content) {
        GoodsOperLog log = new GoodsOperLog();
        log.goodsId = goods == null ? null : goods.id;
        log.spuCode = goods == null ? null : goods.spuCode;
        log.operType = type;
        log.operContent = content;
        log.operator = "admin";
        logMapper.insert(log);
    }
}

