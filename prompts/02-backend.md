# Prompt: Backend Development

Use this prompt when implementing Gateway (NestJS) or AI Backend (FastAPI) features.

---

## Instructions

### NestJS Gateway Patterns

#### Module Structure
```
src/
├── {feature}/
│   ├── {feature}.module.ts
│   ├── {feature}.controller.ts
│   ├── {feature}.service.ts
│   ├── dto/
│   │   ├── create-{feature}.dto.ts
│   │   └── update-{feature}.dto.ts
│   ├── entities/
│   │   └── {feature}.entity.ts
│   └── __tests__/
│       ├── {feature}.controller.spec.ts
│       └── {feature}.service.spec.ts
```

#### Controller Template
```typescript
@Controller('api/v1/resource')
@UseGuards(JwtAuthGuard, RolesGuard)
export class ResourceController {
  constructor(private readonly resourceService: ResourceService) {}

  @Get()
  @Roles('admin', 'editor', 'viewer')
  async findAll(@Query() query: PaginationDto) {
    return this.resourceService.findAll(query);
  }

  @Get(':id')
  @Roles('admin', 'editor', 'viewer')
  async findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.resourceService.findOne(id);
  }

  @Post()
  @Roles('admin', 'editor')
  async create(@Body() dto: CreateResourceDto, @CurrentUser() user: JwtPayload) {
    return this.resourceService.create(dto, user.sub);
  }

  @Patch(':id')
  @Roles('admin', 'editor')
  async update(@Param('id', ParseUUIDPipe) id: string, @Body() dto: UpdateResourceDto) {
    return this.resourceService.update(id, dto);
  }

  @Delete(':id')
  @Roles('admin')
  async remove(@Param('id', ParseUUIDPipe) id: string) {
    return this.resourceService.remove(id);
  }
}
```

### FastAPI Patterns

#### Module Structure
```
app/
├── api/v1/
│   ├── router.py
│   └── endpoints/
│       └── {feature}.py
├── services/
│   └── {feature}_service.py
├── models/
│   └── {feature}.py
├── schemas/
│   └── {feature}.py
└── repositories/
    └── {feature}_repo.py
```

#### Endpoint Template
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user, get_db
from app.schemas.resource import ResourceCreate, ResourceResponse
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/resources", tags=["resources"])

@router.get("/", response_model=PaginatedResponse[ResourceResponse])
async def list_resources(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = ResourceService(db)
    return await service.list_resources(user.id, page, per_page)

@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    data: ResourceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = ResourceService(db)
    return await service.create_resource(user.id, data)
```

### Key Rules
- Always validate inputs with DTOs (NestJS) or Pydantic schemas (FastAPI)
- Use async/await throughout
- Handle errors with appropriate HTTP exceptions
- Log all errors with context
- Return consistent response format `{ success, data, error, meta }`
- Check permissions before every operation
- Use dependency injection for services
