export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
} as const;