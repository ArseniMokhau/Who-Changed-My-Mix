// [Inference] src/app.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BullModule } from '@nestjs/bull';
import { AudioModule } from './audio/audio.module';

@Module({
  imports: [
    // PostgreSQL
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: 'localhost',
      port: 5432,
      username: 'admin',
      password: 'password',
      database: 'whocangedmymix',
      autoLoadEntities: true,
      synchronize: true, // Only in development
    }),
    // Redis
    BullModule.forRoot({
      redis: {
        host: 'localhost',
        port: 6379,
      },
    }),
    AudioModule,
  ],
})
export class AppModule {}