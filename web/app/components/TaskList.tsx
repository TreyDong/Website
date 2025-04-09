'use client';

import React, { useState, useEffect } from 'react';
import { Button, Table, Input, Space, Tag, message } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';

interface Task {
    job_id: string;
    auth_code: string;
    next_run_time: string;
    cron_expression: string;
    is_active: boolean;
    reading_time_minutes: number;
    created_at: string;
    last_validated_at: string;
}

export default function TaskList() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchAuthCode, setSearchAuthCode] = useState('');
    const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);

    // 加载任务列表
    const fetchTasks = async (authCode?: string) => {
        try {
            setLoading(true);
            const url = authCode 
                ? `${process.env.NEXT_PUBLIC_API_URL}/api/tasks?auth_code=${authCode}`
                : `${process.env.NEXT_PUBLIC_API_URL}/api/tasks`;
                
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                setTasks(data.tasks);
                setFilteredTasks(data.tasks);
            } else {
                message.error(data.error || '获取任务列表失败');
            }
        } catch (error) {
            console.error('获取任务列表出错:', error);
            message.error('获取任务列表出错，请稍后重试');
        } finally {
            setLoading(false);
        }
    };

    // 组件加载时获取任务列表
    useEffect(() => {
        // fetchTasks();
    }, []);

    // 处理搜索
    const handleSearch = () => {
        if (searchAuthCode.trim()) {
            fetchTasks(searchAuthCode.trim());
        } else {
            fetchTasks();
        }
    };

    // 处理刷新
    const handleRefresh = () => {
        fetchTasks();
    };

    // 表格列定义
    const columns = [
        {
            title: '授权码',
            dataIndex: 'auth_code',
            key: 'auth_code',
        },
        {
            title: '下次运行时间',
            dataIndex: 'next_run_time',
            key: 'next_run_time',
        },
        {
            title: 'Cron表达式',
            dataIndex: 'cron_expression',
            key: 'cron_expression',
        },
        {
            title: '阅读时间(分钟)',
            dataIndex: 'reading_time_minutes',
            key: 'reading_time_minutes',
        },
        {
            title: '状态',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (isActive: boolean) => (
                <Tag color={isActive ? 'green' : 'red'}>
                    {isActive ? '活跃' : '未激活'}
                </Tag>
            ),
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
        },
        {
            title: '最后验证时间',
            dataIndex: 'last_validated_at',
            key: 'last_validated_at',
        },
    ];

    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">定时任务列表</h2>
                <Space>
                    <Input
                        placeholder="输入授权码搜索"
                        value={searchAuthCode}
                        onChange={(e) => setSearchAuthCode(e.target.value)}
                        style={{ width: 200 }}
                    />
                    <Button 
                        type="primary" 
                        icon={<SearchOutlined />} 
                        onClick={handleSearch}
                    >
                        搜索
                    </Button>
                    <Button 
                        icon={<ReloadOutlined />} 
                        onClick={handleRefresh}
                    >
                        刷新
                    </Button>
                </Space>
            </div>
            
            <Table
                dataSource={filteredTasks}
                columns={columns}
                rowKey="job_id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />
        </div>
    );
} 