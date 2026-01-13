import React from 'react';
import { Form, InputNumber, Button, DatePicker, Select, Card, message } from 'antd';
// import { runBacktest } from '../services/api';

const { RangePicker } = DatePicker;

const BacktestConfig: React.FC = () => {
    const [form] = Form.useForm();

    const onFinish = async (values: any) => {
        console.log('Success:', values);
        try {
            // const params = {
            //     fund_codes: values.fund_codes,
            //     start_date: values.date_range[0].format('YYYY-MM-DD'),
            //     end_date: values.date_range[1].format('YYYY-MM-DD'),
            //     strategy_params: {
            //         rise_ratio: values.rise_ratio,
            //         fall_ratio: values.fall_ratio,
            //         multiplier: values.multiplier
            //     }
            // };
            // await runBacktest(params);
            message.success('回测任务已提交');
        } catch (error) {
            message.error('提交失败');
        }
    };

    return (
        <Card title="策略回测配置">
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                initialValues={{
                    rise_ratio: 0.05,
                    fall_ratio: 0.05,
                    multiplier: 2
                }}
            >
                <Form.Item
                    label="选择基金"
                    name="fund_codes"
                    rules={[{ required: true, message: '请选择至少一只基金' }]}
                >
                    <Select
                        mode="multiple"
                        placeholder="请选择基金"
                        options={[
                            { label: '华夏成长 (000001)', value: '000001' },
                            { label: '华夏大盘 (000002)', value: '000002' },
                        ]}
                    />
                </Form.Item>

                <Form.Item
                    label="回测时间范围"
                    name="date_range"
                    rules={[{ required: true, message: '请选择时间范围' }]}
                >
                    <RangePicker style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item label="网格策略参数" style={{ marginBottom: 0 }}>
                    <Form.Item
                        label="上涨触发比例"
                        name="rise_ratio"
                        rules={[{ required: true }]}
                        style={{ display: 'inline-block', width: 'calc(33% - 8px)', marginRight: 8 }}
                    >
                        <InputNumber step={0.01} min={0} max={1} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                        label="下跌触发比例"
                        name="fall_ratio"
                        rules={[{ required: true }]}
                        style={{ display: 'inline-block', width: 'calc(33% - 8px)', margin: '0 8px' }}
                    >
                        <InputNumber step={0.01} min={0} max={1} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                        label="加倍投系数"
                        name="multiplier"
                        rules={[{ required: true }]}
                        style={{ display: 'inline-block', width: 'calc(33% - 8px)', marginLeft: 8 }}
                    >
                        <InputNumber step={0.1} min={1} style={{ width: '100%' }} />
                    </Form.Item>
                </Form.Item>

                <Form.Item>
                    <Button type="primary" htmlType="submit" block>
                        开始回测
                    </Button>
                </Form.Item>
            </Form>
        </Card>
    );
};

export default BacktestConfig;
