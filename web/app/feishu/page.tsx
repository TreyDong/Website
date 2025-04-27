'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { message } from 'antd';

const API_BASE_URL = 'http://localhost:5000'; // Update this to your backend server URL

export default function FeishuRegistration() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [orderId, setOrderId] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [templateUrl, setTemplateUrl] = useState('');
    const [authToken, setAuthToken] = useState('');

    const handleOrderIdSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/check-order`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ orderId }),
            });
            const data = await response.json();
            
            if (data.exists) {
                if (data.isConfigured) {
                    router.push(`/feishu/complete?orderId=${orderId}`);
                } else {
                    setStep(2);
                }
            } else {
                message.error('订单号不存在');
            }
        } catch (error) {
            message.error('检查订单号时出错');
        } finally {
            setIsLoading(false);
        }
    };

    const handlePhoneNumberSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/start-registration`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ orderId, phoneNumber }),
            });
            const data = await response.json();
            
            if (data.success) {
                setStep(3);
            } else {
                message.error('启动注册流程失败');
            }
        } catch (error) {
            message.error('启动注册流程时出错');
        } finally {
            setIsLoading(false);
        }
    };

    const handleVerificationCodeSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/complete-registration`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ orderId, verificationCode }),
            });
            const data = await response.json();
            
            if (data.success) {
                setTemplateUrl(data.templateUrl);
                setAuthToken(data.authToken);
                setStep(4);
            } else {
                message.error('验证码验证失败');
            }
        } catch (error) {
            message.error('完成注册流程时出错');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-md mx-auto">
                <h1 className="text-2xl font-bold text-center mb-8">飞书账号配置</h1>
                
                {step === 1 && (
                    <form onSubmit={handleOrderIdSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="orderId" className="block text-sm font-medium text-gray-700">
                                订单号
                            </label>
                            <input
                                type="text"
                                id="orderId"
                                value={orderId}
                                onChange={(e) => setOrderId(e.target.value)}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
                        >
                            {isLoading ? '检查中...' : '下一步'}
                        </button>
                    </form>
                )}

                {step === 2 && (
                    <form onSubmit={handlePhoneNumberSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700">
                                手机号码
                            </label>
                            <input
                                type="tel"
                                id="phoneNumber"
                                value={phoneNumber}
                                onChange={(e) => setPhoneNumber(e.target.value)}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
                        >
                            {isLoading ? '处理中...' : '下一步'}
                        </button>
                    </form>
                )}

                {step === 3 && (
                    <form onSubmit={handleVerificationCodeSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="verificationCode" className="block text-sm font-medium text-gray-700">
                                验证码
                            </label>
                            <input
                                type="text"
                                id="verificationCode"
                                value={verificationCode}
                                onChange={(e) => setVerificationCode(e.target.value)}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
                        >
                            {isLoading ? '验证中...' : '完成'}
                        </button>
                    </form>
                )}

                {step === 4 && (
                    <div className="space-y-4">
                        <div className="bg-white p-4 rounded-md shadow">
                            <h2 className="text-lg font-medium mb-2">配置完成</h2>
                            <p className="text-sm text-gray-600 mb-4">
                                您的飞书账号已成功配置。以下是相关信息：
                            </p>
                            <div className="space-y-2">
                                <div>
                                    <span className="font-medium">模板链接：</span>
                                    <a href={templateUrl} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 break-all">
                                        {templateUrl}
                                    </a>
                                </div>
                                <div>
                                    <span className="font-medium">授权码：</span>
                                    <span className="font-mono bg-gray-100 p-1 rounded">{authToken}</span>
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={() => router.push('/')}
                            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        >
                            返回首页
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
} 