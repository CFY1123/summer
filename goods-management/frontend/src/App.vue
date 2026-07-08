<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">后台管理系统</div>
      <el-menu default-active="goods" background-color="#17202a" text-color="#cfd8dc" active-text-color="#ffffff">
        <el-menu-item index="home">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="goods">
          <el-icon><GoodsIcon /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-sub-menu index="category">
          <template #title>
            <el-icon><Grid /></el-icon>
            <span>分类管理</span>
          </template>
          <el-menu-item index="category-list">分类列表</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="stock">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="stock-list">库存明细</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="order">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>订单管理</span>
          </template>
          <el-menu-item index="order-list">订单列表</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="setting">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="warn-setting">库存预警设置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <p class="caption">电商运营后台</p>
          <h1>商品管理</h1>
        </div>
        <div class="toolbar">
          <el-button :icon="Search" @click="focusKeyword">搜索商品</el-button>
          <el-button type="primary" :icon="Plus" @click="openCreate">新建商品</el-button>
          <el-button :icon="Upload" @click="importVisible = true">批量导入</el-button>
          <el-button :icon="Download" @click="handleExport">Excel 导出</el-button>
        </div>
      </header>

      <div class="content-grid">
        <section class="main-panel">
          <section class="filter-area">
            <el-select v-model="store.query.status" clearable placeholder="商品状态">
              <el-option label="全部" :value="undefined" />
              <el-option label="待审核" :value="0" />
              <el-option label="已上架" :value="1" />
              <el-option label="已下架" :value="2" />
            </el-select>
            <el-input ref="keywordInput" v-model="store.query.keyword" clearable placeholder="商品名称 / SPU 编码" :prefix-icon="Search" />
            <el-select v-model="store.query.categoryId" clearable filterable placeholder="商品分类">
              <el-option v-for="item in leafCategories" :key="item.id" :label="item.categoryName" :value="item.id" />
            </el-select>
            <el-select v-model="store.query.stockStatus" clearable placeholder="库存状态">
              <el-option label="全部" value="" />
              <el-option label="正常" value="normal" />
              <el-option label="库存预警" value="warning" />
              <el-option label="无库存" value="empty" />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
            <div class="filter-actions">
              <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
              <el-button :icon="Refresh" @click="handleReset">重置</el-button>
            </div>
          </section>

          <div class="quick-tags">
            <el-check-tag v-for="tag in quickTags" :key="tag" @click="handleQuickTag(tag)">{{ tag }}</el-check-tag>
          </div>

          <el-table
            v-loading="store.loading"
            :data="store.list"
            class="goods-table"
            row-key="id"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="46" />
            <el-table-column label="商品信息" min-width="260">
              <template #default="{ row }">
                <div class="goods-info">
                  <el-image class="goods-img" :src="row.mainImg || fallbackImg" fit="cover" />
                  <div class="goods-text">
                    <strong>{{ row.goodsName }}</strong>
                    <div class="goods-tags">
                      <el-tag size="small" :type="statusTagType(row.status)">{{ statusName(row.status) }}</el-tag>
                      <el-tag v-if="isWarning(row)" size="small" type="danger">库存预警</el-tag>
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="spuCode" label="SPU 编码" min-width="160" />
            <el-table-column prop="categoryName" label="分类" min-width="110" />
            <el-table-column label="价格" width="110">
              <template #default="{ row }">{{ row.price == null ? '-' : `¥${Number(row.price).toFixed(2)}` }}</template>
            </el-table-column>
            <el-table-column prop="stockNum" label="库存" width="90" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ statusName(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" min-width="130">
              <template #default="{ row }">{{ formatDate(row.createTime) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-dropdown trigger="click" @command="(command: string) => handleRowCommand(command, row)">
                  <el-button size="small">
                    操作
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">编辑</el-dropdown-item>
                      <el-dropdown-item command="status">{{ statusActionText(row.status) }}</el-dropdown-item>
                      <el-dropdown-item command="stock">库存</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>

          <footer class="table-footer">
            <div class="batch-bar">
              <span>已选 {{ selectedRows.length }} 项</span>
              <el-button :disabled="!selectedRows.length" @click="openBatchEdit">编辑</el-button>
              <el-button :disabled="!selectedRows.length" @click="openBatchStock">库存</el-button>
              <el-button :disabled="!selectedRows.length" @click="handleBatchOffSale">下架</el-button>
              <el-button type="danger" :disabled="!selectedRows.length" @click="handleBatchDelete">删除</el-button>
            </div>
            <el-pagination
              v-model:current-page="store.query.page"
              v-model:page-size="store.query.pageSize"
              :page-sizes="[5, 10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="store.total"
              @size-change="store.refresh"
              @current-change="store.refresh"
            />
          </footer>
        </section>

        <aside class="stats-panel">
          <div class="stat-card">
            <el-icon class="stat-icon success"><CircleCheck /></el-icon>
            <span>全部商品</span>
            <strong>{{ store.stats.total }}</strong>
          </div>
          <div class="stat-card">
            <el-icon class="stat-icon warning"><Warning /></el-icon>
            <span>已上架</span>
            <strong>{{ store.stats.onSale }}</strong>
            <small>待审核 {{ store.stats.pending }}</small>
          </div>
          <div class="stat-card">
            <el-icon class="stat-icon danger"><WarningFilled /></el-icon>
            <span>库存预警</span>
            <strong>{{ store.stats.stockWarning }}</strong>
          </div>
        </aside>
      </div>
    </main>

    <el-dialog v-model="formVisible" :title="form.id ? '编辑商品' : '新建商品'" width="620px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="商品名称" prop="goodsName">
          <el-input v-model="form.goodsName" />
        </el-form-item>
        <el-form-item label="SPU 编码" prop="spuCode">
          <el-input v-model="form.spuCode" />
        </el-form-item>
        <el-form-item label="商品分类" prop="categoryId">
          <el-select v-model="form.categoryId" filterable placeholder="请选择分类">
            <el-option v-for="item in leafCategories" :key="item.id" :label="item.categoryName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="价格">
              <el-input-number v-model="form.price" :min="0" :precision="2" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="库存">
              <el-input-number v-model="form.stockNum" :min="-9999" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预警库存">
              <el-input-number v-model="form.warnStock" :min="0" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="主图地址">
          <el-input v-model="form.mainImg" />
        </el-form-item>
        <el-form-item label="商品详情">
          <el-input v-model="form.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="stockVisible" title="库存调整" width="420px">
      <el-form label-width="92px">
        <el-form-item label="商品">
          <span>{{ currentGoods?.goodsName || '批量商品' }}</span>
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="stockValue" :min="-9999" controls-position="right" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveStock">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importVisible" title="批量导入商品" width="560px">
      <div class="import-box">
        <el-button :icon="Download" @click="downloadFile('/goods/import-template', '商品导入模板.xlsx')">下载标准模板</el-button>
        <el-upload drag :auto-upload="false" :limit="1" accept=".xlsx,.xls" :on-change="handleFileChange">
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div>拖拽 Excel 到此处，或点击选择文件</div>
        </el-upload>
        <div v-if="importResult" class="import-result">
          <el-alert
            :title="`导入成功 ${importResult.successCount} 条，失败 ${importResult.failCount} 条`"
            type="info"
            show-icon
            :closable="false"
          />
          <ul v-if="importResult.errors.length">
            <li v-for="error in importResult.errors" :key="error">{{ error }}</li>
          </ul>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import {
  ArrowDown,
  Box,
  CircleCheck,
  Download,
  Goods as GoodsIcon,
  Grid,
  House,
  Plus,
  Refresh,
  Search,
  Setting,
  Tickets,
  Upload,
  UploadFilled,
  Warning,
  WarningFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type InputInstance, type UploadFile } from 'element-plus'
import {
  createGoods,
  deleteBatchGoods,
  deleteGoods,
  downloadFile,
  importGoods,
  updateBatchStatus,
  updateBatchStock,
  updateGoods,
  updateGoodsStatus,
  updateGoodsStock
} from './api/goods'
import { useGoodsStore } from './stores/goodsStore'
import type { Goods, GoodsForm, ImportResult } from './types/goods'

const store = useGoodsStore()
const keywordInput = ref<InputInstance>()
const formRef = ref<FormInstance>()
const dateRange = ref<[string, string] | null>(null)
const selectedRows = ref<Goods[]>([])
const formVisible = ref(false)
const stockVisible = ref(false)
const importVisible = ref(false)
const currentGoods = ref<Goods | null>(null)
const stockValue = ref(0)
const isBatchStock = ref(false)
const importResult = ref<ImportResult | null>(null)
const fallbackImg = 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=300'
const quickTags = ['筛选', '关键词搜索', '商品分类', '商品类型', '价格区间', '库存状态', '上下架']

const form = reactive<GoodsForm>({
  spuCode: '',
  goodsName: '',
  categoryId: undefined,
  price: undefined,
  stockNum: 0,
  status: 0,
  mainImg: '',
  description: '',
  warnStock: 10
})

const rules: FormRules = {
  goodsName: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  spuCode: [{ required: true, message: '请输入 SPU 编码', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择商品分类', trigger: 'change' }]
}

const leafCategories = computed(() => {
  const parentIds = new Set(store.categories.map((item) => item.parentId))
  return store.categories.filter((item) => !parentIds.has(item.id))
})

onMounted(async () => {
  await Promise.all([store.loadCategories(), store.refresh()])
})

function syncDateRange() {
  store.query.startDate = dateRange.value?.[0]
  store.query.endDate = dateRange.value?.[1]
}

function handleSearch() {
  syncDateRange()
  store.query.page = 1
  store.refresh()
}

function handleReset() {
  dateRange.value = null
  store.resetQuery()
  store.refresh()
}

function focusKeyword() {
  keywordInput.value?.focus()
}

function handleQuickTag(tag: string) {
  if (tag === '关键词搜索') {
    focusKeyword()
  }
  if (tag === '库存状态') {
    store.query.stockStatus = 'warning'
    handleSearch()
  }
  if (tag === '上下架') {
    store.query.status = 1
    handleSearch()
  }
}

function handleSelectionChange(rows: Goods[]) {
  selectedRows.value = rows
}

function resetForm() {
  Object.assign(form, {
    id: undefined,
    spuCode: '',
    goodsName: '',
    categoryId: undefined,
    price: undefined,
    stockNum: 0,
    status: 0,
    mainImg: '',
    description: '',
    warnStock: 10
  })
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

function openEdit(row: Goods) {
  Object.assign(form, {
    id: row.id,
    spuCode: row.spuCode,
    goodsName: row.goodsName,
    categoryId: row.categoryId,
    price: row.price,
    stockNum: row.stockNum,
    status: row.status,
    mainImg: row.mainImg,
    description: row.description,
    warnStock: row.warnStock ?? 10
  })
  formVisible.value = true
}

async function handleSave() {
  await formRef.value?.validate()
  if (form.id) {
    await updateGoods(form.id, form)
    ElMessage.success('商品已更新')
  } else {
    await createGoods(form)
    ElMessage.success('商品已新增，状态为待审核')
  }
  formVisible.value = false
  await store.refresh()
}

function statusName(status: number) {
  return status === 1 ? '已上架' : status === 2 ? '已下架' : '待审核'
}

function statusTagType(status: number) {
  return status === 1 ? 'success' : status === 2 ? 'info' : 'warning'
}

function statusActionText(status: number) {
  if (status === 1) return '下架'
  if (status === 2) return '重新提交审核'
  return '审核通过'
}

function nextStatus(status: number) {
  if (status === 1) return 2
  if (status === 2) return 0
  return 1
}

function isWarning(row: Goods) {
  return row.stockNum <= (row.warnStock ?? 10)
}

function formatDate(value?: string) {
  return value ? value.slice(0, 10) : '-'
}

async function handleRowCommand(command: string, row: Goods) {
  if (command === 'edit') {
    openEdit(row)
  }
  if (command === 'status') {
    await updateGoodsStatus(row.id, nextStatus(row.status))
    ElMessage.success('状态已更新')
    await store.refresh()
  }
  if (command === 'stock') {
    currentGoods.value = row
    stockValue.value = row.stockNum
    isBatchStock.value = false
    stockVisible.value = true
  }
  if (command === 'delete') {
    const message = row.status === 1 ? '该商品已上架，删除后商城将不可见，确认继续？' : '确认删除该商品？'
    await ElMessageBox.confirm(message, '删除确认', { type: 'warning' })
    await deleteGoods(row.id)
    ElMessage.success('商品已删除')
    await store.refresh()
  }
}

function openBatchEdit() {
  ElMessage.info('批量编辑可在此扩展更多字段，本版本已支持批量库存和状态处理')
}

function openBatchStock() {
  currentGoods.value = null
  stockValue.value = 0
  isBatchStock.value = true
  stockVisible.value = true
}

async function handleSaveStock() {
  if (isBatchStock.value) {
    await updateBatchStock(selectedRows.value.map((item) => item.id), stockValue.value)
    ElMessage.success('批量库存已更新')
  } else if (currentGoods.value) {
    await updateGoodsStock(currentGoods.value.id, stockValue.value)
    ElMessage.success('库存已更新')
  }
  stockVisible.value = false
  await store.refresh()
}

async function handleBatchOffSale() {
  await ElMessageBox.confirm('确认将选中商品批量下架？', '批量下架', { type: 'warning' })
  await updateBatchStatus(selectedRows.value.map((item) => item.id), 2)
  ElMessage.success('已批量下架')
  await store.refresh()
}

async function handleBatchDelete() {
  await ElMessageBox.confirm('确认删除选中的商品？该操作会进行逻辑删除。', '批量删除', { type: 'warning' })
  await deleteBatchGoods(selectedRows.value.map((item) => item.id))
  ElMessage.success('已批量删除')
  await store.refresh()
}

async function handleExport() {
  syncDateRange()
  await downloadFile('/goods/export', '商品数据.xlsx', store.query)
}

async function handleFileChange(uploadFile: UploadFile) {
  if (!uploadFile.raw) return
  importResult.value = await importGoods(uploadFile.raw)
  await store.refresh()
}
</script>

