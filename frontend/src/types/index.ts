export interface Story {
  id: string;
  canonical_url: string;
  title: string;
  description: string;
  content: string;
  published_date: string;
  fetched_date: string;
  source_domain: string;
  source_name: string;
  score?: number;
  marketer_relevance: string[];
  action_hint: string;
  tags: string[];
  relevance_score?: number;
  impact_score?: number;
  adoption_score?: number;
  urgency_score?: number;
  credibility_score?: number;
  similar_stories: string[];
  is_canonical: boolean;
}

export interface Newsletter {
  newsletter_id: string;
  content: string;
  story_count: number;
  stories_used: string[];
  generated_date: string;
  metadata?: {
    date_from: string;
    date_to: string;
    min_score: number;
    editorial_instructions: string;
  };
}

export interface NewsSource {
  domain: string;
  name: string;
  rss_urls: string[];
  fallback_urls: string[];
  is_active?: boolean;
  has_rss?: boolean;
}

export interface SystemStats {
  total_stories: number;
  total_newsletters: number;
  score_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  average_score: number;
  data_dir: string;
  stories_file_size: number;
}

export interface NewsletterRequest {
  date_from: string;
  date_to: string;
  min_score: number;
  selected_story_ids: string[];
  editorial_instructions: string;
  max_stories: number;
}