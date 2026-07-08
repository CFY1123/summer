const DEFAULT_ERROR_MESSAGE = '操作失败，请稍后重试';

const ERROR_MESSAGE_MAP: Record<string, string> = {
  FACE_NOT_REGISTERED: '当前账号还没有注册人脸，请先注册人脸模板。',
  FACE_TEMPLATE_EXPIRED: '旧版人脸模板已失效，请重新注册人脸。',
  FACE_MISMATCH: '人脸与注册模板不一致，请本人登录或使用密码登录。',
  FACE_NOT_FOUND: '没有检测到清晰的人脸，请正对摄像头重试。',
  FACE_DETECTOR_UNAVAILABLE: '人脸检测模型加载失败，请检查 OpenCV 环境。',
  LIVENESS_CHECK_FAILED: '活体检测未通过，请眨眼或轻微转头后重试。',
  IMAGE_DECODE_FAILED: '摄像头画面解析失败，请重新采集。',
  USERNAME_REQUIRED: '请输入用户名后再进行人脸识别。',
};

/**
 * 解析接口或运行时错误的展示文案。
 *
 * @param error 原始错误对象
 * @param fallback 无明确错误信息时的兜底文案
 * @return 可直接展示给用户的错误文案
 */
export function resolveErrorMessage(error: unknown, fallback = DEFAULT_ERROR_MESSAGE): string {
  if (error instanceof Error && error.message in ERROR_MESSAGE_MAP) {
    return ERROR_MESSAGE_MAP[error.message];
  }

  // 只信任标准 Error 的 message，其它异常类型统一走页面提供的兜底文案。
  return error instanceof Error && error.message ? error.message : fallback;
}
