function snakeToCamel(key: string): string {
  return key.replace(/_([a-z0-9])/g, (_, c: string) => c.toUpperCase());
}

function camelToSnake(key: string): string {
  return key.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
}

function mapKeys(input: unknown, mapKey: (key: string) => string): unknown {
  if (Array.isArray(input)) {
    return input.map((item) => mapKeys(item, mapKey));
  }
  if (input !== null && typeof input === 'object' && !(input instanceof Date)) {
    return Object.fromEntries(
      Object.entries(input as Record<string, unknown>).map(([key, value]) => [
        mapKey(key),
        mapKeys(value, mapKey),
      ]),
    );
  }
  return input;
}

export function keysToCamel<T = unknown>(input: unknown): T {
  return mapKeys(input, snakeToCamel) as T;
}

export function keysToSnake<T = unknown>(input: unknown): T {
  return mapKeys(input, camelToSnake) as T;
}
