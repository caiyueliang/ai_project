import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Tag, 
  Space, 
  Button, 
  Input, 
  Select, 
  Card, 
  Drawer, 
  message, 
  Descriptions,
  Statistic,
  Row,
  Col,
  Modal,
  InputNumber
} from 'antd';
import { SyncOutlined, ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import ReactECharts from 'echarts-for-react';
import { getFunds, getFundDetail, syncFunds } from '../services/api';
import { cacheGet, cacheSet } from '../utils/cache';

const { Option } = Select;

interface FundData {
  id: number;
  code: string;
  name: string;
  fund_type: string;
  created_at?: string;
  nav?: number;
  nav_date?: string;
  daily_change_pct?: number;
}

interface FundDetail extends FundData {
  navs: {
    nav_date: string;
    nav: number;
    accumulated_nav: number;
  }[];
}

const Funds: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<FundData[]>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({
    page: 1,
    pageSize: 10,
    type: undefined as string | undefined,
    search: undefined as string | undefined,
    sortBy: undefined as string | undefined,
    sortOrder: 'desc' as 'asc' | 'desc',
  });

  const [detailVisible, setDetailVisible] = useState(false);
  const [currentFund, setCurrentFund] = useState<FundDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncModalOpen, setSyncModalOpen] = useState(false);
  const [syncDays, setSyncDays] = useState<number>(30);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (filters.page - 1) * filters.pageSize,
        limit: filters.pageSize,
        type: filters.type,
        search: filters.search,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };

      const cacheKey = `funds:list:${JSON.stringify(params)}`;
      const cached = cacheGet<{ total: number; items: FundData[] }>(cacheKey);
      if (cached) {
        setData(cached.items);
        setTotal(cached.total);
        return;
      }

      const res = await getFunds(params);
      setData(res?.items || []);
      setTotal(res?.total || 0);
      cacheSet(cacheKey, { total: res?.total || 0, items: res?.items || [] }, 30_000);
    } catch (error) {
      message.error('获取基金列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const handleSearch = (value: string) => {
    setFilters({ ...filters, search: value, page: 1 });
  };

  const handleTypeChange = (value: string | undefined) => {
    setFilters({ ...filters, type: value, page: 1 });
  };

  const handleTableChange = (pagination: any, _tableFilters: any, sorter: any) => {
    const next: any = { ...filters, page: pagination.current, pageSize: pagination.pageSize };
    if (sorter?.field) {
      next.sortBy = sorter.field;
      next.sortOrder = sorter.order === 'ascend' ? 'asc' : 'desc';
    } else {
      next.sortBy = undefined;
      next.sortOrder = 'desc';
    }
    setFilters(next);
  };

  const showDetail = async (code: string) => {
    setDetailVisible(true);
    setDetailLoading(true);
    try {
      const cacheKey = `funds:detail:${code}`;
      const cached = cacheGet<FundDetail>(cacheKey);
      if (cached) {
        setCurrentFund(cached);
        return;
      }
      const res = await getFundDetail(code);
      setCurrentFund(res as any);
      cacheSet(cacheKey, res as any, 60_000);
    } catch (error) {
      message.error('获取基金详情失败');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSync = async (days: number) => {
    setSyncLoading(true);
    try {
      const res = await syncFunds(days);
      message.success(`同步完成，新增 ${res?.inserted ?? 0} 条净值记录`);
      setSyncModalOpen(false);
      fetchData();
    } catch (error) {
      message.error('同步失败');
    } finally {
      setSyncLoading(false);
    }
  };

  const columns: ColumnsType<FundData> = [
    {
      title: '基金代码',
      dataIndex: 'code',
      key: 'code',
      render: (text) => <a onClick={() => showDetail(text)}>{text}</a>,
    },
    {
      title: '基金名称',
      dataIndex: 'name',
      key: 'name',
      sorter: true,
    },
    {
      title: '最新净值',
      dataIndex: 'nav',
      key: 'nav',
      sorter: true,
      render: (v?: number) => (typeof v === 'number' ? v.toFixed(4) : '-'),
    },
    {
      title: '净值日期',
      dataIndex: 'nav_date',
      key: 'nav_date',
      render: (v?: string) => v || '-',
    },
    {
      title: '日涨跌幅',
      dataIndex: 'daily_change_pct',
      key: 'daily_change_pct',
      sorter: true,
      render: (v?: number) => {
        if (typeof v !== 'number') return '-';
        const color = v >= 0 ? '#cf1322' : '#389e0d';
        const prefix = v >= 0 ? '+' : '';
        return <span style={{ color }}>{prefix}{v.toFixed(2)}%</span>;
      },
    },
    {
      title: '类型',
      dataIndex: 'fund_type',
      key: 'fund_type',
      render: (type) => (
        <Tag color={type === '混合型' ? 'blue' : type === '股票型' ? 'red' : 'green'}>
          {type || '未知'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <a onClick={() => showDetail(record.code)}>详情</a>
        </Space>
      ),
    },
  ];

  const getChartOption = () => {
    if (!currentFund || !currentFund.navs) return {};
    
    const sortedNavs = [...currentFund.navs].sort((a, b) => 
      new Date(a.nav_date).getTime() - new Date(b.nav_date).getTime()
    );

    return {
      title: {
        text: '历史净值走势'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: sortedNavs.map(item => item.nav_date)
      },
      yAxis: {
        type: 'value',
        scale: true
      },
      series: [
        {
          name: '单位净值',
          type: 'line',
          data: sortedNavs.map(item => item.nav),
          smooth: true,
          areaStyle: {
            opacity: 0.1
          }
        }
      ]
    };
  };

  return (
    <div style={{ padding: 24 }}>
      <Card bordered={false}>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <Space>
            <Input.Search
              placeholder="搜索基金代码/名称"
              onSearch={handleSearch}
              style={{ width: 200 }}
              allowClear
            />
            <Select
              placeholder="基金类型"
              style={{ width: 120 }}
              allowClear
              onChange={handleTypeChange}
            >
              <Option value="混合型">混合型</Option>
              <Option value="股票型">股票型</Option>
              <Option value="债券型">债券型</Option>
              <Option value="指数型">指数型</Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={fetchData}>刷新</Button>
          </Space>
          <Button 
            type="primary" 
            icon={<SyncOutlined />} 
            loading={syncLoading}
            onClick={() => setSyncModalOpen(true)}
          >
            同步最近数据
          </Button>
        </div>
        
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            current: filters.page,
            pageSize: filters.pageSize,
            total: total,
            showSizeChanger: true
          }}
          onChange={handleTableChange}
        />
      </Card>

      <Modal
        title="手动同步"
        open={syncModalOpen}
        okText="开始同步"
        cancelText="取消"
        confirmLoading={syncLoading}
        onOk={() => handleSync(syncDays)}
        onCancel={() => setSyncModalOpen(false)}
      >
        <Space>
          <span>同步最近</span>
          <InputNumber min={1} max={3650} value={syncDays} onChange={(v) => setSyncDays(v || 30)} />
          <span>天</span>
        </Space>
      </Modal>

      <Drawer
        title="基金详情"
        width={800}
        onClose={() => setDetailVisible(false)}
        open={detailVisible}
        destroyOnClose
      >
        {detailLoading ? (
          <div>加载中...</div>
        ) : currentFund ? (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Descriptions title="基本信息" bordered column={2}>
              <Descriptions.Item label="基金代码">{currentFund.code}</Descriptions.Item>
              <Descriptions.Item label="基金名称">{currentFund.name}</Descriptions.Item>
              <Descriptions.Item label="基金类型">{currentFund.fund_type}</Descriptions.Item>
              <Descriptions.Item label="成立时间">{currentFund.created_at}</Descriptions.Item>
            </Descriptions>

            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="最新净值"
                  value={currentFund.navs[currentFund.navs.length - 1]?.nav ?? '-'}
                  precision={4}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="累计净值"
                  value={currentFund.navs[currentFund.navs.length - 1]?.accumulated_nav ?? '-'}
                  precision={4}
                />
              </Col>
            </Row>

            <Card title="净值走势" bordered={false}>
              <ReactECharts option={getChartOption()} style={{ height: 400 }} />
            </Card>
          </Space>
        ) : (
          <div>暂无数据</div>
        )}
      </Drawer>
    </div>
  );
};

export default Funds;
