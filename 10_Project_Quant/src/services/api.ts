import request from '../utils/request';

export const login = (data: any) => request.post('/api/auth/login', data);
export const getFunds = (params: any) => request.get<any>('/api/funds/', { params }) as any;
export const getFundDetail = (code: string) => request.get<any>(`/api/funds/${code}`) as any;
export const syncFunds = (days: number) => request.post<any>(`/api/funds/sync?days=${days}`) as any;
export const getUsers = (params: any = {}) => request.get<any>('/api/users', { params }) as any;
export const runBacktest = (data: any) => request.post('/api/backtest/run', data);
