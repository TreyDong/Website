'use client';

import Navigation from '@/app/components/Navigation';
import WereadForm from '@/app/components/WereadForm';
import TaskList from '@/app/components/TaskList';
import { Tabs } from 'antd';

export default function WereadPage() {
    return (
        <div className="min-h-screen bg-white text-gray-800 font-sans">
            <Navigation />
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 pt-24">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-12">
                        <h1 className="text-4xl font-bold mb-4">微信读书自动签到</h1>
                        <p className="text-lg text-gray-600">
                            设置您的微信读书账号，实现每日自动签到
                        </p>
                    </div>
                    
                    <Tabs
                        defaultActiveKey="1"
                        items={[
                            {
                                key: '1',
                                label: '添加新任务',
                                children: <WereadForm />,
                            },
                            {
                                key: '2',
                                label: '查看定时任务',
                                children: <TaskList />,
                            },
                        ]}
                        className="mb-8"
                    />
                </div>
            </div>
        </div>
    );
}