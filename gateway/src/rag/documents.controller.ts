import {
  BadRequestException,
  Body,
  Controller,
  Delete,
  Get,
  Param,
  Post,
  Query,
  Req,
  UseGuards,
  UseInterceptors,
  UploadedFile,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { Request } from 'express';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard';
import { AiBackendClient } from './ai-backend-client.service';
import { UploadDocumentDto } from './dto/document.dto';

@Controller('documents')
@UseGuards(JwtAuthGuard)
export class DocumentsController {
  constructor(private readonly client: AiBackendClient) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  upload(
    @UploadedFile() file: Express.Multer.File | undefined,
    @Body() dto: UploadDocumentDto,
    @Req() req: Request,
  ) {
    if (!file) {
      throw new BadRequestException('file is required');
    }

    const formData = new FormData();
    formData.append('knowledge_base_id', dto.knowledgeBaseId);
    formData.append(
      'file',
      new Blob([Uint8Array.from(file.buffer)], { type: file.mimetype }),
      file.originalname,
    );

    return this.client.forward('POST', '/documents', req.headers.authorization, { formData });
  }

  @Get()
  list(@Query('knowledgeBaseId') knowledgeBaseId: string, @Req() req: Request) {
    return this.client.forward('GET', '/documents', req.headers.authorization, {
      query: { knowledge_base_id: knowledgeBaseId },
    });
  }

  @Get(':id')
  get(@Param('id') id: string, @Req() req: Request) {
    return this.client.forward('GET', `/documents/${id}`, req.headers.authorization);
  }

  @Delete(':id')
  remove(@Param('id') id: string, @Req() req: Request) {
    return this.client.forward('DELETE', `/documents/${id}`, req.headers.authorization);
  }
}
