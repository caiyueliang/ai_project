import React from 'react';
import { Table, Tag, Space, Button } from 'antd';
import type { ColumnsType } from 'antd/es/table';

interface DataType {
  key: string;
  name: string;
  code: string;
  nav: number;
  date: string;
  type: string;
}

const columns: ColumnsType<DataType> = [
  {
    title: '基金代码',
    dataIndex: 'code',
    key: 'code',
    render: (text) => <a>{text}</a>,
  },
  {
    title: '基金名称',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '最新净值',
    dataIndex: 'nav',
    key: 'nav',
  },
  {
    title: '日期',
    dataIndex: 'date',
    key: 'date',
  },
  {
    title: '类型',
    key: 'type',
    dataIndex: 'type',
    render: (_, { type }) => (
      <>
        <Tag color={type === '混合型' ? 'geekblue' : 'green'} key={type}>
          {type}
        </Tag>
      </>
    ),
  },
  {
    title: '操作',
    key: 'action',
    render: (_, record) => (
      <Space size="middle">
        <a>查看详情</a>
        <a>同步数据</a>
      </Space>
    ),
  },
];

const data: DataType[] = [
  {
    key: '1',
    name: '华夏成长',
    code: '000001',
    nav: 1.2345,
    date: '2023-10-01',
    type: '混合型',
  },
  {
    key: '2',
    name: '华夏大盘精选',
    code: '000002',
    nav: 3.4567,
    date: '2023-10-01',
    type: '混合型',
  },
];

const Funds: React.FC = () => (
    <div>
        <div style={{ marginBottom: 16 }}>
            <Button type="primary">同步最近数据</Button>
        </div>
        <Table columns={columns} dataSource={data} />
    </div>
);

export default Funds;
