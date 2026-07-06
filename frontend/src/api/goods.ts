import http from './http'
import type { Category, DashboardStats, Goods, GoodsForm, GoodsQuery, ImportResult, PageResult } from '../types/goods'

export async function fetchGoods(query: GoodsQuery) {
  const { data } = await http.get<{ data: PageResult<Goods> }>('/goods', { params: query })
  return data.data
}

export async function fetchStats() {
  const { data } = await http.get<{ data: DashboardStats }>('/goods/stats')
  return data.data
}

export async function fetchCategories() {
  const { data } = await http.get<{ data: Category[] }>('/categories')
  return data.data
}

export async function createGoods(payload: GoodsForm) {
  const { data } = await http.post<{ data: Goods }>('/goods', payload)
  return data.data
}

export async function updateGoods(id: number, payload: GoodsForm) {
  const { data } = await http.put<{ data: Goods }>(`/goods/${id}`, payload)
  return data.data
}

export async function updateGoodsStatus(id: number, status: number) {
  await http.patch(`/goods/${id}/status`, { status })
}

export async function updateBatchStatus(ids: number[], status: number) {
  await http.patch('/goods/status', { ids, status })
}

export async function updateGoodsStock(id: number, stockNum: number) {
  await http.patch(`/goods/${id}/stock`, { stockNum })
}

export async function updateBatchStock(ids: number[], stockNum: number) {
  await http.patch('/goods/stock', { ids, stockNum })
}

export async function deleteGoods(id: number) {
  await http.delete(`/goods/${id}`)
}

export async function deleteBatchGoods(ids: number[]) {
  await http.delete('/goods', { data: { ids } })
}

export async function importGoods(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await http.post<{ data: ImportResult }>('/goods/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data.data
}

export async function downloadFile(url: string, filename: string, params?: Record<string, unknown>) {
  const response = await http.get(url, { params, responseType: 'blob' })
  const blobUrl = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(blobUrl)
}

