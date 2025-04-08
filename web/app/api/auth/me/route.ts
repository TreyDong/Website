import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

// 模拟用户数据，实际应用中应该从数据库获取
const mockUsers = [
  {
    id: '1',
    name: '测试用户',
    email: 'test@example.com',
    password: 'password123',
    role: 'user'
  }
];

export async function GET(request: NextRequest) {
  try {
    // 获取认证token
    const token = cookies().get('auth_token')?.value;
    
    if (!token) {
      return NextResponse.json(
        { 
          success: false,
          error: "Unauthorized"
        },
        { status: 401 }
      );
    }
    
    // 在实际应用中，应该验证token并获取对应的用户
    // 这里简单返回第一个用户作为示例
    const user = mockUsers[0];
    
    if (!user) {
      return NextResponse.json(
        { 
          success: false,
          error: "User not found"
        },
        { status: 404 }
      );
    }
    
    // 不返回密码
    const { password: _, ...userWithoutPassword } = user;
    
    return NextResponse.json({
      success: true,
      data: userWithoutPassword
    });
    
  } catch (error: any) {
    console.error('Get current user failed:', error);
    return NextResponse.json(
      { 
        success: false,
        error: error.message || 'Failed to get current user'
      },
      { status: 500 }
    );
  }
} 