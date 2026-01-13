import React, { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  FundOutlined,
  PieChartOutlined,
  HistoryOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';

const { Header, Content, Footer, Sider } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
  } as MenuItem;
}

const items: MenuItem[] = [
  getItem('仪表盘', '/dashboard', <DashboardOutlined />),
  getItem('基金数据', '/funds', <FundOutlined />),
  getItem('回测配置', '/backtest', <PieChartOutlined />),
  getItem('历史记录', '/history', <HistoryOutlined />),
  getItem('用户管理', '/users', <UserOutlined />),
];

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)' }} />
        <Menu 
            theme="dark" 
            defaultSelectedKeys={[location.pathname]} 
            mode="inline" 
            items={items} 
            onClick={({ key }) => navigate(key.toString())}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }} />
        <Content style={{ margin: '0 16px' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
              marginTop: 16
            }}
          >
            <Outlet />
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          Fund Quant Platform ©{new Date().getFullYear()} Created by Trae AI
        </Footer>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
