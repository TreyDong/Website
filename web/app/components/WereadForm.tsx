'use client';

import React, { useState, useEffect } from 'react';
import { Button } from 'antd';
import { message } from 'antd';

export default function WereadForm() {
    const [mode, setMode] = useState<'qr' | 'manual'>('qr');
    const [formData, setFormData] = useState({
        authCode: '',
        headers: '',
        cookies: '',
        readTimeMinutes: 30,
        scheduleTime: '00:00',
        bashRequest: '',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [qrCode, setQrCode] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [showQRCode, setShowQRCode] = useState(false);
    const [isConfirming, setIsConfirming] = useState(false);
    const [isQrCodeLoading, setIsQrCodeLoading] = useState(false);
    const [isPolling, setIsPolling] = useState(false);
    const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
    const [loginStatus, setLoginStatus] = useState<string>('');
    const [loginError, setLoginError] = useState<string | null>(null);

    const startQRLogin = async () => {
        try {
            setIsQrCodeLoading(true);
            setLoginError(null);
            setLoginStatus('正在获取二维码...');
            
            const response = await fetch('http://localhost:5000/api/config/qrcode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (data.success) {
                setQrCode(data.qrcode);
                setSessionId(data.session_id);
                setLoginStatus('请扫描二维码登录');
                
                startPollingLoginStatus(data.session_id);
            } else {
                setLoginError(data.error || '获取二维码失败');
                setLoginStatus('');
            }
        } catch (error) {
            console.error('Error fetching QR code:', error);
            setLoginError('获取二维码失败，请重试');
            setLoginStatus('');
        } finally {
            setIsQrCodeLoading(false);
        }
    };

    const startPollingLoginStatus = (sid: string) => {
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
        
        setIsPolling(true);
        
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`http://localhost:5000/api/config/qrcode/status/${sid}`);
                const data = await response.json();
                
                if (data.success) {
                    setLoginStatus(data.message || '');
                    
                    if (data.status === 'completed') {
                        setFormData(prev => ({
                            ...prev,
                            headers: data.headers,
                            cookies: data.cookies,
                        }));
                        
                        clearInterval(interval);
                        setPollingInterval(null);
                        setIsPolling(false);
                        
                        message.success('登录成功！');
                    } else if (data.status === 'error' || data.status === 'timeout' || data.status === 'cancelled') {
                        clearInterval(interval);
                        setPollingInterval(null);
                        setIsPolling(false);
                        setLoginError(data.error || '登录失败');
                        setLoginStatus('');
                    }
                } else {
                    clearInterval(interval);
                    setPollingInterval(null);
                    setIsPolling(false);
                    setLoginError(data.error || '检查登录状态失败');
                    setLoginStatus('');
                }
            } catch (error) {
                console.error('Error polling login status:', error);
                clearInterval(interval);
                setPollingInterval(null);
                setIsPolling(false);
                setLoginError('检查登录状态失败，请重试');
                setLoginStatus('');
            }
        }, 3000);
        
        setPollingInterval(interval);
    };

    const cancelQRLogin = async () => {
        if (sessionId) {
            try {
                await fetch(`http://localhost:5000/api/config/qrcode/cancel/${sessionId}`, {
                    method: 'POST',
                });
            } catch (error) {
                console.error('Error cancelling QR login:', error);
            }
        }
        
        if (pollingInterval) {
            clearInterval(pollingInterval);
            setPollingInterval(null);
        }
        
        setIsPolling(false);
        setLoginStatus('');
        setLoginError(null);
    };

    useEffect(() => {
        return () => {
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
        };
    }, [pollingInterval]);

    const resetForm = () => {
        setFormData({
            authCode: '',
            readTimeMinutes: 30,
            scheduleTime: '08:00',
            headers: '',
            cookies: '',
            bashRequest: '',
        });
        setQrCode(null);
        setSessionId(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!formData.authCode) {
            message.error('请输入授权码');
            return;
        }
        
        if (!formData.readTimeMinutes) {
            message.error('请输入阅读时间');
            return;
        }
        
        if (!formData.scheduleTime) {
            message.error('请选择执行时间');
            return;
        }
        
        if (!formData.headers || !formData.cookies) {
            message.error('请先完成微信读书登录');
            return;
        }
        
        setIsLoading(true);
        
        try {
            const response = await fetch('http://localhost:5000/api/setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    authCode: formData.authCode,
                    readTimeMinutes: formData.readTimeMinutes,
                    scheduleTime: formData.scheduleTime,
                    headers: formData.headers,
                    cookies: formData.cookies,
                    session_id: sessionId,
                }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                message.success('设置成功！');
                resetForm();
            } else {
                message.error(data.error || '设置失败，请重试');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            message.error('提交失败，请重试');
        } finally {
            setIsLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleBashRequestChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const bashRequest = e.target.value;
        setFormData(prev => ({ ...prev, bashRequest }));
        
        try {
            const headersMatch = bashRequest.match(/headers: ({[\s\S]*?})/);
            const cookiesMatch = bashRequest.match(/cookies: ({[\s\S]*?})/);
            
            if (headersMatch) {
                setFormData(prev => ({ ...prev, headers: headersMatch[1] }));
            }
            if (cookiesMatch) {
                setFormData(prev => ({ ...prev, cookies: cookiesMatch[1] }));
            }
        } catch (error) {
            console.error('Error parsing bash request:', error);
        }
    };

    return (
        <div className="bg-white p-8 rounded-lg shadow-sm">
            <h2 className="text-2xl font-bold mb-6">微信读书自动签到设置</h2>
            
            <div className="mb-6">
                <div className="flex space-x-4">
                    <button
                        type="button"
                        onClick={() => setMode('qr')}
                        className={`px-4 py-2 rounded-lg ${
                            mode === 'qr' ? 'bg-black text-white' : 'bg-gray-100 text-gray-700'
                        }`}
                    >
                        二维码模式
                    </button>
                    <button
                        type="button"
                        onClick={() => setMode('manual')}
                        className={`px-4 py-2 rounded-lg ${
                            mode === 'manual' ? 'bg-black text-white' : 'bg-gray-100 text-gray-700'
                        }`}
                    >
                        手工模式
                    </button>
                    <a
                        href="https://docs.qq.com/doc/DS1R0V1J0V1J0V1J0"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 text-blue-600 hover:text-blue-800"
                    >
                        帮助文档
                    </a>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="mb-6">
                    <label
                        htmlFor="authCode"
                        className="block text-sm font-medium text-gray-700 mb-2"
                    >
                        授权码
                    </label>
                    <input
                        type="text"
                        id="authCode"
                        name="authCode"
                        value={formData.authCode}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200"
                        placeholder="请输入您的授权码"
                        required
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        输入您购买的授权码以启用服务
                    </p>
                </div>

                {mode === 'qr' ? (
                    <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium text-gray-700">微信读书登录</label>
                            <div className="flex space-x-2">
                                <Button 
                                    onClick={startQRLogin} 
                                    loading={isQrCodeLoading}
                                    disabled={isQrCodeLoading || isPolling}
                                >
                                    获取二维码
                                </Button>
                                {isPolling && (
                                    <Button 
                                        onClick={cancelQRLogin}
                                        danger
                                    >
                                        取消登录
                                    </Button>
                                )}
                            </div>
                        </div>
                        
                        {loginError && (
                            <div className="mb-2 text-red-500 text-sm">
                                {loginError}
                            </div>
                        )}
                        
                        {loginStatus && (
                            <div className="mb-2 text-blue-500 text-sm">
                                {loginStatus}
                            </div>
                        )}
                        
                        {qrCode && (
                            <div className="flex justify-center">
                                <img 
                                    src={qrCode} 
                                    alt="微信读书登录二维码" 
                                    className="border border-gray-300 rounded-md p-2"
                                />
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="mb-6">
                        <label
                            htmlFor="bashRequest"
                            className="block text-sm font-medium text-gray-700 mb-2"
                        >
                            Bash请求
                        </label>
                        <textarea
                            id="bashRequest"
                            name="bashRequest"
                            value={formData.bashRequest}
                            onChange={handleBashRequestChange}
                            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200"
                            placeholder="请粘贴完整的bash请求内容"
                            rows={6}
                            required
                        />
                        <p className="mt-1 text-xs text-gray-500">
                            从微信读书网页版复制完整的bash请求内容
                        </p>
                    </div>
                )}

                <div className="mb-6">
                    <label
                        htmlFor="readTimeMinutes"
                        className="block text-sm font-medium text-gray-700 mb-2"
                    >
                        阅读时间（分钟）
                    </label>
                    <input
                        type="number"
                        id="readTimeMinutes"
                        name="readTimeMinutes"
                        value={formData.readTimeMinutes}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200"
                        min="1"
                        max="1440"
                        required
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        设置每日阅读时间，建议设置合理的时长（1-120分钟）
                    </p>
                </div>

                <div className="mb-8">
                    <label
                        htmlFor="scheduleTime"
                        className="block text-sm font-medium text-gray-700 mb-2"
                    >
                        定时时间
                    </label>
                    <input
                        type="time"
                        id="scheduleTime"
                        name="scheduleTime"
                        value={formData.scheduleTime}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200"
                        required
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        设置每日自动签到的时间（24小时制）
                    </p>
                </div>

                <button
                    type="submit"
                    className="w-full px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={isLoading}
                >
                    {isLoading ? '提交中...' : '提交设置'}
                </button>
            </form>
        </div>
    );
} 