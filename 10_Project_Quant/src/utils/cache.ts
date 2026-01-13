type CacheEntry<T> = {
  expiresAt: number;
  value: T;
};

export function cacheGet<T>(key: string): T | null {
  const raw = localStorage.getItem(key);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as CacheEntry<T>;
    if (Date.now() > parsed.expiresAt) {
      localStorage.removeItem(key);
      return null;
    }
    return parsed.value;
  } catch {
    localStorage.removeItem(key);
    return null;
  }
}

export function cacheSet<T>(key: string, value: T, ttlMs: number): void {
  const entry: CacheEntry<T> = {
    expiresAt: Date.now() + ttlMs,
    value,
  };
  localStorage.setItem(key, JSON.stringify(entry));
}

