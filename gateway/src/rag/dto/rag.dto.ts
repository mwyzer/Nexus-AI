import { IsIn, IsInt, IsOptional, IsString, IsUUID, Max, Min, MinLength } from 'class-validator';

export class GenerateAnswerDto {
  @IsString()
  @MinLength(1)
  question!: string;

  @IsUUID()
  knowledgeBaseId!: string;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(20)
  topK?: number;

  @IsOptional()
  @IsIn(['semantic', 'keyword', 'hybrid'])
  searchType?: string;
}
