import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { InjectQueue } from '@nestjs/bull';
import type { Queue } from 'bull';
import { AudioMetadata } from './audio.entity';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AudioService {
  constructor(
    @InjectRepository(AudioMetadata)
    private audioRepository: Repository<AudioMetadata>,
    @InjectQueue('audio-analysis') 
    private audioQueue: Queue,
  ) {}

  async processNewFile(file: Express.Multer.File): Promise<AudioMetadata> {

    const uploadDir = path.join(process.cwd(), 'storage', 'uploads');

    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    const fileName = `${Date.now()}-${file.originalname}`;
    const storagePath = path.join(uploadDir, fileName);

    fs.writeFileSync(storagePath, file.buffer);

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

  async saveAiResult(metadataId: string, score: number, isManipulated: boolean) {
    const record = await this.audioRepository.findOne({ where: { id: metadataId } });
    
    if (record) {
      record.manipulationScore = score;
      record.isManipulated = isManipulated;
      record.status = 'completed';
      await this.audioRepository.save(record);
      console.log(`Updated database for file ID: ${metadataId}`);
    }
  }

  async getAudioStastus(metadataId: string): Promise<AudioMetadata> {
    const record = await this.audioRepository.findOne({where: {id: metadataId}})

    if (!record) {
      throw new Error('Audio record not found');
    }

    return record;
  }
}