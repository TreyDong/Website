import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

// 这里应该引入您的用户验证逻辑，例如数据库查询
// 这里使用模拟数据作为示例
const mockUsers = [
  {
    id: '1',
    name: '测试用户',
    email: 'test@example.com',
    password: 'password123', // 实际应用中应该使用加密密码
    role: 'user'
  }
];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;
    
    // 验证必需的参数
    if (!email || !password) {
      return NextResponse.json(
        { 
          success: false,
          error: "Missing required parameters: email and password"
        },
        { status: 400 }
      );
    }
    
    // 查找用户
    const user = mockUsers.find(u => u.email === email);
    
    // 验证用户和密码
    if (!user || user.password !== password) {
      return NextResponse.json(
        { 
          success: false,
          error: "Invalid email or password"
        },
        { status: 401 }
      );
    }
    
    // 创建一个不包含密码的用户对象
    const { password: _, ...userWithoutPassword } = user;
    
    // 生成token (在实际应用中，应该使用JWT或其他安全方法)
    const token = `mock-token-${Date.now()}`;
    
    // 设置cookie
    cookies().set({
      name: 'auth_token',
      value: token,
      httpOnly: true,
      path: '/',
      maxAge: 60 * 60 * 24 * 7, // 7天
      sameSite: 'strict',
      secure: process.env.NODE_ENV === 'production'
    });
    
    return NextResponse.json({
      success: true,
      data: {
        user: userWithoutPassword,
        token
      }
    });
    
  } catch (error: any) {
    console.error('Login failed:', error);
    return NextResponse.json(
      { 
        success: false,
        error: error.message || 'Login failed'
      },
      { status: 500 }
    );
  }
} 