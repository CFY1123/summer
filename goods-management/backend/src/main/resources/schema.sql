DROP TABLE IF EXISTS goods_oper_log;
DROP TABLE IF EXISTS goods;
DROP TABLE IF EXISTS goods_category;

CREATE TABLE goods_category (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '分类 ID',
    parent_id BIGINT NOT NULL DEFAULT 0 COMMENT '父分类 ID',
    category_name VARCHAR(100) NOT NULL COMMENT '分类名称',
    sort_no INT NOT NULL DEFAULT 0 COMMENT '排序号',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '0 禁用 1 启用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category_parent (parent_id),
    INDEX idx_category_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

CREATE TABLE goods (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '商品 ID',
    spu_code VARCHAR(64) NOT NULL COMMENT 'SPU 编码',
    goods_name VARCHAR(255) NOT NULL COMMENT '商品名称',
    category_id BIGINT NOT NULL COMMENT '分类 ID',
    price DECIMAL(10,2) NULL COMMENT '商品售价',
    stock_num INT NOT NULL DEFAULT 0 COMMENT '当前库存',
    status TINYINT NOT NULL DEFAULT 0 COMMENT '0 待审核 1 已上架 2 已下架',
    main_img VARCHAR(500) NULL COMMENT '商品主图地址',
    description TEXT NULL COMMENT '商品详情',
    warn_stock INT NULL COMMENT '商品独立预警库存',
    is_delete TINYINT NOT NULL DEFAULT 0 COMMENT '0 正常 1 删除',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_goods_spu (spu_code),
    INDEX idx_goods_status (status),
    INDEX idx_goods_category (category_id),
    INDEX idx_goods_create_time (create_time),
    INDEX idx_goods_stock (stock_num),
    INDEX idx_goods_deleted (is_delete)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品主表';

CREATE TABLE goods_oper_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志 ID',
    goods_id BIGINT NULL COMMENT '商品 ID',
    spu_code VARCHAR(64) NULL COMMENT 'SPU 编码',
    oper_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    oper_content VARCHAR(1000) NOT NULL COMMENT '操作内容',
    operator VARCHAR(64) NOT NULL COMMENT '操作人',
    oper_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_log_goods (goods_id),
    INDEX idx_log_spu (spu_code),
    INDEX idx_log_type (oper_type),
    INDEX idx_log_time (oper_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品操作日志表';

INSERT INTO goods_category (id, parent_id, category_name, sort_no, status) VALUES
(1, 0, '服饰鞋包', 1, 1),
(2, 1, '男装', 1, 1),
(3, 1, '女装', 2, 1),
(4, 0, '数码家电', 2, 1),
(5, 4, '手机', 1, 1),
(6, 4, '电脑', 2, 1),
(7, 0, '食品生鲜', 3, 1),
(8, 7, '休闲零食', 1, 1);

INSERT INTO goods (spu_code, goods_name, category_id, price, stock_num, status, main_img, description, warn_stock) VALUES
('SPU202607020001', '基础纯棉短袖 T 恤', 2, 79.00, 86, 1, 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300', '夏季基础款短袖 T 恤', 10),
('SPU202607020002', '高腰直筒牛仔裤', 3, 169.00, 8, 0, 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300', '通勤休闲直筒版型', 10),
('SPU202607020003', '旗舰智能手机 Pro', 5, 4999.00, 32, 1, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300', '高性能影像旗舰手机', 5),
('SPU202607020004', '轻薄办公笔记本电脑', 6, 6299.00, 0, 2, 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300', '14 英寸轻薄办公本', 5),
('SPU202607020005', '每日坚果礼盒', 8, 99.00, 4, 1, 'https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=300', '混合坚果独立包装', 10);

