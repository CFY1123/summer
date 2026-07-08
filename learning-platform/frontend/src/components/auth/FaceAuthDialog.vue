<template>
  <el-dialog
    v-model="visible"
    title="人脸识别登录"
    aria-label="人脸识别登录"
    width="520px"
    class="face-auth-dialog"
    destroy-on-close
    align-center
    @opened="startCamera"
    @closed="stopCamera"
  >
    <div class="face-auth-panel">
      <el-form label-position="top" class="face-auth-form">
        <el-form-item label="用户名">
          <el-input
            v-model.trim="username"
            autocomplete="username"
            maxlength="128"
            placeholder="默认 admin"
            size="large"
            clearable
          />
        </el-form-item>
      </el-form>

      <div class="face-camera-box">
        <video ref="videoRef" class="face-camera-video" autoplay muted playsinline></video>
        <canvas ref="canvasRef" class="face-camera-canvas" width="320" height="240"></canvas>
        <div v-if="!cameraReady" class="face-camera-placeholder">{{ cameraStatus }}</div>
      </div>

      <p class="face-auth-tip">{{ captureTip }}</p>
      <p v-if="errorMessage" class="auth-form-error" role="alert">{{ errorMessage }}</p>
    </div>

    <template #footer>
      <div class="face-auth-actions">
        <el-button @click="visible = false">备用密码登录</el-button>
        <el-button :loading="submitting" plain @click="submitRegister">注册人脸</el-button>
        <el-button :loading="submitting" type="primary" @click="submitLogin">人脸登录</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus/es/components/message/index.mjs';
import { computed, nextTick, onBeforeUnmount, ref } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { resolveErrorMessage } from '../../utils/errorMessage';

const visible = defineModel<boolean>({ required: true });
const authStore = useAuthStore();
const username = ref(authStore.user?.username || 'admin');
const videoRef = ref<HTMLVideoElement | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const stream = ref<MediaStream | null>(null);
const cameraReady = ref(false);
const submitting = ref(false);
const errorMessage = ref('');
const livenessStep = ref(false);

const cameraStatus = computed(() => (cameraReady.value ? '摄像头已开启' : '正在等待摄像头权限'));
const captureTip = computed(() =>
  livenessStep.value ? '请眨眼或轻微转头，系统会采集第二帧做简单活体检测。' : '请正对摄像头，点击注册或登录后会自动采集两帧。'
);

async function startCamera(): Promise<void> {
  errorMessage.value = '';
  cameraReady.value = false;
  await nextTick();

  if (!navigator.mediaDevices?.getUserMedia) {
    errorMessage.value = '当前浏览器不支持摄像头调用，请使用密码登录。';
    return;
  }

  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { width: 320, height: 240, facingMode: 'user' },
      audio: false,
    });
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value;
      await videoRef.value.play();
    }
    cameraReady.value = true;
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error, '摄像头开启失败，请检查权限后重试。');
    ElMessage.error(errorMessage.value);
  }
}

function stopCamera(): void {
  stream.value?.getTracks().forEach((track) => track.stop());
  stream.value = null;
  cameraReady.value = false;
  livenessStep.value = false;
}

async function submitRegister(): Promise<void> {
  await submitFaceAction('register');
}

async function submitLogin(): Promise<void> {
  await submitFaceAction('login');
}

async function submitFaceAction(action: 'register' | 'login'): Promise<void> {
  if (!username.value) {
    errorMessage.value = '请输入用户名。';
    ElMessage.warning(errorMessage.value);
    return;
  }

  submitting.value = true;
  errorMessage.value = '';
  try {
    const payload = await captureFacePayload();
    if (action === 'register') {
      await authStore.registerFaceTemplate(payload);
      return;
    }

    await authStore.loginWithFace(payload);
    visible.value = false;
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error, '人脸识别失败，请重试或使用密码登录。');
    ElMessage.error(errorMessage.value);
  } finally {
    submitting.value = false;
    livenessStep.value = false;
  }
}

async function captureFacePayload() {
  if (!cameraReady.value) {
    throw new Error('摄像头尚未就绪，请稍后再试。');
  }

  const frame = captureFrame();
  livenessStep.value = true;
  await wait(900);
  const livenessFrame = captureFrame();
  return {
    username: username.value || 'admin',
    frame,
    livenessFrame,
  };
}

function captureFrame(): string {
  const video = videoRef.value;
  const canvas = canvasRef.value;
  const context = canvas?.getContext('2d');
  if (!video || !canvas || !context) {
    throw new Error('摄像头画面采集失败。');
  }

  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.72);
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

onBeforeUnmount(stopCamera);
</script>

<style scoped>
.face-auth-panel {
  display: grid;
  gap: 14px;
}

.face-auth-form {
  margin-bottom: -4px;
}

.face-camera-box {
  position: relative;
  min-height: 240px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface-soft);
}

.face-camera-video {
  display: block;
  width: 100%;
  height: 240px;
  object-fit: cover;
}

.face-camera-canvas {
  display: none;
}

.face-camera-placeholder {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: var(--color-text-secondary);
  background: var(--color-surface-soft);
}

.face-auth-tip {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.face-auth-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.face-auth-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}
</style>
