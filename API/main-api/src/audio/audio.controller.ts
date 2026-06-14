import { Controller, Post, UploadedFile, UseInterceptors } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AudioService } from './audio.service';

@Controller('audio')
export class AudioController {
  constructor(private readonly audioService: AudioService) {}

  @Post('verify')
  @UseInterceptors(FileInterceptor('file'))
  async verifyAudio(@UploadedFile() file: Express.Multer.File) {
    
    const metadata = await this.audioService.processNewFile(file);

    return {
      message: 'File accepted for processing.',
      trackingId: metadata.id,
      status: metadata.status,
    };
  }
}