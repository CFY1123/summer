interface LearningApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface KnowledgeBase {
  id: number;
  name: string;
  description?: string;
  documentCount: number;
  chunkCount: number;
  vectorCollection: string;
  createTime: string;
  updateTime: string;
}

export interface KnowledgeDocument {
  id: number;
  knowledgeBaseId: number;
  filename: string;
  fileType: string;
  parserStatus: string;
  chunkCount: number;
  errorMessage?: string;
  createTime: string;
}

export interface Chapter {
  id: number;
  knowledgeBaseId: number;
  parentId: number;
  title: string;
  summary: string;
  sortNo: number;
}

export interface ChapterContent extends Chapter {
  content: Array<{ title: string; text: string }>;
}

export interface ProgressOverview {
  total: number;
  completed: number;
  percent: number;
}

export interface Question {
  id: number;
  chapterId: number;
  questionType: string;
  difficulty: string;
  stem: string;
  options: string[];
  answer: string;
  analysis: string;
}

export interface QuizResult {
  attemptId: number;
  score: number;
  total: number;
  correct: number;
  details: Array<{
    question: Question;
    userAnswer: string;
    isCorrect: boolean;
  }>;
}

export interface QuizHistory {
  id: number;
  chapterId: number;
  chapterTitle: string;
  score: number;
  durationSeconds: number;
  totalCount: number;
  correctCount: number;
  createTime: string;
}

export interface WrongQuestion {
  id: number;
  questionId: number;
  chapterId: number;
  chapterTitle: string;
  difficulty: string;
  stem: string;
  options: string[];
  answer: string;
  analysis: string;
  wrongCount: number;
  correctCount: number;
  accuracy: number;
  lastWrongTime: string;
}

export interface SearchChunk {
  id: number;
  documentId: number;
  chunkIndex: number;
  preview: string;
  score?: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init);
  const result = (await response.json()) as LearningApiResponse<T>;
  if (!response.ok || result.code !== 200) {
    throw new Error(result.message || '学习平台接口请求失败');
  }
  return result.data;
}

export function fetchKnowledgeBases(): Promise<KnowledgeBase[]> {
  return request<KnowledgeBase[]>('/knowledge-bases');
}

export function createKnowledgeBase(payload: { name: string; description?: string }): Promise<KnowledgeBase> {
  return request<KnowledgeBase>('/knowledge-bases', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function deleteKnowledgeBase(id: number): Promise<void> {
  return request<void>(`/knowledge-bases/${id}`, { method: 'DELETE' });
}

export function fetchDocuments(kbId: number): Promise<KnowledgeDocument[]> {
  return request<KnowledgeDocument[]>(`/knowledge-bases/${kbId}/documents`);
}

export function uploadDocument(kbId: number, file: File): Promise<KnowledgeDocument> {
  const body = new FormData();
  body.append('file', file);
  return request<KnowledgeDocument>(`/knowledge-bases/${kbId}/documents`, {
    method: 'POST',
    body,
  });
}

export function deleteDocument(id: number): Promise<void> {
  return request<void>(`/documents/${id}`, { method: 'DELETE' });
}

export function searchKnowledge(kbId: number, keyword: string): Promise<SearchChunk[]> {
  return request<SearchChunk[]>(`/knowledge-bases/${kbId}/search?keyword=${encodeURIComponent(keyword)}`);
}

export function generateOutline(kbId: number): Promise<Chapter[]> {
  return request<Chapter[]>(`/knowledge-bases/${kbId}/outline`, { method: 'POST' });
}

export function fetchChapters(kbId: number): Promise<Chapter[]> {
  return request<Chapter[]>(`/knowledge-bases/${kbId}/chapters`);
}

export function fetchChapterContent(chapterId: number): Promise<ChapterContent> {
  return request<ChapterContent>(`/chapters/${chapterId}/content`);
}

export function updateChapterProgress(chapterId: number, status: string): Promise<void> {
  return request<void>(`/chapters/${chapterId}/progress`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
}

export function fetchProgressOverview(kbId: number): Promise<ProgressOverview> {
  return request<ProgressOverview>(`/knowledge-bases/${kbId}/progress`);
}

export function resetProgress(kbId: number): Promise<void> {
  return request<void>(`/knowledge-bases/${kbId}/progress`, { method: 'DELETE' });
}

export function generateQuestions(chapterId: number, difficulty: string, count: number): Promise<Question[]> {
  return request<Question[]>(`/chapters/${chapterId}/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty, count }),
  });
}

export function fetchQuestions(chapterId: number): Promise<Question[]> {
  return request<Question[]>(`/chapters/${chapterId}/questions`);
}

export function submitQuiz(
  chapterId: number,
  answers: Array<{ questionId: number; userAnswer: string }>,
  durationSeconds: number,
): Promise<QuizResult> {
  return request<QuizResult>(`/chapters/${chapterId}/quiz`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers, durationSeconds }),
  });
}

export function fetchQuizHistory(): Promise<QuizHistory[]> {
  return request<QuizHistory[]>('/quiz/history');
}

export function fetchWrongQuestions(): Promise<WrongQuestion[]> {
  return request<WrongQuestion[]>('/wrong-questions');
}
