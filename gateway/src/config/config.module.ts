import { Global, Module } from '@nestjs/common';

@Global()
@Module({
  providers: [
    {
      provide: 'APP_CONFIG',
      useFactory: () => ({
        jwtAccessSecret: process.env.JWT_ACCESS_SECRET || 'dev-secret',
        jwtRefreshSecret: process.env.JWT_REFRESH_SECRET || 'dev-refresh-secret',
        jwtAccessExpiresIn: process.env.JWT_ACCESS_EXPIRES_IN || '15m',
        jwtRefreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
        gatewayPort: parseInt(process.env.GATEWAY_PORT || '3001', 10),
        aiBackendUrl: process.env.AI_BACKEND_URL || 'http://localhost:8000',
        frontendUrl: process.env.FRONTEND_URL || 'http://localhost:3000',
      }),
    },
  ],
  exports: ['APP_CONFIG'],
})
export class ConfigModule {}
