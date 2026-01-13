import React from 'react';
import { Table, Tag, Space } from 'antd';
import { Link } from 'react-router-dom';

const columns = [
  {
    title: '任务ID',
    dataIndex: 'task_id',
    key: 'task_id',
  },
  {
    title: '策略',
    dataIndex: 'strategy',
    key: 'strategy',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    render: (status: string) => {
        let color = status === 'completed' ? 'green' : 'geekblue';
        if (status === 'failed') color = 'volcano';
        return (
            <Tag color={color} key={status}>
                {status.toUpperCase()}
            </Tag>
        );
    }
  },
  {
    title: '总收益',
    dataIndex: 'return',
    key: 'return',
    render: (text: number) => <span style={{ color: text >= 0 ? 'red' : 'green' }}>{text}%</span>
  },
  {
    title: '提交时间',
    dataIndex: 'created_at',
    key: 'created_at',
  },
  {
    title: '操作',
    key: 'action',
    render: (_: any, record: any) => (
      <Space size="middle">
        <Link to={`/backtest/result/${record.task_id}`}>查看报告</Link>
      </Space>
    ),
  },
];

const data = [
  {
    key: '1',
    task_id: 'TASK-001',
    strategy: '网格交易',
    status: 'completed',
    return: 12.5,
    created_at: '2023-10-24 10:00:00',
  },
  {
    key: '2',
    task_id: 'TASK-002',
    strategy: '定投增强',
    status: 'running',
    return: 0,
    created_at: '2023-10-24 11:00:00',
  },
];

const History: React.FC = () => <Table columns={columns} dataSource={data} />;

export default History;
