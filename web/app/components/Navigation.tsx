'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { authService } from '@/app/services/authService';

export default function Navigation() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // 检查用户登录状态
    useEffect(() => {
        setIsLoggedIn(authService.isLoggedIn());
    }, []);

    return (
        <nav className="fixed w-full bg-white/90 backdrop-blur-sm z-10 py-4 px-6 md:px-12 flex items-center border-b border-gray-100">
            <div className="text-xl font-medium tracking-tight mr-8">
                <Link href="/" className="text-black">
                    Trey
                </Link>
            </div>
            
            {/* 将菜单项放在中间，占据大部分空间 */}
            <div className="hidden md:flex space-x-8 text-sm flex-grow">
                <Link
                    href="/notion"
                    className="hover:text-black text-gray-500 transition-colors"
                >
                    Notion
                </Link>
                <Link
                    href="/weread"
                    className="hover:text-black text-gray-500 transition-colors"
                >
                    微信读书自动签到
                </Link>
            </div>
            
            {/* 登录/仪表板按钮 */}
            {isLoggedIn ? (
                <Link
                    href="/dashboard"
                    className="px-4 py-2 border border-gray-200 rounded-full text-sm hover:bg-gray-50 transition-colors"
                >
                    仪表板
                </Link>
            ) : (
                <Link
                    href="/login"
                    className="px-4 py-2 border border-gray-200 rounded-full text-sm hover:bg-gray-50 transition-colors"
                >
                    登录
                </Link>
            )}
        </nav>
    );
}