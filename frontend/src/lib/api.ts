const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function startResearch(companyName: string, websiteUrl?: string) {
  const res = await fetch(`${API_BASE}/api/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company_name: companyName, website_url: websiteUrl }),
  });
  return res.json();
}

export async function getResearch(id: string) {
  const res = await fetch(`${API_BASE}/api/research/${id}`);
  return res.json();
}

export function streamResearch(id: string): EventSource {
  return new EventSource(`${API_BASE}/api/research/${id}/stream`);
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/api/history`);
  return res.json();
}

export async function searchBriefings(query: string) {
  const params = new URLSearchParams({ q: query });
  const res = await fetch(`${API_BASE}/api/search?${params}`);
  return res.json();
}
