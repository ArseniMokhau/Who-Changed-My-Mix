// [Inference] src/audio/audio.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BullModule } from '@nestjs/bull';
import { AudioController } from './audio.controller';
import { AudioService } from './audio.service';
import { AudioMetadata } from './audio.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([AudioMetadata]),
    BullModule.registerQueue({
      name: 'audio-analysis',
    }),
  ],
  controllers: [AudioController],
  providers: [AudioService],
})
export class AudioModule {}