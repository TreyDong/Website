import { request, ApiResponse } from '@/app/utils/httpClient';

// 登录请求参数接口
export interface LoginParams {
  email: string;
  password: string;
}

// 登录响应接口
export interface LoginResponse {
  user: {
    id: string;
    name: string;
    email: string;
    role?: string;
  };
  token: string;
}

// 注册请求参数接口
export interface RegisterParams {
  name: string;
  email: string;
  password: string;
}

// 认证服务类
class AuthService {
  private baseUrl = '/api/auth';
  
  // 用户登录
  async login(params: LoginParams): Promise<ApiResponse<LoginResponse>> {
    return request<LoginResponse>('POST', `${this.baseUrl}/login`, params);
  }
  
  // 用户注册
  async register(params: RegisterParams): Promise<ApiResponse<LoginResponse>> {
    return request<LoginResponse>('POST', `${this.baseUrl}/register`, params);
  }
  
  // 退出登录
  async logout(): Promise<ApiResponse<{ success: boolean }>> {
    return request<{ success: boolean }>('POST', `${this.baseUrl}/logout`);
  }
  
  // 获取当前用户信息
  async getCurrentUser(): Promise<ApiResponse<LoginResponse['user']>> {
    return request<LoginResponse['user']>('GET', `${this.baseUrl}/me`);
  }
  
  // 保存token到本地存储
  saveToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }
  
  // 从本地存储获取token
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }
  
  // 清除token
  clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }
  
  // 检查用户是否已登录
  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}

// 导出单例实例
export const authService = new AuthService(); 