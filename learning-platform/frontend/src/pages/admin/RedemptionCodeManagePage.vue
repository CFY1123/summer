<template>
  <section class="admin-redemption-page">
    <div class="admin-page-hero redemption-code-hero">
      <div>
        <h2>鍏戞崲鐮佺鐞?/h2>
      </div>
      <el-button type="primary" round :loading="exporting" @click="exportCodes">瀵煎嚭鍏戞崲鐮?/el-button>
    </div>

    <el-card shadow="never" class="admin-filter-card redemption-generate-card">
      <el-form :model="generateForm" label-position="top" class="redemption-generate-form">
        <el-form-item label="鍏戞崲鐮佺被鍨?>
          <el-select v-model="generateForm.codeType" size="large" placeholder="璇烽€夋嫨鍏戞崲鐮佺被鍨?>
            <el-option v-for="item in codeTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="鐢熸垚鏁伴噺">
          <el-input-number v-model="generateForm.quantity" :min="1" :max="500" :step="1" size="large" />
        </el-form-item>
        <el-form-item class="admin-filter-actions">
          <el-button type="primary" round size="large" :loading="generating" @click="generateCodes">鐢熸垚鍏戞崲鐮?/el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="admin-filter-card">
      <el-form :model="filters" label-position="top" class="redemption-filter-form">
        <el-form-item label="鍏抽敭璇?>
          <el-input v-model="filters.keyword" clearable placeholder="鎼滅储鍏戞崲鐮佹垨浣跨敤鐢ㄦ埛" @keyup.enter="searchCodes" />
        </el-form-item>
        <el-form-item label="绫诲瀷">
          <el-select v-model="filters.codeType" clearable placeholder="鍏ㄩ儴绫诲瀷">
            <el-option v-for="item in codeTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="鐘舵€?>
          <el-select v-model="filters.status" clearable placeholder="鍏ㄩ儴鐘舵€?>
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item class="admin-filter-actions">
          <el-button type="primary" round :loading="loading" @click="searchCodes">鏌ヨ</el-button>
          <el-button round @click="resetFilters">閲嶇疆</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="admin-table-card">
      <el-table v-loading="loading" :data="codes" row-key="id" aria-label="鍏戞崲鐮佺鐞嗗垪琛?>
        <el-table-column prop="code" label="鍏戞崲鐮? min-width="210" />
        <el-table-column prop="codeTypeText" label="绫诲瀷" min-width="170" />
        <el-table-column label="鐘舵€? width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'UNUSED' ? 'success' : 'info'" round>{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="浣跨敤鐢ㄦ埛" min-width="140">
          <template #default="{ row }">{{ row.usedByUsername || '-' }}</template>
        </el-table-column>
        <el-table-column label="浣跨敤鏃堕棿" width="180">
          <template #default="{ row }">{{ formatTime(row.usedAt) }}</template>
        </el-table-column>
        <el-table-column label="鍒涘缓鏃堕棿" width="180">
          <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-action-row">
              <el-button text type="primary" :disabled="!row.editable" @click="openEditDialog(row as AdminRedemptionCode)">缂栬緫</el-button>
              <el-button text type="danger" :disabled="!row.deletable" @click="deleteCode(row as AdminRedemptionCode)">鍒犻櫎</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page.pageNo"
        layout="prev, pager, next, total"
        :total="page.total"
        :page-size="page.pageSize"
        aria-label="鍏戞崲鐮佺鐞嗗垎椤?
        @current-change="loadCodes"
      />
    </el-card>

    <el-dialog v-model="editDialogVisible" title="缂栬緫鍏戞崲鐮? width="480px" class="redemption-code-dialog">
      <el-form :model="editForm" label-position="top">
        <el-form-item label="鍏戞崲鐮佺被鍨?>
          <el-select v-model="editForm.codeType" placeholder="璇烽€夋嫨鍏戞崲鐮佺被鍨?>
            <el-option v-for="item in codeTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">鍙栨秷</el-button>
        <el-button type="primary" :loading="saving" @click="saveEdit">淇濆瓨</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { ElCard } from 'element-plus/es/components/card/index.mjs';
import { ElInputNumber } from 'element-plus/es/components/input-number/index.mjs';
import { ElMessage } from 'element-plus/es/components/message/index.mjs';
import { ElMessageBox } from 'element-plus/es/components/message-box/index.mjs';
import { ElPagination } from 'element-plus/es/components/pagination/index.mjs';
import { ElOption, ElSelect } from 'element-plus/es/components/select/index.mjs';
import { ElTable, ElTableColumn } from 'element-plus/es/components/table/index.mjs';
import { ElTag } from 'element-plus/es/components/tag/index.mjs';
import 'element-plus/es/components/card/style/css';
import 'element-plus/es/components/input-number/style/css';
import 'element-plus/es/components/pagination/style/css';
import 'element-plus/es/components/select/style/css';
import 'element-plus/es/components/table/style/css';
import 'element-plus/es/components/tag/style/css';
import { onMounted, reactive, ref } from 'vue';
import {
  deleteAdminRedemptionCode,
  exportAdminRedemptionCodes,
  fetchAdminRedemptionCodes,
  generateAdminRedemptionCodes,
  updateAdminRedemptionCode,
  type AdminRedemptionCode,
  type RedemptionCodeStatus,
  type RedemptionCodeType,
} from '../../api/adminRedemptionCodes';
import { formatMediumDateTime as formatTime } from '../../utils/dateTimeFormat';
import { downloadBlobFile } from '../../utils/downloadFile';
import { resolveErrorMessage } from '../../utils/errorMessage';

const PAGE_SIZE = 10;
const loading = ref(false);
const generating = ref(false);
const saving = ref(false);
const exporting = ref(false);
const editDialogVisible = ref(false);
const editingId = ref<string | null>(null);
const codes = ref<AdminRedemptionCode[]>([]);
const page = reactive({ pageNo: 1, pageSize: PAGE_SIZE, total: 0 });
const filters = reactive<{ keyword: string; codeType: RedemptionCodeType | ''; status: RedemptionCodeStatus | '' }>({
  keyword: '',
  codeType: '',
  status: '',
});
const generateForm = reactive<{ codeType: RedemptionCodeType; quantity: number }>({
  codeType: 'PRO_MONTHLY',
  quantity: 10,
});
const editForm = reactive<{ codeType: RedemptionCodeType }>({ codeType: 'PRO_MONTHLY' });
const codeTypeOptions: Array<{ label: string; value: RedemptionCodeType }> = [
  { label: '楂樼骇妯″瀷涓€涓湀', value: 'PRO_MONTHLY' },
  { label: '瓒呯骇妯″瀷涓€涓湀', value: 'SUPER_MONTHLY' },
  { label: '楂樼骇妯″瀷姘镐箙', value: 'PRO_PERMANENT' },
  { label: '瓒呯骇妯″瀷姘镐箙', value: 'SUPER_PERMANENT' },
  { label: '楂樼骇妯″瀷姘镐箙鍗囪秴', value: 'PRO_PERMANENT_TO_SUPER' },
];
const statusOptions: Array<{ label: string; value: RedemptionCodeStatus }> = [
  { label: '鏈娇鐢?, value: 'UNUSED' },
  { label: '宸蹭娇鐢?, value: 'USED' },
];

/**
 * 鍔犺浇鍏戞崲鐮佸垪琛ㄣ€? */
async function loadCodes(): Promise<void> {
  loading.value = true;
  try {
    const result = await fetchAdminRedemptionCodes({ pageNo: page.pageNo, pageSize: page.pageSize, ...filters });
    codes.value = result.records;
    page.total = result.total;
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '鍏戞崲鐮佸姞杞藉け璐?));
  } finally {
    loading.value = false;
  }
}

/**
 * 鏌ヨ鍏戞崲鐮併€? */
async function searchCodes(): Promise<void> {
  page.pageNo = 1;
  await loadCodes();
}

/**
 * 閲嶇疆绛涢€夋潯浠躲€? */
async function resetFilters(): Promise<void> {
  filters.keyword = '';
  filters.codeType = '';
  filters.status = '';
  await searchCodes();
}

/**
 * 鎵归噺鐢熸垚鍏戞崲鐮併€? */
async function generateCodes(): Promise<void> {
  generating.value = true;
  try {
    const generatedCodes = await generateAdminRedemptionCodes(generateForm.codeType, generateForm.quantity);
    ElMessage.success(`宸茬敓鎴?${generatedCodes.length} 涓厬鎹㈢爜`);
    await searchCodes();
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '鐢熸垚澶辫触'));
  } finally {
    generating.value = false;
  }
}

/**
 * 鎵撳紑缂栬緫寮圭獥銆? */
function openEditDialog(row: AdminRedemptionCode): void {
  editingId.value = row.id;
  editForm.codeType = row.codeType;
  editDialogVisible.value = true;
}

/**
 * 淇濆瓨鍏戞崲鐮佺被鍨嬨€? */
async function saveEdit(): Promise<void> {
  if (!editingId.value) {
    return;
  }
  saving.value = true;
  try {
    await updateAdminRedemptionCode(editingId.value, editForm.codeType);
    editDialogVisible.value = false;
    ElMessage.success('鍏戞崲鐮佸凡鏇存柊');
    await loadCodes();
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '淇濆瓨澶辫触'));
  } finally {
    saving.value = false;
  }
}

/**
 * 鍒犻櫎鍏戞崲鐮併€? */
async function deleteCode(row: AdminRedemptionCode): Promise<void> {
  await ElMessageBox.confirm(`纭鍒犻櫎鍏戞崲鐮併€?{row.code}銆嶅悧锛焋, '鍒犻櫎纭', { type: 'warning' });
  await deleteAdminRedemptionCode(row.id);
  ElMessage.success('鍏戞崲鐮佸凡鍒犻櫎');
  await loadCodes();
}

/**
 * 瀵煎嚭鍏戞崲鐮併€? */
async function exportCodes(): Promise<void> {
  exporting.value = true;
  try {
    const blob = await exportAdminRedemptionCodes({ pageNo: page.pageNo, pageSize: page.pageSize, ...filters });
    downloadBlobFile(blob, '妯″瀷鏉冪泭鍏戞崲鐮?csv');
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '瀵煎嚭澶辫触'));
  } finally {
    exporting.value = false;
  }
}

onMounted(loadCodes);
</script>

