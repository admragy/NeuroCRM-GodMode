const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export async function apiFetch(path: string, options: RequestInit = {}) {
  const url = API_BASE ? `${API_BASE.replace(/\/$/, '')}/${path.replace(/^/, '')}` : `/api/${path.replace(/^/, '')}`;
  const res = await fetch(url, options as any);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API Error ${res.status}: ${text}`);
  }
  return res.json();
}