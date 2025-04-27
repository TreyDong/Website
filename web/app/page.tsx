'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/app/components/Navigation';
import Link from 'next/link';

export default function Page() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return null;
    }

    return (
        <div className="min-h-screen bg-white text-gray-800 font-sans">
            <Navigation />
            
            <section className="pt-32 pb-20 px-6 md:px-12">
                <div className="max-w-6xl mx-auto">
                    <h1 className="text-4xl md:text-6xl lg:text-7xl font-light leading-tight mb-6">
                        简约设计 <br />
                        <span className="text-gray-400">
                            卓越体验
                        </span>
                    </h1>
                    <p className="text-lg md:text-xl text-gray-600 max-w-xl mb-12">
                        专注于创造简洁大气的产品体验，让复杂的功能变得简单易用，为用户带来愉悦的使用体验。
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4">
                        <button className="px-8 py-3 bg-black text-white rounded-full hover:bg-gray-800 transition-colors">
                            了解更多
                        </button>
                        <button className="px-8 py-3 border border-gray-200 rounded-full hover:bg-gray-50 transition-colors">
                            查看演示
                        </button>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-20 px-6 md:px-12 bg-gray-50">
                <div className="max-w-6xl mx-auto">
                    <h2 className="text-3xl font-light mb-16 text-center">
                        产品特点
                    </h2>
                    <div className="grid md:grid-cols-3 gap-12">
                        <div className="flex flex-col items-center text-center">
                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-6">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                </svg>
                            </div>
                            <h3 className="text-xl mb-3">简约设计</h3>
                            <p className="text-gray-600">专注于核心功能，去除冗余元素，让产品更加直观易用。</p>
                        </div>
                        <div className="flex flex-col items-center text-center">
                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-6">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl mb-3">响应式体验</h3>
                            <p className="text-gray-600">完美适配各种设备，无论是手机、平板还是电脑，都能提供一致的体验。</p>
                        </div>
                        <div className="flex flex-col items-center text-center">
                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-6">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <h3 className="text-xl mb-3">高效性能</h3>
                            <p className="text-gray-600">优化代码结构和资源加载，确保产品运行流畅，响应迅速。</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Showcase Section */}
            <section id="showcase" className="py-20 px-6 md:px-12">
                <div className="max-w-6xl mx-auto">
                    <h2 className="text-3xl font-light mb-16 text-center">产品展示</h2>
                    <div className="grid md:grid-cols-2 gap-8">
                        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                            <p className="text-gray-400">产品图片 1</p>
                        </div>
                        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                            <p className="text-gray-400">产品图片 2</p>
                        </div>
                        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                            <p className="text-gray-400">产品图片 3</p>
                        </div>
                        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                            <p className="text-gray-400">产品图片 4</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Contact Section */}
            <section id="contact" className="py-20 px-6 md:px-12" data-oid="ev8y4ox">
                <div className="max-w-3xl mx-auto text-center" data-oid="0zwkmun">
                    <h2 className="text-3xl font-light mb-8" data-oid="w67gdqw">
                        联系我们
                    </h2>
                    <p className="text-gray-600 mb-12" data-oid="fiiltln">
                        如果您对我们的产品感兴趣，或者有任何问题和建议，欢迎随时联系我们。我们期待与您交流！
                    </p>
                    <div
                        className="flex flex-col sm:flex-row justify-center gap-4"
                        data-oid="p1-m.a0"
                    >
                        <input
                            type="email"
                            placeholder="您的邮箱"
                            className="px-6 py-3 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-gray-200"
                            data-oid="hpl6s4i"
                        />

                        <button
                            className="px-8 py-3 bg-black text-white rounded-full hover:bg-gray-800 transition-colors"
                            data-oid="xy:zna5"
                        >
                            发送消息
                        </button>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 md:px-12 border-t border-gray-100" data-oid=".sy0lxe">
                <div
                    className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center"
                    data-oid="-bknjul"
                >
                    <div
                        className="text-xl font-medium tracking-tight mb-6 md:mb-0"
                        data-oid="ok39mn1"
                    >
                        <span className="text-black" data-oid="mnqvm:r">
                            Trey
                        </span>
                    </div>
                    <div className="flex space-x-8 text-sm text-gray-500" data-oid="sg_m8vt">
                        <Link
                            href="/notion"
                            className="hover:text-black transition-colors"
                            data-oid="78:hdpk"
                        >
                            Notion
                        </Link>
                        <Link
                            href="/weread"
                            className="hover:text-black transition-colors"
                            data-oid=":iwo280"
                        >
                            微信读书
                        </Link>
                    </div>
                    <div className="mt-6 md:mt-0 text-sm text-gray-400" data-oid="ut8j1l9">
                        © 2025 Trey. 保留所有权利。
                    </div>
                </div>
            </footer>
        </div>
    );
}
