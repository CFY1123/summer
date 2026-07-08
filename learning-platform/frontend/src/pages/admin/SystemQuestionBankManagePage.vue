<template>
  <section class="system-question-bank-page">
    <div class="admin-page-hero system-question-hero">
      <div>
        <h2>绯荤粺棰樺簱绠＄悊</h2>
      </div>
      <div class="system-question-actions">
        <el-button round type="danger" plain :loading="clearing" aria-label="涓€閿竻闄ゅ綋鍓嶉搴? @click="handleClearAll">涓€閿竻闄ゅ綋鍓嶉搴?/el-button>
        <el-button round @click="downloadTemplate">涓嬭浇CSV妯℃澘</el-button>
        <el-upload :show-file-list="false" accept=".csv,text/csv" :before-upload="handleImportFile">
          <el-button round :loading="prechecking" aria-label="涓婁紶CSV骞堕妫€棰樺簱瀵煎叆鍐呭">涓婁紶CSV棰勬</el-button>
        </el-upload>
        <el-button type="primary" round @click="openCreateDialog">鏂板棰樼洰</el-button>
      </div>
    </div>

    <el-card shadow="never" class="admin-filter-card">
      <el-form :model="filters" label-position="top" class="admin-filter-form">
        <el-form-item label="鍏抽敭璇?>
          <el-input v-model="filters.keyword" clearable aria-label="棰樺簱鍏抽敭璇? placeholder="鎼滅储缂栫爜銆侀鐩垨绛旀" @keyup.enter="searchQuestions" />
        </el-form-item>
        <el-form-item label="鍒嗙被">
          <el-select v-model="filters.questionType" clearable filterable allow-create aria-label="棰樼洰鍒嗙被绛涢€? placeholder="鍏ㄩ儴鍒嗙被">
            <el-option v-for="item in questionTypes" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item class="admin-filter-actions">
          <el-button type="primary" round :loading="loading" @click="searchQuestions">鏌ヨ</el-button>
          <el-button round @click="resetFilters">閲嶇疆</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="admin-table-card">
      <el-table v-loading="loading" :data="questions" row-key="id" class="system-question-table" aria-label="绯荤粺棰樺簱鍒楄〃">
        <el-table-column prop="code" label="棰樼洰缂栫爜" width="180" />
        <el-table-column prop="questionType" label="鍒嗙被" width="130" />
        <el-table-column label="棰樼洰" min-width="320">
          <template #default="{ row }">
            <p class="question-cell">{{ row.question }}</p>
          </template>
        </el-table-column>
        <el-table-column prop="importanceScore" label="閲嶈鎬? width="100" />
        <el-table-column prop="occurrenceCount" label="鐪熷疄闈㈣瘯鍑虹幇娆℃暟" width="150" />
        <el-table-column label="鏇存柊鏃堕棿" width="180">
          <template #default="{ row }">{{ formatTime(row.updatedAt) }}</template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-action-row">
              <el-button text type="primary" :aria-label="`缂栬緫棰樼洰 ${row.code}`" @click="openEditDialog(row as SystemQuestionItem)">缂栬緫</el-button>
              <el-button text type="danger" :aria-label="`鍒犻櫎棰樼洰 ${row.code}`" @click="handleDelete(row as SystemQuestionItem)">鍒犻櫎</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page.pageNo"
        layout="prev, pager, next, total"
        :total="page.total"
        :page-size="page.pageSize"
        aria-label="绯荤粺棰樺簱鍒嗛〉"
        @current-change="loadQuestions"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '缂栬緫绯荤粺棰樼洰' : '鏂板绯荤粺棰樼洰'" width="760px" class="system-question-dialog">
      <el-form :model="form" label-position="top">
        <div class="dialog-grid">
          <el-form-item label="棰樼洰缂栫爜锛堝彲绌猴紝绌哄垯鑷姩鐢熸垚锛?>
            <el-input
              v-model="form.code"
              aria-label="棰樼洰缂栫爜"
              :maxlength="QUESTION_CODE_MAX_LENGTH"
              placeholder="渚嬪 SYSTEM-RAG-001"
            />
          </el-form-item>
          <el-form-item label="棰樼洰鍒嗙被">
            <el-select v-model="form.questionType" filterable allow-create default-first-option aria-label="棰樼洰鍒嗙被" placeholder="渚嬪 RAG">
              <el-option v-for="item in questionTypes" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="棰樼洰">
          <el-input
            v-model="form.question"
            aria-label="棰樼洰鍐呭"
            type="textarea"
            :rows="5"
            :maxlength="QUESTION_LONG_TEXT_MAX_LENGTH"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="鍙傝€冪瓟妗?>
          <el-input
            v-model="form.standardAnswer"
            aria-label="鍙傝€冪瓟妗?
            type="textarea"
            :rows="5"
            :maxlength="QUESTION_LONG_TEXT_MAX_LENGTH"
            show-word-limit
          />
        </el-form-item>
        <div class="dialog-grid">
          <el-form-item label="閲嶈鎬ц瘎鍒嗭紙0-100锛?>
            <el-input-number v-model="form.importanceScore" aria-label="閲嶈鎬ц瘎鍒? :min="0" :max="100" :step="0.1" :precision="1" />
          </el-form-item>
          <el-form-item label="鐪熷疄闈㈣瘯鍑虹幇娆℃暟">
            <el-input-number v-model="form.occurrenceCount" aria-label="鐪熷疄闈㈣瘯鍑虹幇娆℃暟" :min="0" />
          </el-form-item>
        </div>
        <p v-if="formError" class="admin-form-error" role="alert">{{ formError }}</p>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">鍙栨秷</el-button>
        <el-button type="primary" :loading="saving" @click="saveQuestion">淇濆瓨</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importPreviewVisible" title="CSV瀵煎叆棰勬" width="1080px" class="system-question-import-dialog">
      <div v-if="importPreview" class="import-preview-panel">
        <div class="import-summary-grid" aria-label="CSV瀵煎叆棰勬姹囨€?>
          <div class="import-summary-item">
            <span>CSV琛屾暟</span>
            <strong>{{ importPreview.totalCount }}</strong>
          </div>
          <div class="import-summary-item is-create">
            <span>鏂板</span>
            <strong>{{ importPreview.createdCount }}</strong>
          </div>
          <div class="import-summary-item is-update">
            <span>鏇存柊</span>
            <strong>{{ importPreview.updatedCount }}</strong>
          </div>
          <div class="import-summary-item is-warning">
            <span>鍐茬獊</span>
            <strong>{{ importPreview.conflictCount }}</strong>
          </div>
          <div class="import-summary-item is-danger">
            <span>閿欒</span>
            <strong>{{ importPreview.errorCount }}</strong>
          </div>
        </div>

        <el-alert
          v-if="importPreview.issues.length"
          type="warning"
          :closable="false"
          show-icon
          title="瀛樺湪鏃犳硶瀵煎叆鐨勮锛岀‘璁ゅ鍏ユ椂浼氳烦杩囧啿绐佸拰閿欒琛屻€?
        />

        <el-table :data="importPreview.rows" max-height="460" row-key="rowIndex" class="import-preview-table" aria-label="CSV瀵煎叆棰勬鏄庣粏">
          <el-table-column prop="rowIndex" label="琛屽彿" width="76" />
          <el-table-column label="鍔ㄤ綔" width="92">
            <template #default="{ row }">
              <el-tag :type="resolveActionTagType(row.action)" effect="light">{{ row.actionText }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="code" label="棰樼洰缂栫爜" min-width="170" />
          <el-table-column prop="questionType" label="鍒嗙被" width="130" />
          <el-table-column label="棰樼洰" min-width="260">
            <template #default="{ row }">
              <p class="question-cell">{{ row.question }}</p>
            </template>
          </el-table-column>
          <el-table-column label="宸紓 / 瀛楁闂" min-width="280">
            <template #default="{ row }">
              <div class="import-row-detail">
                <template v-if="row.issues.length">
                  <el-tag v-for="issue in row.issues" :key="`${row.rowIndex}-${issue.fieldName}-${issue.message}`" type="danger" effect="plain">
                    {{ issue.fieldLabel }}锛歿{ issue.message }}
                  </el-tag>
                </template>
                <template v-else-if="row.diffs.length">
                  <el-tag v-for="diff in row.diffs" :key="`${row.rowIndex}-${diff.fieldName}`" type="info" effect="plain">
                    {{ diff.fieldLabel }}
                  </el-tag>
                </template>
                <span v-else class="import-row-muted">鏃犲瓧娈靛彉鍖?/span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="closeImportPreview">鍙栨秷</el-button>
        <el-button
          type="primary"
          :disabled="!canConfirmImport"
          :loading="importing"
          aria-label="纭瀵煎叆棰勬閫氳繃鐨凜SV琛?
          @click="confirmImportCsv"
        >
          纭瀵煎叆鍙鍏ヨ
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { ElAlert } from 'element-plus/es/components/alert/index.mjs';
import { ElCard } from 'element-plus/es/components/card/index.mjs';
import { ElInputNumber } from 'element-plus/es/components/input-number/index.mjs';
import { ElMessage } from 'element-plus/es/components/message/index.mjs';
import { ElMessageBox } from 'element-plus/es/components/message-box/index.mjs';
import { ElPagination } from 'element-plus/es/components/pagination/index.mjs';
import { ElOption, ElSelect } from 'element-plus/es/components/select/index.mjs';
import { ElTable, ElTableColumn } from 'element-plus/es/components/table/index.mjs';
import { ElTag } from 'element-plus/es/components/tag/index.mjs';
import { ElUpload } from 'element-plus/es/components/upload/index.mjs';
import 'element-plus/es/components/alert/style/css';
import 'element-plus/es/components/card/style/css';
import 'element-plus/es/components/input-number/style/css';
import 'element-plus/es/components/pagination/style/css';
import 'element-plus/es/components/select/style/css';
import 'element-plus/es/components/table/style/css';
import 'element-plus/es/components/tag/style/css';
import 'element-plus/es/components/upload/style/css';
import type { UploadRawFile } from 'element-plus/es/components/upload';
import { computed, onMounted, reactive, ref } from 'vue';
import {
  clearSystemQuestions,
  createSystemQuestion,
  deleteSystemQuestion,
  downloadSystemQuestionTemplate,
  fetchSystemQuestionTypes,
  fetchSystemQuestions,
  importSystemQuestions,
  precheckImportSystemQuestions,
  updateSystemQuestion,
} from '../../api/adminQuestions';
import { formatMediumDateTime as formatTime } from '../../utils/dateTimeFormat';
import { downloadBlobFile } from '../../utils/downloadFile';
import { resolveErrorMessage } from '../../utils/errorMessage';
import type {
  ImportSystemQuestionAction,
  ImportSystemQuestionsPrecheckResult,
  SystemQuestionItem,
  SystemQuestionPayload,
} from '../../types/system-question';

const PAGE_SIZE = 10;
const QUESTION_CODE_MAX_LENGTH = 64;
const QUESTION_LONG_TEXT_MAX_LENGTH = 10000;
const loading = ref(false);
const saving = ref(false);
const importing = ref(false);
const prechecking = ref(false);
const clearing = ref(false);
const dialogVisible = ref(false);
const importPreviewVisible = ref(false);
const editingId = ref<string | null>(null);
const importFile = ref<File | null>(null);
const importPreview = ref<ImportSystemQuestionsPrecheckResult | null>(null);
const questions = ref<SystemQuestionItem[]>([]);
const questionTypes = ref<string[]>([]);
const page = reactive({ pageNo: 1, pageSize: PAGE_SIZE, total: 0 });
const filters = reactive({ keyword: '', questionType: '' });
const form = reactive<SystemQuestionPayload>(buildEmptyForm());
const formError = ref('');
const canConfirmImport = computed(() => Boolean(importFile.value && importPreview.value?.importableCount));

/**
 * 鏋勫缓绌鸿〃鍗曘€? */
function buildEmptyForm(): SystemQuestionPayload {
  return { code: '', question: '', questionType: '', standardAnswer: '', importanceScore: 60, occurrenceCount: 0 };
}

/**
 * 鍔犺浇棰樼洰鍒嗙被銆? */
async function loadQuestionTypes(): Promise<void> {
  questionTypes.value = await fetchSystemQuestionTypes();
}

/**
 * 鍔犺浇绯荤粺棰樺簱銆? */
async function loadQuestions(): Promise<void> {
  loading.value = true;
  try {
    const result = await fetchSystemQuestions({ pageNo: page.pageNo, pageSize: page.pageSize, ...filters });
    questions.value = result.records;
    page.total = result.total;
  } finally {
    loading.value = false;
  }
}

/**
 * 鎸夋潯浠舵煡璇㈤搴撱€? */
async function searchQuestions(): Promise<void> {
  page.pageNo = 1;
  await loadQuestions();
}

/**
 * 閲嶇疆绛涢€夋潯浠躲€? */
async function resetFilters(): Promise<void> {
  filters.keyword = '';
  filters.questionType = '';
  await searchQuestions();
}

/**
 * 鎵撳紑鏂板寮圭獥銆? */
function openCreateDialog(): void {
  editingId.value = null;
  formError.value = '';
  Object.assign(form, buildEmptyForm());
  dialogVisible.value = true;
}

/**
 * 鎵撳紑缂栬緫寮圭獥銆? */
function openEditDialog(row: SystemQuestionItem): void {
  editingId.value = row.id;
  formError.value = '';
  Object.assign(form, {
    code: row.code,
    question: row.question,
    questionType: row.questionType,
    standardAnswer: row.standardAnswer,
    importanceScore: row.importanceScore,
    occurrenceCount: row.occurrenceCount,
  });
  dialogVisible.value = true;
}

/**
 * 淇濆瓨棰樼洰銆? */
async function saveQuestion(): Promise<void> {
  if (!form.question.trim() || !form.questionType.trim() || !form.standardAnswer.trim()) {
    formError.value = '璇峰～鍐欓鐩€佸垎绫诲拰鍙傝€冪瓟妗?;
    ElMessage.warning(formError.value);
    return;
  }
  saving.value = true;
  formError.value = '';
  try {
    const payload = { ...form, code: form.code?.trim() || undefined, questionType: form.questionType.trim() };
    if (editingId.value) {
      await updateSystemQuestion(editingId.value, payload);
      ElMessage.success('棰樼洰宸叉洿鏂?);
    } else {
      await createSystemQuestion(payload);
      ElMessage.success('棰樼洰宸叉柊澧?);
    }
    dialogVisible.value = false;
    await Promise.all([loadQuestionTypes(), loadQuestions()]);
  } catch (error) {
    formError.value = resolveErrorMessage(error, '淇濆瓨澶辫触');
    ElMessage.error(formError.value);
  } finally {
    saving.value = false;
  }
}

/**
 * 鍒犻櫎棰樼洰銆? */
async function handleDelete(row: SystemQuestionItem): Promise<void> {
  await ElMessageBox.confirm(`纭鍒犻櫎棰樼洰銆?{row.code}銆嶅悧锛焋, '鍒犻櫎纭', { type: 'warning' });
  await deleteSystemQuestion(row.id);
  ElMessage.success('棰樼洰宸插垹闄?);
  await loadQuestions();
}


/**
 * 涓€閿竻绌虹郴缁熼搴撱€? */
async function handleClearAll(): Promise<void> {
  await ElMessageBox.confirm('璇ユ搷浣滀細鐪熷疄娓呯┖褰撳墠棰樺簱鏁版嵁骞堕噸缃嚜澧濱D锛岀‘璁ょ户缁悧锛?, '娓呯┖棰樺簱纭', {
    type: 'warning',
    confirmButtonText: '纭娓呯┖',
    cancelButtonText: '鍙栨秷',
  });
  clearing.value = true;
  try {
    await clearSystemQuestions();
    ElMessage.success('褰撳墠棰樺簱宸叉竻绌?);
    await Promise.all([loadQuestionTypes(), searchQuestions()]);
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '娓呯┖棰樺簱澶辫触'));
  } finally {
    clearing.value = false;
  }
}

/**
 * 涓嬭浇 CSV 妯℃澘銆? */
async function downloadTemplate(): Promise<void> {
  const blob = await downloadSystemQuestionTemplate();
  downloadBlobFile(blob, '绯荤粺棰樺簱瀵煎叆妯℃澘.csv');
}

/**
 * 棰勬 CSV 鏂囦欢銆? */
async function handleImportFile(file: UploadRawFile): Promise<boolean> {
  prechecking.value = true;
  try {
    importFile.value = file;
    importPreview.value = await precheckImportSystemQuestions(file);
    importPreviewVisible.value = true;
    ElMessage.success('CSV棰勬瀹屾垚锛岃纭瀵煎叆鍐呭');
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '棰勬澶辫触'));
  } finally {
    prechecking.value = false;
  }
  return false;
}

/**
 * 鍏抽棴 CSV 瀵煎叆棰勬寮圭獥銆? */
function closeImportPreview(): void {
  importPreviewVisible.value = false;
  importPreview.value = null;
  importFile.value = null;
}

/**
 * 纭瀵煎叆棰勬閫氳繃鐨?CSV 鏂囦欢銆? */
async function confirmImportCsv(): Promise<void> {
  if (!importFile.value) {
    ElMessage.warning('璇峰厛涓婁紶CSV鏂囦欢');
    return;
  }
  importing.value = true;
  try {
    const result = await importSystemQuestions(importFile.value);
    if (result.skippedCount > 0) {
      ElMessage.warning(`瀵煎叆瀹屾垚锛氭柊澧?${result.createdCount} 閬擄紝鏇存柊 ${result.updatedCount} 閬擄紝璺宠繃 ${result.skippedCount} 琛宍);
      if (importPreview.value) {
        importPreview.value = { ...importPreview.value, importableCount: 0 };
      }
      importFile.value = null;
      await Promise.all([loadQuestionTypes(), searchQuestions()]);
      return;
    }
    ElMessage.success(`瀵煎叆鎴愬姛锛氭柊澧?${result.createdCount} 閬擄紝鏇存柊 ${result.updatedCount} 閬揱);
    closeImportPreview();
    await Promise.all([loadQuestionTypes(), searchQuestions()]);
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '瀵煎叆澶辫触'));
  } finally {
    importing.value = false;
  }
}

/**
 * 瑙ｆ瀽棰勬鍔ㄤ綔鏍囩绫诲瀷銆? */
function resolveActionTagType(action: ImportSystemQuestionAction): 'success' | 'primary' | 'warning' | 'danger' {
  if (action === 'CREATE') {
    return 'success';
  }
  if (action === 'UPDATE') {
    return 'primary';
  }
  if (action === 'CONFLICT') {
    return 'warning';
  }
  return 'danger';
}

onMounted(async () => {
  await Promise.all([loadQuestionTypes(), loadQuestions()]);
});
</script>


