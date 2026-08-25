import { Body, Controller, Post, Req, UseGuards } from '@nestjs/common';
import { Request } from 'express';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard';
import { AiBackendClient } from './ai-backend-client.service';
import { SearchDto } from './dto/search.dto';

@Controller('search')
@UseGuards(JwtAuthGuard)
export class SearchController {
  constructor(private readonly client: AiBackendClient) {}

  @Post()
  search(@Body() dto: SearchDto, @Req() req: Request) {
    return this.client.forward('POST', '/search', req.headers.authorization, { json: dto });
  }
}
