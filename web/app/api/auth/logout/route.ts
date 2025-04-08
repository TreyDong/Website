import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: NextRequest) {
  try {
    // 清除认证cookie
    cookies().delete('auth_token');
    
    return NextResponse.json({
      success: true,
      data: {
        success: true
      }
    });
    
  } catch (error: any) {
    console.error('Logout failed:', error);
    return NextResponse.json(
      { 
        success: false,
        error: error.message || 'Logout failed'
      },
      { status: 500 }
    );
  }
} 