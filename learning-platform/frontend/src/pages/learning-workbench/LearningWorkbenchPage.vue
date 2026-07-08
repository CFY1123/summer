<template>
  <section class="learning-workbench-page">
    <header class="workbench-header">
      <div>
        <p class="workbench-eyebrow">LangChain 学习闭环原型</p>
        <h2>学习工作台</h2>
      </div>
      <div class="workbench-score-grid" aria-label="功能覆盖">
        <span>知识库 15分</span>
        <span>章节学习 20分</span>
        <span>测验复盘 20分</span>
      </div>
    </header>

    <div class="workbench-grid">
      <section class="workbench-panel knowledge-panel">
        <div class="panel-title-row">
          <h3>知识库管理</h3>
          <el-button size="small" @click="loadKnowledgeBases">刷新</el-button>
        </div>

        <el-form label-position="top" class="compact-form">
          <el-form-item label="知识库名称">
            <el-input v-model.trim="newKb.name" maxlength="120" placeholder="例如：LangChain 课程资料" />
          </el-form-item>
          <el-form-item label="说明">
            <el-input v-model.trim="newKb.description" maxlength="500" placeholder="选填" />
          </el-form-item>
          <el-button type="primary" :loading="loading" @click="handleCreateKnowledgeBase">创建知识库</el-button>
        </el-form>

        <div class="kb-list">
          <button
            v-for="item in knowledgeBases"
            :key="item.id"
            type="button"
            :class="['kb-item', { 'is-active': item.id === selectedKbId }]"
            @click="selectKnowledgeBase(item.id)"
          >
            <strong>{{ item.name }}</strong>
            <span>{{ item.documentCount }} 个文档 / {{ item.chunkCount }} 个分块</span>
          </button>
        </div>

        <div v-if="selectedKb" class="danger-row">
          <span>当前：{{ selectedKb.name }}</span>
          <el-button size="small" type="danger" plain @click="handleDeleteKnowledgeBase">删除知识库</el-button>
        </div>
      </section>

      <section class="workbench-panel">
        <div class="panel-title-row">
          <h3>文档上传与检索</h3>
          <span class="panel-hint">PDF / DOCX / TXT</span>
        </div>

        <div class="upload-row">
          <input ref="fileInputRef" type="file" accept=".pdf,.docx,.txt" @change="handleFileChange" />
          <el-button :disabled="!selectedKbId" :loading="loading" @click="handleUploadDocument">上传并解析</el-button>
        </div>

        <el-table :data="documents" size="small" max-height="230">
          <el-table-column prop="filename" label="文件名" min-width="170" />
          <el-table-column prop="fileType" label="类型" width="70" />
          <el-table-column prop="parserStatus" label="状态" width="90" />
          <el-table-column prop="chunkCount" label="分块" width="70" />
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button size="small" text type="danger" @click="handleDeleteDocument(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="search-row">
          <el-input v-model.trim="searchKeyword" :disabled="!selectedKbId" placeholder="输入关键词检索知识库" />
          <el-button :disabled="!selectedKbId || !searchKeyword" @click="handleSearch">检索</el-button>
        </div>
        <div class="search-result-list">
          <p v-for="item in searchResults" :key="item.id">
            <strong>#{{ item.chunkIndex + 1 }}</strong>
            {{ item.preview }}
            <span v-if="item.score !== undefined">相似度 {{ item.score }}</span>
          </p>
        </div>
      </section>

      <section class="workbench-panel chapter-panel">
        <div class="panel-title-row">
          <h3>课程大纲与章节学习</h3>
          <el-button :disabled="!selectedKbId" :loading="loading" type="primary" plain @click="handleGenerateOutline">
            生成课程大纲
          </el-button>
        </div>

        <div class="progress-strip">
          <span>{{ progress.completed }} / {{ progress.total }} 章节完成</span>
          <el-progress :percentage="progress.percent" />
          <el-button :disabled="!selectedKbId" size="small" @click="handleResetProgress">重置进度</el-button>
        </div>

        <div class="chapter-layout">
          <div class="chapter-list">
            <button
              v-for="chapter in chapters"
              :key="chapter.id"
              type="button"
              :class="['chapter-item', { 'is-section': chapter.parentId, 'is-active': chapter.id === selectedChapterId }]"
              @click="selectChapter(chapter.id)"
            >
              {{ chapter.title }}
            </button>
          </div>

          <article class="chapter-content">
            <template v-if="chapterContent">
              <div class="chapter-content-header">
                <h4>{{ chapterContent.title }}</h4>
                <el-select v-model="selectedProgressStatus" size="small" @change="handleUpdateProgress">
                  <el-option label="未开始" value="not_started" />
                  <el-option label="学习中" value="learning" />
                  <el-option label="已完成" value="completed" />
                </el-select>
              </div>
              <section v-for="block in chapterContent.content" :key="block.title">
                <h5>{{ block.title }}</h5>
                <p>{{ block.text }}</p>
              </section>
            </template>
            <el-empty v-else description="先选择或生成一个章节" />
          </article>
        </div>
      </section>

      <section class="workbench-panel quiz-panel">
        <div class="panel-title-row">
          <h3>在线测验</h3>
          <div class="quiz-toolbar">
            <el-select v-model="questionDifficulty" size="small">
              <el-option label="简单" value="easy" />
              <el-option label="中等" value="medium" />
              <el-option label="困难" value="hard" />
            </el-select>
            <el-input-number v-model="questionCount" :min="5" :max="20" size="small" />
            <el-button :disabled="!selectedChapterId" :loading="loading" type="primary" @click="handleGenerateQuestions">
              自动出题
            </el-button>
          </div>
        </div>

        <div class="question-list">
          <div v-for="question in questions" :key="question.id" class="question-item">
            <p class="question-stem">{{ question.stem }}</p>
            <el-radio-group v-model="answerMap[question.id]">
              <el-radio v-for="option in question.options" :key="option" :label="option">{{ option }}</el-radio>
            </el-radio-group>
          </div>
        </div>
        <div class="submit-row">
          <el-button :disabled="questions.length === 0" type="primary" @click="handleSubmitQuiz">提交并批改</el-button>
          <span v-if="quizResult">得分 {{ quizResult.score }}，答对 {{ quizResult.correct }} / {{ quizResult.total }}</span>
        </div>
        <div v-if="quizResult" class="quiz-result-list">
          <p v-for="detail in quizResult.details" :key="detail.question.id">
            <el-tag :type="detail.isCorrect ? 'success' : 'danger'" size="small">
              {{ detail.isCorrect ? '正确' : '错误' }}
            </el-tag>
            正确答案：{{ detail.question.answer }}；解析：{{ detail.question.analysis }}
          </p>
        </div>
      </section>

      <section class="workbench-panel">
        <div class="panel-title-row">
          <h3>错题复盘</h3>
          <el-button size="small" @click="loadReviewData">刷新</el-button>
        </div>

        <div class="filter-row">
          <el-select v-model="wrongFilter.chapterId" clearable placeholder="按章节" size="small">
            <el-option v-for="chapter in chapters" :key="chapter.id" :label="chapter.title" :value="chapter.id" />
          </el-select>
          <el-select v-model="wrongFilter.difficulty" clearable placeholder="按难度" size="small">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </div>

        <div class="wrong-list">
          <article v-for="item in filteredWrongQuestions" :key="item.id" class="wrong-item">
            <p>{{ item.stem }}</p>
            <span>{{ item.chapterTitle }} / {{ item.difficulty }} / 正确率 {{ item.accuracy }}%</span>
          </article>
        </div>

        <h4 class="sub-heading">考试历史</h4>
        <el-table :data="quizHistory" size="small" max-height="220">
          <el-table-column prop="chapterTitle" label="章节" />
          <el-table-column prop="score" label="分数" width="80" />
          <el-table-column prop="durationSeconds" label="用时" width="90" />
          <el-table-column prop="createTime" label="时间" min-width="150" />
        </el-table>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus/es/components/message/index.mjs';
import { computed, onMounted, reactive, ref } from 'vue';
import { ElEmpty } from 'element-plus/es/components/empty/index.mjs';
import { ElForm, ElFormItem } from 'element-plus/es/components/form/index.mjs';
import { ElInput } from 'element-plus/es/components/input/index.mjs';
import { ElInputNumber } from 'element-plus/es/components/input-number/index.mjs';
import { ElOption, ElSelect } from 'element-plus/es/components/select/index.mjs';
import { ElProgress } from 'element-plus/es/components/progress/index.mjs';
import { ElRadio, ElRadioGroup } from 'element-plus/es/components/radio/index.mjs';
import { ElTable, ElTableColumn } from 'element-plus/es/components/table/index.mjs';
import { ElTag } from 'element-plus/es/components/tag/index.mjs';
import 'element-plus/es/components/empty/style/css';
import 'element-plus/es/components/input-number/style/css';
import 'element-plus/es/components/progress/style/css';
import 'element-plus/es/components/radio/style/css';
import 'element-plus/es/components/select/style/css';
import 'element-plus/es/components/table/style/css';
import 'element-plus/es/components/tag/style/css';
import {
  createKnowledgeBase,
  deleteDocument,
  deleteKnowledgeBase,
  fetchChapterContent,
  fetchChapters,
  fetchDocuments,
  fetchKnowledgeBases,
  fetchProgressOverview,
  fetchQuestions,
  fetchQuizHistory,
  fetchWrongQuestions,
  generateOutline,
  generateQuestions,
  resetProgress,
  searchKnowledge,
  submitQuiz,
  updateChapterProgress,
  uploadDocument,
  type Chapter,
  type ChapterContent,
  type KnowledgeBase,
  type KnowledgeDocument,
  type ProgressOverview,
  type Question,
  type QuizHistory,
  type QuizResult,
  type SearchChunk,
  type WrongQuestion,
} from '../../api/learning';
import { resolveErrorMessage } from '../../utils/errorMessage';

const loading = ref(false);
const knowledgeBases = ref<KnowledgeBase[]>([]);
const selectedKbId = ref<number | null>(null);
const documents = ref<KnowledgeDocument[]>([]);
const chapters = ref<Chapter[]>([]);
const chapterContent = ref<ChapterContent | null>(null);
const selectedChapterId = ref<number | null>(null);
const selectedProgressStatus = ref('not_started');
const progress = ref<ProgressOverview>({ total: 0, completed: 0, percent: 0 });
const questions = ref<Question[]>([]);
const quizResult = ref<QuizResult | null>(null);
const quizHistory = ref<QuizHistory[]>([]);
const wrongQuestions = ref<WrongQuestion[]>([]);
const searchResults = ref<SearchChunk[]>([]);
const searchKeyword = ref('');
const fileInputRef = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const questionDifficulty = ref('medium');
const questionCount = ref(5);
const answerMap = reactive<Record<number, string>>({});
const wrongFilter = reactive<{ chapterId?: number; difficulty?: string }>({});
const newKb = reactive({ name: '', description: '' });

const selectedKb = computed(() => knowledgeBases.value.find((item) => item.id === selectedKbId.value));
const filteredWrongQuestions = computed(() =>
  wrongQuestions.value.filter((item) => {
    if (wrongFilter.chapterId && item.chapterId !== wrongFilter.chapterId) {
      return false;
    }
    if (wrongFilter.difficulty && item.difficulty !== wrongFilter.difficulty) {
      return false;
    }
    return true;
  }),
);

onMounted(async () => {
  await loadKnowledgeBases();
  await loadReviewData();
});

async function runAction(action: () => Promise<void>, successMessage?: string): Promise<void> {
  loading.value = true;
  try {
    await action();
    if (successMessage) {
      ElMessage.success(successMessage);
    }
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error));
  } finally {
    loading.value = false;
  }
}

async function loadKnowledgeBases(): Promise<void> {
  knowledgeBases.value = await fetchKnowledgeBases();
  if (!selectedKbId.value && knowledgeBases.value.length > 0) {
    await selectKnowledgeBase(knowledgeBases.value[0].id);
  }
}

async function selectKnowledgeBase(id: number): Promise<void> {
  selectedKbId.value = id;
  chapterContent.value = null;
  selectedChapterId.value = null;
  questions.value = [];
  quizResult.value = null;
  await Promise.all([loadDocuments(), loadChapters(), loadProgress()]);
}

async function handleCreateKnowledgeBase(): Promise<void> {
  if (!newKb.name) {
    ElMessage.warning('请输入知识库名称');
    return;
  }
  await runAction(async () => {
    const created = await createKnowledgeBase({ name: newKb.name, description: newKb.description });
    newKb.name = '';
    newKb.description = '';
    await loadKnowledgeBases();
    await selectKnowledgeBase(created.id);
  }, '知识库已创建');
}

async function handleDeleteKnowledgeBase(): Promise<void> {
  if (!selectedKbId.value) {
    return;
  }
  await runAction(async () => {
    await deleteKnowledgeBase(selectedKbId.value as number);
    selectedKbId.value = null;
    documents.value = [];
    chapters.value = [];
    progress.value = { total: 0, completed: 0, percent: 0 };
    await loadKnowledgeBases();
  }, '知识库已删除');
}

async function loadDocuments(): Promise<void> {
  documents.value = selectedKbId.value ? await fetchDocuments(selectedKbId.value) : [];
}

function handleFileChange(event: Event): void {
  selectedFile.value = (event.target as HTMLInputElement).files?.[0] || null;
}

async function handleUploadDocument(): Promise<void> {
  if (!selectedKbId.value || !selectedFile.value) {
    ElMessage.warning('请先选择知识库和文件');
    return;
  }
  await runAction(async () => {
    await uploadDocument(selectedKbId.value as number, selectedFile.value as File);
    selectedFile.value = null;
    if (fileInputRef.value) {
      fileInputRef.value.value = '';
    }
    await Promise.all([loadDocuments(), loadKnowledgeBases()]);
  }, '文档已上传并解析');
}

async function handleDeleteDocument(id: number): Promise<void> {
  await runAction(async () => {
    await deleteDocument(id);
    await Promise.all([loadDocuments(), loadKnowledgeBases()]);
  }, '文档已删除');
}

async function handleSearch(): Promise<void> {
  if (!selectedKbId.value || !searchKeyword.value) {
    return;
  }
  searchResults.value = await searchKnowledge(selectedKbId.value, searchKeyword.value);
}

async function loadChapters(): Promise<void> {
  chapters.value = selectedKbId.value ? await fetchChapters(selectedKbId.value) : [];
}

async function handleGenerateOutline(): Promise<void> {
  if (!selectedKbId.value) {
    return;
  }
  await runAction(async () => {
    chapters.value = await generateOutline(selectedKbId.value as number);
    await loadProgress();
  }, '课程大纲已生成');
}

async function selectChapter(id: number): Promise<void> {
  selectedChapterId.value = id;
  chapterContent.value = await fetchChapterContent(id);
  questions.value = await fetchQuestions(id);
  selectedProgressStatus.value = 'not_started';
}

async function handleUpdateProgress(): Promise<void> {
  if (!selectedChapterId.value) {
    return;
  }
  await updateChapterProgress(selectedChapterId.value, selectedProgressStatus.value);
  await loadProgress();
}

async function loadProgress(): Promise<void> {
  progress.value = selectedKbId.value ? await fetchProgressOverview(selectedKbId.value) : { total: 0, completed: 0, percent: 0 };
}

async function handleResetProgress(): Promise<void> {
  if (!selectedKbId.value) {
    return;
  }
  await resetProgress(selectedKbId.value);
  await loadProgress();
  selectedProgressStatus.value = 'not_started';
}

async function handleGenerateQuestions(): Promise<void> {
  if (!selectedChapterId.value) {
    return;
  }
  await runAction(async () => {
    questions.value = await generateQuestions(selectedChapterId.value as number, questionDifficulty.value, questionCount.value);
    Object.keys(answerMap).forEach((key) => delete answerMap[Number(key)]);
    quizResult.value = null;
  }, '题目已生成');
}

async function handleSubmitQuiz(): Promise<void> {
  if (!selectedChapterId.value) {
    return;
  }
  const answers = questions.value.map((question) => ({
    questionId: question.id,
    userAnswer: answerMap[question.id] || '',
  }));
  quizResult.value = await submitQuiz(selectedChapterId.value, answers, 300);
  await loadReviewData();
}

async function loadReviewData(): Promise<void> {
  [quizHistory.value, wrongQuestions.value] = await Promise.all([fetchQuizHistory(), fetchWrongQuestions()]);
}
</script>

<style scoped>
.learning-workbench-page {
  display: grid;
  gap: 24px;
  padding: 28px var(--space-page-x) 40px;
}

.workbench-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
}

.workbench-eyebrow {
  margin: 0 0 6px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 700;
}

.workbench-header h2 {
  margin: 0;
  color: var(--color-heading);
  font-size: 28px;
}

.workbench-score-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.workbench-score-grid span {
  padding: 7px 10px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-muted);
  background: var(--color-surface);
}

.workbench-grid {
  display: grid;
  grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
  gap: 18px;
}

.workbench-panel {
  min-width: 0;
  padding: 18px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.chapter-panel,
.quiz-panel {
  grid-column: span 2;
}

.panel-title-row,
.danger-row,
.upload-row,
.search-row,
.filter-row,
.submit-row,
.quiz-toolbar,
.chapter-content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-title-row h3 {
  margin: 0;
  color: var(--color-heading);
  font-size: 18px;
}

.panel-hint,
.danger-row,
.submit-row span,
.wrong-item span,
.search-result-list span {
  color: var(--color-muted);
  font-size: 13px;
}

.compact-form {
  margin-top: 14px;
}

.kb-list,
.search-result-list,
.question-list,
.wrong-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.kb-item,
.chapter-item {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  background: var(--color-surface-soft);
  cursor: pointer;
  text-align: left;
}

.kb-item {
  display: grid;
  gap: 4px;
  padding: 11px;
}

.kb-item span {
  color: var(--color-muted);
  font-size: 13px;
}

.kb-item.is-active,
.chapter-item.is-active {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
}

.danger-row,
.search-row,
.filter-row,
.submit-row {
  margin-top: 14px;
}

.upload-row input {
  min-width: 0;
}

.search-result-list p,
.wrong-item,
.question-item {
  margin: 0;
  padding: 11px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface-soft);
  line-height: 1.6;
}

.progress-strip {
  display: grid;
  grid-template-columns: 150px minmax(180px, 1fr) auto;
  align-items: center;
  gap: 12px;
  margin-top: 14px;
}

.chapter-layout {
  display: grid;
  grid-template-columns: 290px minmax(0, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.chapter-list {
  display: grid;
  align-content: start;
  gap: 8px;
  max-height: 420px;
  overflow: auto;
}

.chapter-item {
  padding: 10px 12px;
}

.chapter-item.is-section {
  padding-left: 24px;
  font-size: 13px;
}

.chapter-content {
  min-height: 300px;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface-soft);
}

.chapter-content h4,
.chapter-content h5,
.sub-heading {
  margin: 0 0 10px;
  color: var(--color-heading);
}

.chapter-content p {
  margin: 0 0 14px;
  color: var(--color-text);
  line-height: 1.8;
}

.quiz-toolbar {
  justify-content: flex-end;
}

.question-stem {
  margin: 0 0 8px;
  font-weight: 700;
}

.quiz-result-list {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.quiz-result-list p {
  margin: 0;
  line-height: 1.7;
}

.sub-heading {
  margin-top: 18px;
}

@media (max-width: 960px) {
  .workbench-header,
  .workbench-grid,
  .chapter-layout,
  .progress-strip {
    grid-template-columns: 1fr;
  }

  .workbench-header,
  .panel-title-row,
  .upload-row,
  .search-row,
  .filter-row,
  .submit-row,
  .quiz-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .chapter-panel,
  .quiz-panel {
    grid-column: auto;
  }
}
</style>
