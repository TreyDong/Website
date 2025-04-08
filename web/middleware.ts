import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// 需要保护的路由
const protectedRoutes = ['/dashboard'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;
  const { pathname } = request.nextUrl;

  // 检查是否是受保护的路由
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname === route || pathname.startsWith(`${route}/`)
  );

  // 如果是受保护的路由但没有token，重定向到登录页面
  if (isProtectedRoute && !token) {
    const url = new URL('/login', request.url);
    url.searchParams.set('from', pathname);
    return NextResponse.redirect(url);
  }

  // 如果已经登录但访问登录页面，重定向到仪表板
  if ((pathname === '/login' || pathname === '/register') && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

// 配置匹配的路由
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/login',
    '/register',
  ],
}; 