'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { post } from '@/app/utils/httpClient';
import { authService } from '@/app/services/authService';
import Navigation from '@/app/components/Navigation';

export default function NotionPage() {
    const [formData, setFormData] = useState({
        token: '',
        databaseId: '',
        activationCode: '',
        setCovers: false,
        setIcons: false,
        overwriteCovers: false,
        overwriteIcons: false,
    });
    const [notification, setNotification] = useState({
        show: false,
        message: '',
        type: 'success',
    });
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // 检查用户登录状态
    useEffect(() => {
        setIsLoggedIn(authService.isLoggedIn());
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // 确保 URL 路径与 API 路由文件的位置匹配
            const response = await fetch('/api/notion-setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: formData.token,
                    database_id: formData.databaseId,
                    ...(formData.activationCode ? { activation_code: formData.activationCode } : {}),
                    set_covers: formData.setCovers,
                    set_icons: formData.setIcons,
                    overwrite_covers: formData.overwriteCovers,
                    overwrite_icons: formData.overwriteIcons,
                }),
            });
            
            console.log(response);
            // 检查响应状态
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setResult(data);

            if (data.success) {
                setNotification({
                    show: true,
                    message: `设置成功！处理了 ${data.pages_processed} 页面，更新了 ${data.covers_updated} 个封面和 ${data.icons_updated} 个图标。`,
                    type: 'success',
                });
            } else {
                throw new Error(data.error || (data.errors && data.errors.join(', ')) || '设置失败');
            }

            // Hide notification after 5 seconds
            setTimeout(() => {
                setNotification((prev) => ({ ...prev, show: false }));
            }, 5000);
        } catch (err: any) {
            setError(err.message || 'An error occurred');
            console.error('Error:', err);

            setNotification({
                show: true,
                message: '设置失败，请检查您的输入并重试。',
                type: 'error',
            });

            setTimeout(() => {
                setNotification((prev) => ({ ...prev, show: false }));
            }, 5000);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white text-gray-800 font-sans">
            <Navigation />
            
            <section className="pt-32 pb-16 px-6 md:px-12 bg-gray-50">
                <div className="max-w-4xl mx-auto" data-oid="c7ijsj0">
                    <h1
                        className="text-3xl md:text-5xl font-light leading-tight mb-6"
                        data-oid="pqvaifl"
                    >
                        Notion 集成服务
                    </h1>
                    <p className="text-lg text-gray-600 max-w-2xl mb-8" data-oid="i8jne7-">
                        通过我们的服务，轻松将 Notion
                        数据库与您的应用程序集成，实现自动化工作流程和数据同步。
                    </p>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-16 px-6 md:px-12" data-oid="fzc4g..">
                <div className="max-w-4xl mx-auto" data-oid="zmw.69.">
                    <h2 className="text-2xl font-light mb-8" data-oid="le_72w-">
                        Notion 集成功能
                    </h2>

                    <div className="grid md:grid-cols-2 gap-8 mb-12" data-oid="l0zoot.">
                        <div className="bg-gray-50 p-6 rounded-lg" data-oid="ciw-re8">
                            <h3 className="text-xl mb-3" data-oid="705uq:b">
                                数据同步
                            </h3>
                            <p className="text-gray-600" data-oid="vxvakk7">
                                自动同步 Notion 数据库与您的应用程序，确保信息始终保持最新状态。
                            </p>
                        </div>
                        <div className="bg-gray-50 p-6 rounded-lg" data-oid="fteq6wj">
                            <h3 className="text-xl mb-3" data-oid="i97cx7r">
                                自动化工作流
                            </h3>
                            <p className="text-gray-600" data-oid="qfjb72e">
                                设置触发器和操作，实现工作流程自动化，提高工作效率。
                            </p>
                        </div>
                        <div className="bg-gray-50 p-6 rounded-lg" data-oid="6v_kw49">
                            <h3 className="text-xl mb-3" data-oid="y6:fp57">
                                数据分析
                            </h3>
                            <p className="text-gray-600" data-oid="22_br-a">
                                从 Notion 数据库中提取有价值的见解，帮助您做出更明智的决策。
                            </p>
                        </div>
                        <div className="bg-gray-50 p-6 rounded-lg" data-oid="-227q3f">
                            <h3 className="text-xl mb-3" data-oid="vp_r426">
                                自定义集成
                            </h3>
                            <p className="text-gray-600" data-oid="v0wuvz:">
                                根据您的特定需求定制集成方案，满足您的业务需求。
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Setup Form Section */}
            <section className="py-16 px-6 md:px-12 bg-gray-50" data-oid="_nlmjn7">
                <div className="max-w-3xl mx-auto" data-oid="uvvp1jq">
                    <h2 className="text-2xl font-light mb-8 text-center" data-oid="x_xj9be">
                        设置您的 Notion 集成
                    </h2>
                    <p className="text-gray-600 mb-8 text-center" data-oid=".l0mff3">
                        请填写以下信息以设置您的 Notion 集成。您可以在 Notion 开发者页面找到 API Key
                        和 Database ID。
                    </p>

                    <form
                        onSubmit={handleSubmit}
                        className="bg-white p-8 rounded-lg shadow-sm"
                        data-oid=".oleol7"
                    >
                        <div className="mb-6" data-oid="f55gwpf">
                            <label
                                htmlFor="token"
                                className="block text-sm font-medium text-gray-700 mb-2"
                                data-oid="-w6etwi"
                            >
                                Notion API Token
                            </label>
                            <input
                                type="text"
                                id="token"
                                name="token"
                                value={formData.token}
                                onChange={handleChange}
                                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200"
                                placeholder="secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                required
                                data-oid="03yv9ex"
                            />

                            <p className="mt-1 text-xs text-gray-500" data-oid="3o5m:si">
                                在 Notion 开发者页面创建集成后获取
                            </p>
                        </div>

                        <div className="mb-6" data-oid="9gfw5w-">
                            <label
                                htmlFor="databaseId"
                                className="block text-sm font-medium text-gray-700 mb-2"
                                data-oid=".xqbgqo"
                            >
                                Notion Database ID
                            </label>
                            <input
                                type="text"
                                id="databaseId"
                                name="databaseId"
                                value={formData.databaseId}
                                onChange={handleChange}
                                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200"
                                placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                required
                                data-oid="bjm5s05"
                            />

                            <p className="mt-1 text-xs text-gray-500" data-oid="xu97cj:">
                                从 Notion 数据库 URL 中获取
                            </p>
                        </div>

                        <div className="mb-8" data-oid="_hhk10s">
                            <label
                                htmlFor="activationCode"
                                className="block text-sm font-medium text-gray-700 mb-2"
                                data-oid="y9120:e"
                            >
                                激活码
                            </label>
                            <input
                                type="text"
                                id="activationCode"
                                name="activationCode"
                                value={formData.activationCode}
                                onChange={handleChange}
                                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200"
                                placeholder="XXXX-XXXX-XXXX-XXXX"
                                required
                                data-oid="kfh0h20"
                            />

                            <p className="mt-1 text-xs text-gray-500" data-oid="xonzej.">
                                输入您购买的激活码以启用服务
                            </p>
                        </div>

                        <div className="mb-8 space-y-4" data-oid="de3.4fz">
                            <div className="flex items-center" data-oid=".137bdq">
                                <input
                                    type="checkbox"
                                    id="setCovers"
                                    name="setCovers"
                                    checked={formData.setCovers}
                                    onChange={handleChange}
                                    className="h-4 w-4 text-black rounded border-gray-300 focus:ring-gray-500"
                                    data-oid="7u7-gm2"
                                />

                                <label
                                    htmlFor="setCovers"
                                    className="ml-2 text-sm text-gray-700"
                                    data-oid="fsnwj4-"
                                >
                                    设置页面封面
                                </label>
                            </div>

                            <div className="flex items-center" data-oid="szrclsb">
                                <input
                                    type="checkbox"
                                    id="setIcons"
                                    name="setIcons"
                                    checked={formData.setIcons}
                                    onChange={handleChange}
                                    className="h-4 w-4 text-black rounded border-gray-300 focus:ring-gray-500"
                                    data-oid="opp4p3-"
                                />

                                <label
                                    htmlFor="setIcons"
                                    className="ml-2 text-sm text-gray-700"
                                    data-oid="egm6s9-"
                                >
                                    设置页面图标
                                </label>
                            </div>

                            <div className="flex items-center" data-oid="c5j_1d.">
                                <input
                                    type="checkbox"
                                    id="overwriteCovers"
                                    name="overwriteCovers"
                                    checked={formData.overwriteCovers}
                                    onChange={handleChange}
                                    className="h-4 w-4 text-black rounded border-gray-300 focus:ring-gray-500"
                                    data-oid="snz:8.9"
                                />

                                <label
                                    htmlFor="overwriteCovers"
                                    className="ml-2 text-sm text-gray-700"
                                    data-oid="ss8evqb"
                                >
                                    覆盖现有封面
                                </label>
                            </div>

                            <div className="flex items-center" data-oid="q166r8g">
                                <input
                                    type="checkbox"
                                    id="overwriteIcons"
                                    name="overwriteIcons"
                                    checked={formData.overwriteIcons}
                                    onChange={handleChange}
                                    className="h-4 w-4 text-black rounded border-gray-300 focus:ring-gray-500"
                                    data-oid="8pu0rod"
                                />

                                <label
                                    htmlFor="overwriteIcons"
                                    className="ml-2 text-sm text-gray-700"
                                    data-oid="u7n-8u5"
                                >
                                    覆盖现有图标
                                </label>
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="w-full px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
                            data-oid="ff5mjga"
                            disabled={loading}
                        >
                            {loading ? 'Processing...' : 'Submit'}
                        </button>
                    </form>
                </div>
            </section>

            {/* Notification */}
            {notification.show && (
                <div
                    className={`fixed bottom-6 right-6 px-6 py-4 rounded-lg shadow-lg ${
                        notification.type === 'success'
                            ? 'bg-green-50 text-green-800'
                            : 'bg-red-50 text-red-800'
                    }`}
                    data-oid="5:jgzj2"
                >
                    <div className="flex items-center" data-oid="63je76e">
                        {notification.type === 'success' ? (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5 mr-2"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                                data-oid="las3qon"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                    data-oid=":ma77se"
                                />
                            </svg>
                        ) : (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5 mr-2"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                                data-oid="vbg0dm6"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                                    clipRule="evenodd"
                                    data-oid="zv1d4j0"
                                />
                            </svg>
                        )}
                        {notification.message}
                    </div>
                </div>
            )}

            {/* Result */}
            {result && (
                <div className="container mx-auto p-4" data-oid=":7jq4.u">
                    <h1 className="text-2xl font-bold mb-4" data-oid="mblmown">
                        API Integration
                    </h1>

                    {error && (
                        <div
                            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
                            data-oid="sxq-pvv"
                        >
                            {error}
                        </div>
                    )}

                    {result && (
                        <div
                            className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded"
                            data-oid="qqbg7zh"
                        >
                            <pre data-oid="y_.7df0">{JSON.stringify(result, null, 2)}</pre>
                        </div>
                    )}
                </div>
            )}

            {/* Footer */}
            <footer className="py-12 px-6 md:px-12 border-t border-gray-100" data-oid="qknc4:o">
                <div
                    className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center"
                    data-oid="6nfimfs"
                >
                    <div
                        className="text-xl font-medium tracking-tight mb-6 md:mb-0"
                        data-oid="4.f-ktt"
                    >
                        <span className="text-black" data-oid="ufkso_-">
                            Trey
                        </span>
                    </div>
                    <div className="flex space-x-8 text-sm text-gray-500" data-oid="-4-x_iu">
                        <Link
                            href="/#blog"
                            className="hover:text-black transition-colors"
                            data-oid="un:vktr"
                        >
                            Blog
                        </Link>
                        <Link
                            href="/notion"
                            className="text-black font-medium transition-colors"
                            data-oid="m41lqwp"
                        >
                            Notion
                        </Link>
                        <Link
                            href="/#product2"
                            className="hover:text-black transition-colors"
                            data-oid="jftqgbx"
                        >
                            产品位2
                        </Link>
                        <Link
                            href="/#about"
                            className="hover:text-black transition-colors"
                            data-oid="bwg26_d"
                        >
                            关于我
                        </Link>
                    </div>
                    <div className="mt-6 md:mt-0 text-sm text-gray-400" data-oid="cwldnwc">
                        © 2023 Trey. 保留所有权利。
                    </div>
                </div>
            </footer>
        </div>
    );
}
