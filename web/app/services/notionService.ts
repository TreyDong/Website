import { request, ApiResponse } from '@/app/utils/httpClient';

// 定义 Notion 相关的接口
export interface NotionSetupParams {
  token: string;
  database_id: string;
  activation_code?: string;
  set_covers?: boolean;
  set_icons?: boolean;
  overwrite_covers?: boolean;
  overwrite_icons?: boolean;
}

export interface NotionSetupResponse {
  success: boolean;
  pages_processed?: number;
  covers_updated?: number;
  icons_updated?: number;
  errors?: string[];
  error?: string;
}

// Notion 服务类
class NotionService {
  private baseUrl = 'http://81.68.69.38:3005';
  
  // 设置封面和图标
  async setupCoversAndIcons(params: NotionSetupParams): Promise<ApiResponse<NotionSetupResponse>> {
    try {
      return request<NotionSetupResponse>('POST', `${this.baseUrl}/api/set-covers-icons`, params);
    } catch (error: any) {
      console.error('Notion API request failed:', error);
      return {
        success: false,
        data: {
          success: false,
          error: error.message || 'Failed to connect to Notion service'
        },
      };
    }
  }
  
  // 可以添加更多 Notion 相关的方法
  // ...
}

// 导出单例实例
export const notionService = new NotionService(); 