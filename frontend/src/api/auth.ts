import axios from 'axios';
import { apiClient } from './client';
import type { HealthStatus, LoginRequest, TokenResponse, User } from '../types/auth';

export async function loginApi(data: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', data);
  return response.data;
}

export async function getMeApi(): Promise<User> {
  const response = await apiClient.get<User>('/auth/me');
  return response.data;
}

export async function checkHealthApi(): Promise<HealthStatus> {
  const response = await axios.get<HealthStatus>('/health', { timeout: 5000 });
  return response.data;
}
