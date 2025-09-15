import axios from 'axios';
import { Story, Newsletter, NewsSource, SystemStats, NewsletterRequest } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Stories API
export const storiesApi = {
  getStories: async (params?: {
    min_score?: number;
    source_domain?: string;
    days_back?: number;
    limit?: number;
    canonical_only?: boolean;
  }): Promise<{ stories: Story[]; count: number }> => {
    const response = await api.get('/stories', { params });
    return response.data;
  },

  getStory: async (storyId: string): Promise<{ story: Story }> => {
    const response = await api.get(`/stories/${storyId}`);
    return response.data;
  },

  refreshStories: async (sourceDomains?: string[]): Promise<any> => {
    const response = await api.post('/refresh', { source_domains: sourceDomains });
    return response.data;
  },

  getSources: async (): Promise<{ sources: NewsSource[]; count: number }> => {
    const response = await api.get('/sources');
    return response.data;
  },

  getTags: async (): Promise<{ tags: string[]; count: number }> => {
    const response = await api.get('/tags');
    return response.data;
  },

  getStats: async (): Promise<{ stats: SystemStats }> => {
    const response = await api.get('/stats');
    return response.data;
  },
};

// Newsletters API
export const newslettersApi = {
  generateNewsletter: async (request: NewsletterRequest): Promise<{ newsletter: Newsletter }> => {
    const response = await api.post('/newsletters/render', request);
    return response.data;
  },

  getNewsletters: async (): Promise<{ newsletters: Newsletter[]; count: number }> => {
    const response = await api.get('/newsletters');
    return response.data;
  },

  getNewsletter: async (newsletterId: string): Promise<{ newsletter: Newsletter }> => {
    const response = await api.get(`/newsletters/${newsletterId}`);
    return response.data;
  },

  downloadMarkdown: async (newsletterId: string): Promise<string> => {
    const response = await api.get(`/newsletters/${newsletterId}/markdown`, {
      responseType: 'text',
    });
    return response.data;
  },

  getNewsletterStories: async (newsletterId: string): Promise<{ stories: Story[]; count: number }> => {
    const response = await api.get(`/newsletters/${newsletterId}/stories`);
    return response.data;
  },

  getNewsletterAnalytics: async (newsletterId: string): Promise<any> => {
    const response = await api.get(`/newsletters/${newsletterId}/analytics`);
    return response.data;
  },
};

export default api;