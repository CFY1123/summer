package com.example.goods.mapper;

import com.example.goods.dto.DashboardStats;
import com.example.goods.dto.GoodsQuery;
import com.example.goods.model.Goods;
import java.util.List;
import org.apache.ibatis.annotations.Param;

public interface GoodsMapper {
    List<Goods> selectPage(@Param("query") GoodsQuery query);

    long countPage(@Param("query") GoodsQuery query);

    DashboardStats selectStats(@Param("warnStock") Integer warnStock);

    Goods selectById(@Param("id") Long id);

    Goods selectBySpuCode(@Param("spuCode") String spuCode);

    int insert(Goods goods);

    int update(Goods goods);

    int updateStatus(@Param("id") Long id, @Param("status") Integer status);

    int updateStatusBatch(@Param("ids") List<Long> ids, @Param("status") Integer status);

    int updateStock(@Param("id") Long id, @Param("stockNum") Integer stockNum);

    int updateStockBatch(@Param("ids") List<Long> ids, @Param("stockNum") Integer stockNum);

    int logicalDelete(@Param("id") Long id);

    int logicalDeleteBatch(@Param("ids") List<Long> ids);
}

