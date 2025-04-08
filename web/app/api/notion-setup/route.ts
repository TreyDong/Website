import { NextRequest, NextResponse } from 'next/server';
import { notionService } from '@/app/services/notionService';

export async function POST(request: NextRequest) {
    console.log('API route called')
    try {
        const body = await request.json();
        
        // 验证必需的参数
        if (!body.token || !body.database_id) {
            return NextResponse.json(
                { 
                    success: false,
                    error: "Missing required parameters: token and database_id"
                },
                { status: 400 }
            );
        }
        
        // 使用专门的 Notion 服务
        const response = await notionService.setupCoversAndIcons(body);
        
        // 确保返回的是可序列化的对象
        return NextResponse.json({
            success: response.success,
            ...response.data,
        });
    } catch (error: any) {
        console.error('API request failed:', error);
        return NextResponse.json(
            { 
                success: false,
                error: error.message || 'Failed to process request'
            },
            { status: 500 }
        );
    }
}
