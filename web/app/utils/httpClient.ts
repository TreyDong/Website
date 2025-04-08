import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// 定义响应数据接口
export interface ApiResponse<T = any> {
  data?: T;
  success: boolean;
  message?: string;
  errors?: string[];
  error?: string;
  code?: number;
}

// 创建 axios 实例
const httpClient = axios.create({
  timeout: 30000, // 默认超时时间
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
httpClient.interceptors.request.use(
  (config) => {
    // 从本地存储获取token
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
httpClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // 处理错误响应
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('No response received:', error.request);
    } else {
      // 请求配置出错
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

// 通用请求方法
export const request = async <T = any>(
  method: string,
  url: string, 
  data?: any, 
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  try {
    let response: AxiosResponse;
    
    switch (method.toUpperCase()) {
      case 'GET':
        response = await httpClient.get(url, { params: data, ...config });
        break;
      case 'POST':
        response = await httpClient.post(url, data, config);
        break;
      case 'PUT':
        response = await httpClient.put(url, data, config);
        break;
      case 'DELETE':
        response = await httpClient.delete(url, { data, ...config });
        break;
      default:
        throw new Error(`Unsupported method: ${method}`);
    }
    
    return response.data;
  } catch (error: any) {
    console.error(`${method} request to ${url} failed:`, error);
    
    // 构造统一的错误响应
    const errorResponse: ApiResponse = {
      success: false,
      message: error.message || `Request failed`,
      errors: [error.message || 'Unknown error occurred']
    };
    
    if (error.response?.data) {
      // 如果服务器返回了错误信息，优先使用服务器的错误信息
      return error.response.data as ApiResponse;
    }
    
    if (error.response?.status === 400) {
      // 处理 400 错误
      return {
        success: false,
        error: "Bad request: Please check your input parameters",
        ...error.response.data
      };
    } else if (error.response?.status === 401) {
      // 处理 401 错误
      return {
        success: false,
        error: "Authentication failed: Please check your token",
        ...error.response.data
      };
    } else if (error.response?.status === 404) {
      // 处理 404 错误
      return {
        success: false,
        error: "Resource not found: Please check your database ID",
        ...error.response.data
      };
    }
    
    return errorResponse;
  }
};

// 为了向后兼容，保留原来的方法
export const get = <T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>('GET', url, params, config);
};

export const post = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>('POST', url, data, config);
};

export const put = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>('PUT', url, data, config);
};

export const del = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>('DELETE', url, data, config);
};

export default httpClient; 