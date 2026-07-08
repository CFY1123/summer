import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '../types/goods'

const http = axios.create({
  baseURL: '/api',
  timeout: 15000
})

http.interceptors.response.use(
  (response) => {
    const contentType = String(response.headers['content-type'] || '')
    if (contentType.includes('application/vnd.openxmlformats')) {
      return response
    }
    const body = response.data as ApiResponse<unknown>
    if (body && body.code !== 200) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return response
  },
  (error) => {
    ElMessage.error(error.response?.data?.message || error.message || '网络异常')
    return Promise.reject(error)
  }
)

export default http
