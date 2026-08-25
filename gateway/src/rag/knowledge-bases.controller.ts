import { Body, Controller, Delete, Get, Param, Patch, Post, Req, UseGuards } from '@nestjs/common';
import { Request } from 'express';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard';
import { AiBackendClient } from './ai-backend-client.service';
import { CreateKnowledgeBaseDto, UpdateKnowledgeBaseDto } from './dto/knowledge-base.dto';

@Controller('knowledge-bases')
@UseGuards(JwtAuthGuard)
export class KnowledgeBasesController {
  constructor(private readonly client: AiBackendClient) {}

  @Post()
  create(@Body() dto: CreateKnowledgeBaseDto, @Req() req: Request) {
    return this.client.forward('POST', '/knowledge-bases', req.headers.authorization, { json: dto });
  }

  @Get()
  list(@Req() req: Request) {
    return this.client.forward('GET', '/knowledge-bases', req.headers.authorization);
  }

  @Get(':id')
  get(@Param('id') id: string, @Req() req: Request) {
    return this.client.forward('GET', `/knowledge-bases/${id}`, req.headers.authorization);
  }

  @Patch(':id')
  update(@Param('id') id: string, @Body() dto: UpdateKnowledgeBaseDto, @Req() req: Request) {
    return this.client.forward('PATCH', `/knowledge-bases/${id}`, req.headers.authorization, { json: dto });
  }

  @Delete(':id')
  remove(@Param('id') id: string, @Req() req: Request) {
    return this.client.forward('DELETE', `/knowledge-bases/${id}`, req.headers.authorization);
  }
}
