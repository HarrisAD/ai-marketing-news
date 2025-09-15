import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useSearchParams } from 'react-router-dom';
import { storiesApi } from '../services/api';
import StoryCard from '../components/StoryCard';
import { AdjustmentsHorizontalIcon, CheckIcon } from '@heroicons/react/24/outline';

const Stories: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedStories, setSelectedStories] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Filter state
  const [filters, setFilters] = useState({
    min_score: parseInt(searchParams.get('min_score') || '0'),
    source_domain: searchParams.get('source_domain') || '',
    days_back: parseInt(searchParams.get('days_back') || '') || undefined,
    limit: parseInt(searchParams.get('limit') || '') || undefined,
  });

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.min_score > 0) params.set('min_score', filters.min_score.toString());
    if (filters.source_domain) params.set('source_domain', filters.source_domain);
    if (filters.days_back) params.set('days_back', filters.days_back.toString());
    if (filters.limit) params.set('limit', filters.limit.toString());
    setSearchParams(params);
  }, [filters, setSearchParams]);

  const { data: storiesData, isLoading, error, refetch } = useQuery(
    ['stories', filters],
    () => storiesApi.getStories(filters),
    { refetchInterval: 60000 }
  );

  const { data: sourcesData } = useQuery('sources', storiesApi.getSources);

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSelectStory = (storyId: string) => {
    setSelectedStories(prev => 
      prev.includes(storyId) 
        ? prev.filter(id => id !== storyId)
        : [...prev, storyId]
    );
  };

  const handleSelectAll = () => {
    if (selectedStories.length === storiesData?.stories.length) {
      setSelectedStories([]);
    } else {
      setSelectedStories(storiesData?.stories.map(s => s.id) || []);
    }
  };

  const clearFilters = () => {
    setFilters({
      min_score: 0,
      source_domain: '',
      days_back: undefined,
      limit: undefined,
    });
  };

  if (error) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="text-center py-12">
          <div className="text-red-500 mb-4">Failed to load stories</div>
          <button
            onClick={() => refetch()}
            className="text-blue-600 hover:text-blue-500"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stories</h1>
          <p className="mt-2 text-sm text-gray-700">
            Browse and filter AI marketing news stories
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <AdjustmentsHorizontalIcon className="h-4 w-4 mr-2" />
            Filters
          </button>
          {selectedStories.length > 0 && (
            <button
              onClick={() => {
                // Navigate to newsletter creation with selected stories
                const params = new URLSearchParams();
                params.set('selected_stories', selectedStories.join(','));
                window.location.href = `/create-newsletter?${params.toString()}`;
              }}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Create Newsletter ({selectedStories.length})
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Min Score
              </label>
              <select
                value={filters.min_score}
                onChange={(e) => handleFilterChange('min_score', parseInt(e.target.value))}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value={0}>All scores</option>
                <option value={90}>90+ (Excellent)</option>
                <option value={80}>80+ (High)</option>
                <option value={70}>70+ (Good)</option>
                <option value={60}>60+ (Moderate)</option>
                <option value={50}>50+ (Basic)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Source
              </label>
              <select
                value={filters.source_domain}
                onChange={(e) => handleFilterChange('source_domain', e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="">All sources</option>
                {sourcesData?.sources.map((source) => (
                  <option key={source.domain} value={source.domain}>
                    {source.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Time Range
              </label>
              <select
                value={filters.days_back || ''}
                onChange={(e) => handleFilterChange('days_back', e.target.value ? parseInt(e.target.value) : undefined)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="">All time</option>
                <option value={1}>Last 24 hours</option>
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Limit
              </label>
              <select
                value={filters.limit || ''}
                onChange={(e) => handleFilterChange('limit', e.target.value ? parseInt(e.target.value) : undefined)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="">No limit</option>
                <option value={10}>10 stories</option>
                <option value={25}>25 stories</option>
                <option value={50}>50 stories</option>
                <option value={100}>100 stories</option>
              </select>
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <button
              onClick={clearFilters}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Clear all filters
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="mt-6">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-sm text-gray-500">Loading stories...</p>
          </div>
        ) : !storiesData?.stories.length ? (
          <div className="text-center py-12">
            <h3 className="mt-2 text-sm font-medium text-gray-900">No stories found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your filters or refreshing the data.
            </p>
          </div>
        ) : (
          <>
            {/* Selection header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSelectAll}
                  className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
                >
                  <div className={`w-4 h-4 border border-gray-300 rounded mr-2 flex items-center justify-center ${
                    selectedStories.length === storiesData?.stories.length ? 'bg-blue-600 border-blue-600' : ''
                  }`}>
                    {selectedStories.length === storiesData?.stories.length && (
                      <CheckIcon className="w-3 h-3 text-white" />
                    )}
                  </div>
                  Select all ({storiesData.stories.length})
                </button>
                {selectedStories.length > 0 && (
                  <span className="text-sm text-gray-500">
                    {selectedStories.length} selected
                  </span>
                )}
              </div>

              <div className="text-sm text-gray-500">
                Showing {storiesData.stories.length} stories
              </div>
            </div>

            {/* Stories list */}
            <div className="space-y-6">
              {storiesData.stories.map((story) => (
                <StoryCard
                  key={story.id}
                  story={story}
                  showCheckbox={true}
                  isSelected={selectedStories.includes(story.id)}
                  onSelect={handleSelectStory}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Stories;