import { post, postPublic } from './http';
import type { CurrentUser } from './user';

export interface RegisterPayload {
  username: string;
  password: string;
  nickname?: string;
  email?: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface AuthResult {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
  user: CurrentUser;
}

export interface FaceAuthPayload {
  username: string;
  frame: string;
  livenessFrame: string;
}

export interface FaceRegisterResult {
  username: string;
  registered: boolean;
}

/**
 * 调用注册接口。
 */
export function register(payload: RegisterPayload): Promise<AuthResult> {
  return postPublic<AuthResult, RegisterPayload>('/auth/register', payload);
}

/**
 * 调用登录接口。
 */
export function login(payload: LoginPayload): Promise<AuthResult> {
  return postPublic<AuthResult, LoginPayload>('/auth/login', payload);
}

/**
 * 提交摄像头采集的人脸模板。
 */
export function registerFace(payload: FaceAuthPayload): Promise<FaceRegisterResult> {
  return postPublic<FaceRegisterResult, FaceAuthPayload>('/auth/face/register', payload);
}

/**
 * 使用摄像头采集的人脸信息登录。
 */
export function loginByFace(payload: FaceAuthPayload): Promise<AuthResult> {
  return postPublic<AuthResult, FaceAuthPayload>('/auth/face/login', payload);
}

/**
 * 调用退出登录接口。
 */
export function logout(): Promise<boolean> {
  return post<boolean>('/auth/logout');
}
