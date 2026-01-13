import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, Col, Row, Statistic } from 'antd';
import { useParams } from 'react-router-dom';

const BacktestResult: React.FC = () => {
    const { id } = useParams();

    const option = {
        title: {
            text: '策略收益曲线'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['策略收益', '基准收益']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', '2023-07']
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                name: '策略收益',
                type: 'line',
                data: [0, 5, 3, 8, 12, 15, 18],
                smooth: true,
                areaStyle: {
                    opacity: 0.3
                }
            },
            {
                name: '基准收益',
                type: 'line',
                data: [0, 2, 4, 3, 5, 7, 8],
                smooth: true,
                lineStyle: {
                    type: 'dashed'
                }
            }
        ]
    };

    return (
        <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                    <Card>
                        <Statistic title="年化收益" value={15.3} suffix="%" precision={2} valueStyle={{ color: '#cf1322' }} />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic title="最大回撤" value={5.4} suffix="%" precision={2} valueStyle={{ color: '#3f8600' }} />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic title="夏普比率" value={1.8} precision={2} />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic title="交易次数" value={24} />
                    </Card>
                </Col>
            </Row>
            <Card title={`回测结果详情 (ID: ${id || 'Demo'})`}>
                <ReactECharts option={option} style={{ height: 400 }} />
            </Card>
        </div>
    );
};

export default BacktestResult;
