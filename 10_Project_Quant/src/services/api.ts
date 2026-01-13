import request from '../utils/request';

export const login = (data: any) => request.post('/api/auth/login', data);
export const getFunds = (params: any) => request.get('/api/funds', { params });
export const getUsers = (params: any = {}) => request.get('/api/users', { params });
export const runBacktest = (data: any) => request.post('/api/backtest/run', data);
