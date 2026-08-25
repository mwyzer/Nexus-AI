import { Body, Controller, Post, Req, UseGuards } from '@nestjs/common';
import { Request } from 'express';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard';
import { AiBackendClient } from './ai-backend-client.service';
import { GenerateAnswerDto } from './dto/rag.dto';

@Controller('rag')
@UseGuards(JwtAuthGuard)
export class RagController {
  constructor(private readonly client: AiBackendClient) {}

  @Post('generate')
  generate(@Body() dto: GenerateAnswerDto, @Req() req: Request) {
    return this.client.forward('POST', '/rag/generate', req.headers.authorization, { json: dto });
  }
}
