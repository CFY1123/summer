export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PageResult<T> {
  records: T[]
  total: number
  page: number
  pageSize: number
}

export interface Goods {
  id: number
  spuCode: string
  goodsName: string
  categoryId: number
  categoryName?: string
  price?: number
  stockNum: number
  status: 0 | 1 | 2
  mainImg?: string
  description?: string
  warnStock?: number
  createTime?: string
  updateTime?: string
}

export interface Category {
  id: number
  parentId: number
  categoryName: string
  sortNo: number
  status: number
}

export interface GoodsQuery {
  status?: number
  keyword?: string
  categoryId?: number
  stockStatus?: string
  startDate?: string
  endDate?: string
  page: number
  pageSize: number
}

export interface DashboardStats {
  total: number
  onSale: number
  pending: number
  stockWarning: number
}

export interface GoodsForm {
  id?: number
  spuCode: string
  goodsName: string
  categoryId?: number
  price?: number
  stockNum: number
  status: 0 | 1 | 2
  mainImg?: string
  description?: string
  warnStock?: number
}

export interface ImportResult {
  successCount: number
  failCount: number
  errors: string[]
}

