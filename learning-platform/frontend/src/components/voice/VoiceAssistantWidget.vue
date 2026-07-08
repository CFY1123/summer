<template>
  <div class="voice-assistant-widget" :class="{ 'is-listening': listening }">
    <button class="voice-toggle-button" type="button" :aria-pressed="enabled" @click="toggleVoice">
      <span class="voice-dot" aria-hidden="true"></span>
      <span>{{ enabled ? '语音开' : '语音关' }}</span>
    </button>

    <div v-if="enabled" class="voice-status-panel" role="status">
      <strong>{{ listening ? '正在聆听' : '语音待机' }}</strong>
      <span>{{ statusText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus/es/components/message/index.mjs';
import { onBeforeUnmount, ref } from 'vue';
import { useRouter } from 'vue-router';

type SpeechRecognitionConstructor = new () => {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: { error?: string }) => void) | null;
  onend: (() => void) | null;
};

interface SpeechRecognitionEventLike {
  resultIndex: number;
  results: ArrayLike<{
    isFinal: boolean;
    0: { transcript: string };
  }>;
}

const router = useRouter();
const enabled = ref(false);
const listening = ref(false);
const statusText = ref('说“学习助手 打开学习”、“开始测验”或“查看进度”。');
const recognition = ref<InstanceType<SpeechRecognitionConstructor> | null>(null);

function resolveRecognitionCtor(): SpeechRecognitionConstructor | null {
  const speechWindow = window as typeof window & {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  };
  return speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition || null;
}

function toggleVoice(): void {
  if (enabled.value) {
    stopVoice();
    return;
  }
  startVoice();
}

function startVoice(): void {
  const SpeechRecognition = resolveRecognitionCtor();
  if (!SpeechRecognition) {
    ElMessage.warning('当前浏览器不支持语音识别，可继续使用页面按钮操作。');
    return;
  }

  enabled.value = true;
  recognition.value = new SpeechRecognition();
  recognition.value.lang = 'zh-CN';
  recognition.value.continuous = true;
  recognition.value.interimResults = false;
  recognition.value.onresult = handleVoiceResult;
  recognition.value.onerror = () => {
    statusText.value = '语音识别暂时不可用，请检查麦克风权限。';
  };
  recognition.value.onend = () => {
    listening.value = false;
    if (enabled.value) {
      startRecognitionSafely();
    }
  };
  startRecognitionSafely();
  speak('语音模式已开启');
}

function stopVoice(): void {
  enabled.value = false;
  listening.value = false;
  recognition.value?.stop();
  recognition.value = null;
  statusText.value = '语音模式已关闭。';
  speak('语音模式已关闭');
}

function startRecognitionSafely(): void {
  try {
    recognition.value?.start();
    listening.value = true;
    statusText.value = '正在等待语音指令。';
  } catch {
    listening.value = true;
  }
}

function handleVoiceResult(event: SpeechRecognitionEventLike): void {
  const transcript = Array.from(event.results)
    .slice(event.resultIndex)
    .map((result) => result[0]?.transcript || '')
    .join('')
    .trim();

  if (!transcript) {
    return;
  }

  statusText.value = `识别到：${transcript}`;
  runCommand(transcript);
}

async function runCommand(rawText: string): Promise<void> {
  const text = rawText.replace(/\s/g, '');
  const commandText = text.includes('学习助手') ? text.replace('学习助手', '') : text;

  if (commandText.includes('关闭语音')) {
    stopVoice();
    return;
  }

  if (commandText.includes('打开学习') || commandText.includes('学习工作台') || commandText.includes('知识库')) {
    await navigate('/learning-workbench', '已打开学习工作台');
    return;
  }

  if (commandText.includes('学习路线') || commandText.includes('查看资料')) {
    await navigate('/learning-roadmap', '已打开学习路线');
    return;
  }

  if (commandText.includes('开始测验') || commandText.includes('开始刷题') || commandText.includes('刷题')) {
    await navigate('/practice-agent', '已打开智能刷题');
    return;
  }

  if (commandText.includes('查看进度') || commandText.includes('个人中心')) {
    await navigate('/profile', '已打开个人中心');
    return;
  }

  if (commandText.includes('面试题')) {
    await navigate('/interview-questions', '已打开热门面试题');
    return;
  }

  statusText.value = '没有匹配到指令，可说：打开学习、开始测验、查看进度。';
}

async function navigate(path: string, message: string): Promise<void> {
  await router.push(path);
  ElMessage.success(message);
  speak(message);
}

function speak(text: string): void {
  if (!window.speechSynthesis) {
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'zh-CN';
  utterance.rate = 1;
  window.speechSynthesis.speak(utterance);
}

onBeforeUnmount(() => {
  enabled.value = false;
  recognition.value?.stop();
});
</script>

<style scoped>
.voice-assistant-widget {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 50;
  display: grid;
  justify-items: end;
  gap: 8px;
  pointer-events: none;
}

.voice-toggle-button,
.voice-status-panel {
  pointer-events: auto;
}

.voice-toggle-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 96px;
  height: 38px;
  padding: 0 14px;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  color: var(--color-text-primary);
  background: var(--color-glass-surface-strong);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.14);
  cursor: pointer;
}

.voice-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--el-color-info);
}

.is-listening .voice-dot {
  background: var(--el-color-success);
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--el-color-success) 16%, transparent);
}

.voice-status-panel {
  display: grid;
  gap: 2px;
  width: min(280px, calc(100vw - 32px));
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
  background: var(--color-glass-surface-strong);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
  font-size: 13px;
  line-height: 1.5;
}

.voice-status-panel strong {
  color: var(--color-text-primary);
  font-size: 14px;
}

@media (max-width: 768px) {
  .voice-assistant-widget {
    right: 16px;
    bottom: 78px;
  }
}
</style>
