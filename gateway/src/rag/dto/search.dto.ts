import { IsIn, IsInt, IsNumber, IsOptional, IsString, IsUUID, Max, Min, MinLength } from 'class-validator';

export class SearchDto {
  @IsString()
  @MinLength(1)
  query!: string;

  @IsUUID()
  knowledgeBaseId!: string;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(50)
  topK?: number;

  @IsOptional()
  @IsIn(['semantic', 'keyword', 'hybrid'])
  searchType?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(1)
  hybridWeight?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(1)
  scoreThreshold?: number;
}
