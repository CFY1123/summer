<template>
  <section class="admin-user-page">
    <div class="admin-page-hero user-manage-hero">
      <div>
        <h2>鐢ㄦ埛绠＄悊</h2>
        <p>缁熶竴缁存姢骞冲彴璐﹀彿銆佽秴绾х鐞嗗憳鏉冮檺鍜岀郴缁熺敤鎴峰閲忎笂闄愩€?/p>
      </div>
      <el-button type="primary" round @click="openCreateDialog">鏂板鐢ㄦ埛</el-button>
    </div>

    <el-card shadow="never" class="user-limit-card">
      <div class="user-limit-copy">
        <span>鏈€澶х敤鎴锋暟闄愬埗</span>
        <strong>{{ limitInfo.currentUsers }} / {{ limitInfo.maxUsers }}</strong>
        <small>杈惧埌涓婇檺鍚庯紝娉ㄥ唽椤靛皢鎻愮ず鐢ㄦ埛绛夊緟绠＄悊鍛樺崌绾ф湇鍔″櫒骞舵墿瀹广€?/small>
      </div>
      <div class="user-limit-action">
        <el-input-number
          v-model="limitForm.maxUsers"
          :min="USER_LIMIT_MIN_USERS"
          :max="USER_LIMIT_MAX_USERS"
          :step="USER_LIMIT_STEP"
        />
        <el-button type="primary" round :loading="savingLimit" @click="saveUserLimit">淇濆瓨闄愬埗</el-button>
      </div>
    </el-card>

    <el-card shadow="never" class="admin-filter-card">
      <el-form :model="filters" label-position="top" class="admin-user-filter-form">
        <el-form-item label="鍏抽敭璇?>
          <el-input v-model="filters.keyword" clearable aria-label="鐢ㄦ埛鍏抽敭璇? placeholder="鎼滅储鐢ㄦ埛鍚嶃€佹樀绉版垨閭" @keyup.enter="searchUsers" />
        </el-form-item>
        <el-form-item class="admin-filter-actions">
          <el-button type="primary" round :loading="loading" @click="searchUsers">鏌ヨ</el-button>
          <el-button round @click="resetFilters">閲嶇疆</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="admin-table-card">
      <el-table v-loading="loading" :data="users" row-key="id" aria-label="鐢ㄦ埛绠＄悊鍒楄〃">
        <el-table-column label="鐢ㄦ埛" min-width="220">
          <template #default="{ row }">
            <div class="admin-user-cell">
              <el-avatar :size="34" :src="row.avatar || undefined">{{ avatarText(row as AdminUserItem) }}</el-avatar>
              <div>
                <strong>{{ row.nickname }}</strong>
                <span>@{{ row.username }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="閭" min-width="220" />
        <el-table-column label="瑙掕壊" width="130">
          <template #default="{ row }">
            <el-tag :type="row.superAdmin ? 'success' : 'info'" round>
              {{ row.superAdmin ? '瓒呯骇绠＄悊鍛? : '鏅€氱敤鎴? }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="experience" label="缁忛獙" width="100" />
        <el-table-column label="娉ㄥ唽鏃堕棿" width="180">
          <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-action-row">
              <el-button text type="primary" :aria-label="`缂栬緫鐢ㄦ埛 ${row.username}`" @click="openEditDialog(row as AdminUserItem)">缂栬緫</el-button>
              <el-button text type="danger" :aria-label="`鍒犻櫎鐢ㄦ埛 ${row.username}`" @click="handleDelete(row as AdminUserItem)">鍒犻櫎</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page.pageNo"
        layout="prev, pager, next, total"
        :total="page.total"
        :page-size="page.pageSize"
        aria-label="鐢ㄦ埛绠＄悊鍒嗛〉"
        @current-change="loadUsers"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '缂栬緫鐢ㄦ埛' : '鏂板鐢ㄦ埛'" width="620px" class="admin-user-dialog">
      <el-form :model="form" label-position="top">
        <div class="dialog-grid">
          <el-form-item label="鐢ㄦ埛鍚?>
            <el-input
              v-model.trim="form.username"
              :maxlength="USER_PROFILE_LIMITS.usernameMaxLength"
              placeholder="3-32浣嶅瓧姣嶃€佹暟瀛椼€佷笅鍒掔嚎"
            />
          </el-form-item>
          <el-form-item :label="editingId ? '鏂板瘑鐮侊紙鍙┖锛? : '瀵嗙爜'">
            <el-input
              v-model="form.password"
              type="password"
              :maxlength="USER_PROFILE_LIMITS.passwordMaxLength"
              show-password
              placeholder="8-64浣嶅瘑鐮?
            />
          </el-form-item>
        </div>
        <div class="dialog-grid">
          <el-form-item label="鏄电О">
            <el-input
              v-model.trim="form.nickname"
              :maxlength="USER_PROFILE_LIMITS.nicknameMaxLength"
              placeholder="璇疯緭鍏ユ樀绉?
            />
          </el-form-item>
          <el-form-item label="閭">
            <el-input
              v-model.trim="form.email"
              :maxlength="USER_PROFILE_LIMITS.emailMaxLength"
              placeholder="demo@example.com"
            />
          </el-form-item>
        </div>
        <el-form-item label="澶村儚鍦板潃锛堝彲绌猴級">
          <el-input v-model.trim="form.avatar" maxlength="255" placeholder="浣跨敤 HTTPS 鍥剧墖鍦板潃锛岀暀绌哄垯灞曠ず鏂囧瓧澶村儚" />
        </el-form-item>
        <el-form-item label="鏉冮檺">
          <el-switch v-model="form.superAdmin" active-text="瓒呯骇绠＄悊鍛? inactive-text="鏅€氱敤鎴? />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">鍙栨秷</el-button>
        <el-button type="primary" :loading="saving" @click="saveUser">淇濆瓨</el-button>
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
import { ElSwitch } from 'element-plus/es/components/switch/index.mjs';
import { ElTable, ElTableColumn } from 'element-plus/es/components/table/index.mjs';
import { ElTag } from 'element-plus/es/components/tag/index.mjs';
import 'element-plus/es/components/card/style/css';
import 'element-plus/es/components/input-number/style/css';
import 'element-plus/es/components/pagination/style/css';
import 'element-plus/es/components/switch/style/css';
import 'element-plus/es/components/table/style/css';
import 'element-plus/es/components/tag/style/css';
import { onMounted, reactive, ref } from 'vue';
import {
  createAdminUser,
  deleteAdminUser,
  fetchAdminUsers,
  fetchUserLimit,
  updateAdminUser,
  updateUserLimit,
} from '../../api/adminUsers';
import type { AdminUserItem, AdminUserPayload, UserLimitInfo } from '../../types/admin-user';
import { formatMediumDateTime as formatTime } from '../../utils/dateTimeFormat';
import { resolveErrorMessage } from '../../utils/errorMessage';
import { resolveUserAvatarText } from '../../utils/userDisplay';
import {
  isValidEmail,
  isValidNickname,
  isValidPasswordLength,
  isValidUsername,
  USER_PROFILE_LIMITS,
  USER_PROFILE_MESSAGES,
} from '../../utils/userProfileValidation';

const PAGE_SIZE = 10;
const USER_LIMIT_MIN_USERS = 1;
const USER_LIMIT_MAX_USERS = 1_000_000;
const USER_LIMIT_STEP = 10;
const USER_LIMIT_DEFAULT_MAX_USERS = 10_000;
const loading = ref(false);
const saving = ref(false);
const savingLimit = ref(false);
const dialogVisible = ref(false);
const editingId = ref<string | null>(null);
const users = ref<AdminUserItem[]>([]);
const page = reactive({ pageNo: 1, pageSize: PAGE_SIZE, total: 0 });
const filters = reactive({ keyword: '' });
const limitInfo = reactive<UserLimitInfo>({ maxUsers: USER_LIMIT_DEFAULT_MAX_USERS, currentUsers: 0 });
const limitForm = reactive({ maxUsers: USER_LIMIT_DEFAULT_MAX_USERS });
const form = reactive<AdminUserPayload>(buildEmptyForm());

/**
 * 鏋勫缓绌虹敤鎴疯〃鍗曘€? */
function buildEmptyForm(): AdminUserPayload {
  return { username: '', password: '', nickname: '', email: '', avatar: '', superAdmin: false };
}

/**
 * 鍔犺浇鐢ㄦ埛瀹归噺闄愬埗銆? */
async function loadUserLimit(): Promise<void> {
  const result = await fetchUserLimit();
  Object.assign(limitInfo, result);
  limitForm.maxUsers = result.maxUsers;
}

/**
 * 淇濆瓨鐢ㄦ埛瀹归噺闄愬埗銆? */
async function saveUserLimit(): Promise<void> {
  savingLimit.value = true;
  try {
    const result = await updateUserLimit(limitForm.maxUsers);
    Object.assign(limitInfo, result);
    ElMessage.success('鏈€澶х敤鎴锋暟闄愬埗宸蹭繚瀛?);
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '淇濆瓨闄愬埗澶辫触'));
  } finally {
    savingLimit.value = false;
  }
}

/**
 * 鍔犺浇鐢ㄦ埛鍒楄〃銆? */
async function loadUsers(): Promise<void> {
  loading.value = true;
  try {
    const result = await fetchAdminUsers({ pageNo: page.pageNo, pageSize: page.pageSize, ...filters });
    users.value = result.records;
    page.total = result.total;
  } finally {
    loading.value = false;
  }
}

/**
 * 鎸夋潯浠舵煡璇㈢敤鎴枫€? */
async function searchUsers(): Promise<void> {
  page.pageNo = 1;
  await loadUsers();
}

/**
 * 閲嶇疆绛涢€夋潯浠躲€? */
async function resetFilters(): Promise<void> {
  filters.keyword = '';
  await searchUsers();
}

/**
 * 鎵撳紑鏂板寮圭獥銆? */
function openCreateDialog(): void {
  editingId.value = null;
  Object.assign(form, buildEmptyForm());
  dialogVisible.value = true;
}

/**
 * 鎵撳紑缂栬緫寮圭獥銆? */
function openEditDialog(row: AdminUserItem): void {
  editingId.value = row.id;
  Object.assign(form, {
    username: row.username,
    password: '',
    nickname: row.nickname,
    email: row.email,
    avatar: row.avatar || '',
    superAdmin: row.superAdmin,
  });
  dialogVisible.value = true;
}

/**
 * 淇濆瓨鐢ㄦ埛銆? */
async function saveUser(): Promise<void> {
  if (!validateUserForm()) {
    return;
  }
  saving.value = true;
  try {
    const payload = normalizePayload();
    if (editingId.value) {
      await updateAdminUser(editingId.value, payload);
      ElMessage.success('鐢ㄦ埛宸叉洿鏂?);
    } else {
      await createAdminUser(payload);
      ElMessage.success('鐢ㄦ埛宸叉柊澧?);
    }
    dialogVisible.value = false;
    await Promise.all([loadUsers(), loadUserLimit()]);
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, '淇濆瓨鐢ㄦ埛澶辫触'));
  } finally {
    saving.value = false;
  }
}

/**
 * 鍒犻櫎鐢ㄦ埛銆? */
async function handleDelete(row: AdminUserItem): Promise<void> {
  await ElMessageBox.confirm(`纭鍒犻櫎鐢ㄦ埛銆?{row.username}銆嶅悧锛焋, '鍒犻櫎纭', { type: 'warning' });
  await deleteAdminUser(row.id);
  ElMessage.success('鐢ㄦ埛宸插垹闄?);
  await Promise.all([loadUsers(), loadUserLimit()]);
}

/**
 * 鏍￠獙鐢ㄦ埛琛ㄥ崟銆? */
function validateUserForm(): boolean {
  if (!isValidUsername(form.username)) {
    ElMessage.warning(USER_PROFILE_MESSAGES.usernameInvalid);
    return false;
  }
  if (!editingId.value && (!form.password || form.password.length < USER_PROFILE_LIMITS.passwordMinLength)) {
    ElMessage.warning(USER_PROFILE_MESSAGES.createPasswordInvalid);
    return false;
  }
  if (form.password && !isValidPasswordLength(form.password)) {
    ElMessage.warning(USER_PROFILE_MESSAGES.passwordInvalid);
    return false;
  }
  if (!isValidNickname(form.nickname)) {
    ElMessage.warning(USER_PROFILE_MESSAGES.nicknameInvalid);
    return false;
  }
  if (!isValidEmail(form.email)) {
    ElMessage.warning(USER_PROFILE_MESSAGES.emailInvalid);
    return false;
  }
  return true;
}

/**
 * 瑙勬暣淇濆瓨杞借嵎銆? */
function normalizePayload(): AdminUserPayload {
  return {
    username: form.username.trim(),
    password: form.password?.trim() || undefined,
    nickname: form.nickname.trim(),
    email: form.email.trim(),
    avatar: form.avatar?.trim() || null,
    superAdmin: form.superAdmin,
  };
}

/**
 * 鐢熸垚澶村儚榛樿鏂囧瓧銆? */
function avatarText(row: AdminUserItem): string {
  return resolveUserAvatarText(row);
}

onMounted(async () => {
  await Promise.all([loadUsers(), loadUserLimit()]);
});
</script>

