import { HttpException, Inject, Injectable } from '@nestjs/common';
import { keysToCamel, keysToSnake } from '../common/utils/case-converter';

interface ForwardOptions {
  query?: Record<string, string | undefined>;
  json?: unknown;
  formData?: FormData;
}

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE';

@Injectable()
export class AiBackendClient {
  private readonly baseUrl: string;

  constructor(@Inject('APP_CONFIG') config: { aiBackendUrl: string }) {
    this.baseUrl = config.aiBackendUrl;
  }

  async forward<T>(
    method: HttpMethod,
    path: string,
    authHeader: string | undefined,
    options: ForwardOptions = {},
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}/api/v1${path}`);
    if (options.query) {
      for (const [key, value] of Object.entries(options.query)) {
        if (value !== undefined) url.searchParams.set(key, value);
      }
    }

    const headers: Record<string, string> = {};
    if (authHeader) headers.Authorization = authHeader;

    let body: BodyInit | undefined;
    if (options.formData) {
      body = options.formData;
    } else if (options.json !== undefined) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(keysToSnake(options.json));
    }

    let response: Response;
    try {
      response = await fetch(url, { method, headers, body });
    } catch {
      throw new HttpException(
        { code: 'AI_BACKEND_UNREACHABLE', message: 'AI backend is unreachable' },
        502,
      );
    }

    const text = await response.text();
    const data = text ? JSON.parse(text) : undefined;

    if (!response.ok) {
      const message =
        (typeof data?.detail === 'string' && data.detail) ||
        (Array.isArray(data?.detail) && JSON.stringify(data.detail)) ||
        'AI backend request failed';
      throw new HttpException({ code: `AI_BACKEND_${response.status}`, message }, response.status);
    }

    return keysToCamel<T>(data);
  }
}
