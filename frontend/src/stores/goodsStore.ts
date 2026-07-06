import { defineStore } from 'pinia'
import { fetchCategories, fetchGoods, fetchStats } from '../api/goods'
import type { Category, DashboardStats, Goods, GoodsQuery } from '../types/goods'

const defaultQuery = (): GoodsQuery => ({
  page: 1,
  pageSize: 10
})

export const useGoodsStore = defineStore('goods', {
  state: () => ({
    list: [] as Goods[],
    total: 0,
    loading: false,
    query: defaultQuery(),
    categories: [] as Category[],
    stats: {
      total: 0,
      onSale: 0,
      pending: 0,
      stockWarning: 0
    } as DashboardStats
  }),
  actions: {
    async loadGoods() {
      this.loading = true
      try {
        const page = await fetchGoods(this.query)
        this.list = page.records
        this.total = page.total
      } finally {
        this.loading = false
      }
    },
    async loadStats() {
      this.stats = await fetchStats()
    },
    async loadCategories() {
      this.categories = await fetchCategories()
    },
    async refresh() {
      await Promise.all([this.loadGoods(), this.loadStats()])
    },
    resetQuery() {
      this.query = defaultQuery()
    }
  }
})

