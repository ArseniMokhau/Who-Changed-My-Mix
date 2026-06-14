import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { InjectQueue } from '@nestjs/bull';
import type { Queue } from 'bull';
import { AudioMetadata } from './audio.entity';

@Injectable()
export class AudioService {
  constructor(
    @InjectRepository(AudioMetadata)
    private audioRepository: Repository<AudioMetadata>,
    @InjectQueue('audio-analysis') 
    private audioQueue: Queue,
  ) {}

  async processNewFile(file: Express.Multer.File): Promise<AudioMetadata> {
    const storagePath = `/storage/uploads/${Date.now()}-${file.originalname}`;

    const metadata = this.audioRepository.create({
      originalFileName: file.originalname,
      storagePath: storagePath,
    });
    const savedMetadata = await this.audioRepository.save(metadata);

    await this.audioQueue.add('analyze-mix', {
      metadataId: savedMetadata.id,
      filePath: storagePath,
    });

    return savedMetadata;
  }
}