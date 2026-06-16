import { Controller, Post, Body, UploadedFile, UseInterceptors, Get, Param } from '@nestjs/common';
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

  @Post('webhook/ai-result')
  async handleAiWebhook(@Body() body: { metadataId: string; score: number; isManipulated: boolean }) {
    await this.audioService.saveAiResult(body.metadataId, body.score, body.isManipulated);
    return { success: true };
  }

  @Get('status/:id')
  async checkStatus(@Param('id') id: string) {
    return this.audioService.getAudioStastus(id);
  }
}