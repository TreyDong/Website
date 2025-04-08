import { request, ApiResponse } from '@/app/utils/httpClient';

// 用户相关接口
export interface User {
  id: string;
  name: string;
  email: string;
  // 其他用户属性
}

export interface LoginParams {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
}

// 用户服务类
class UserService {
  private baseUrl = '/api/users';
  
  // 登录
  async login(params: LoginParams): Promise<ApiResponse<LoginResponse>> {
    return request<LoginResponse>('POST', `${this.baseUrl}/login`, params);
  }
  
  // 获取用户信息
  async getUserInfo(userId: string): Promise<ApiResponse<User>> {
    return request<User>('GET', `${this.baseUrl}/${userId}`);
  }
  
  // 更新用户信息
  async updateUser(userId: string, userData: Partial<User>): Promise<ApiResponse<User>> {
    return request<User>('PUT', `${this.baseUrl}/${userId}`, userData);
  }
}

// 导出单例实例
export const userService = new UserService(); 