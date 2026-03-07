export interface KeyPerson {
  name: string;
  title: string;
}

export interface NewsItem {
  headline: string;
  date?: string;
  summary?: string;
}

export interface TechStack {
  confirmed: string[];
  inferred: string[];
}

export interface FundingInfo {
  total_raised?: string;
  last_round?: string;
  investors: string[];
}

export interface Briefing {
  company_name?: string;
  summary: string;
  business_model?: string;
  industry?: string;
  stage?: string;
  founded?: string;
  headquarters?: string;
  size?: string;
  website?: string;
  products_services: string[];
  key_people: KeyPerson[];
  recent_news: NewsItem[];
  tech_stack: TechStack;
  growth_signals: string[];
  competitive_landscape: string[];
  talking_points: string[];
  funding?: FundingInfo;
  confidence: number;
}

export interface ResearchJob {
  id: string;
  company_name: string;
  status: 'pending' | 'extracting' | 'synthesizing' | 'complete' | 'failed';
  created_at: string;
  updated_at: string;
  briefing?: Briefing;
  error?: string;
}

export interface ProgressEvent {
  research_id: string;
  status: string;
  stage: string;
  progress: number;
  message?: string;
}

export interface SearchResult {
  research_id: string;
  company_name: string;
  similarity: number;
  snippet: string;
}
