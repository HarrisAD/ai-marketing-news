import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  DocumentTextIcon, 
  NewspaperIcon, 
  ChartBarIcon,
  ArrowPathIcon,
  ExclamationCircleIcon,
  RssIcon,
  CheckCircleIcon,
  XCircleIcon,
  GlobeAltIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { storiesApi, newslettersApi } from '../services/api';

const Dashboard: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [refreshSuccess, setRefreshSuccess] = useState(false);

  const { data: statsData, isLoading: statsLoading } = useQuery(
    'stats',
    storiesApi.getStats,
    { refetchInterval: 30000 }
  );

  const { data: recentStories, isLoading: storiesLoading } = useQuery(
    'recent-stories',
    () => storiesApi.getStories({ limit: 5, min_score: 70 }),
    { refetchInterval: 30000 }
  );

  const { data: newslettersData } = useQuery(
    'newsletters',
    newslettersApi.getNewsletters
  );

  const { data: sourcesData, isLoading: sourcesLoading } = useQuery(
    'sources',
    storiesApi.getSources,
    { refetchInterval: 60000 }
  );

  const stats = statsData?.stats;

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshError(null);
    setRefreshSuccess(false);
    
    try {
      await storiesApi.refreshStories();
      setRefreshSuccess(true);
      // Refresh queries after a short delay to show success message
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error: any) {
      console.error('Failed to refresh stories:', error);
      
      // Handle different types of errors
      if (error.code === 'ECONNABORTED') {
        setRefreshError('Refresh is taking longer than expected due to OpenAI rate limits. The process is running in the background and may take 5-10 minutes to complete.');
      } else if (error.response?.status === 429) {
        setRefreshError('Rate limit reached. Please try again later.');
      } else if (error.response?.data?.error) {
        setRefreshError(error.response.data.error);
      } else {
        setRefreshError('Refresh timed out but may still be running in the background. Check back in a few minutes for new stories.');
      }
      
      setIsRefreshing(false);
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            AI news monitoring and newsletter generation for marketers
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
              isRefreshing 
                ? 'bg-gray-400 cursor-not-allowed' 
                : refreshSuccess 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing...' : refreshSuccess ? 'Success!' : 'Refresh Stories'}
          </button>
        </div>
      </div>

      {/* Notifications */}
      {(refreshError || refreshSuccess) && (
        <div className={`mt-4 rounded-md p-4 ${
          refreshError ? 'bg-yellow-50' : 'bg-green-50'
        }`}>
          <div className="flex">
            <div className="flex-shrink-0">
              {refreshError ? (
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
              ) : (
                <CheckCircleIcon className="h-5 w-5 text-green-400" />
              )}
            </div>
            <div className="ml-3">
              <p className={`text-sm font-medium ${
                refreshError ? 'text-yellow-800' : 'text-green-800'
              }`}>
                {refreshError || 'Stories refresh completed successfully!'}
              </p>
            </div>
            <div className="ml-auto pl-3">
              <div className="-mx-1.5 -my-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setRefreshError(null);
                    setRefreshSuccess(false);
                  }}
                  className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                    refreshError 
                      ? 'bg-yellow-50 text-yellow-500 hover:bg-yellow-100 focus:ring-yellow-600' 
                      : 'bg-green-50 text-green-500 hover:bg-green-100 focus:ring-green-600'
                  }`}
                >
                  <span className="sr-only">Dismiss</span>
                  <XCircleIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Stories
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {statsLoading ? '...' : stats?.total_stories || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <NewspaperIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Newsletters
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {newslettersData?.count || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Avg Score
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {statsLoading ? '...' : Math.round(stats?.average_score || 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationCircleIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    High Score (80+)
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {statsLoading ? '...' : (stats?.score_distribution?.['80-89'] || 0) + (stats?.score_distribution?.['90-100'] || 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent High-Score Stories */}
      <div className="mt-8">
        <div className="sm:flex sm:items-center sm:justify-between">
          <h2 className="text-lg font-medium text-gray-900">
            Recent High-Score Stories
          </h2>
          <Link
            to="/stories"
            className="mt-4 sm:mt-0 text-sm text-blue-600 hover:text-blue-500"
          >
            View all stories →
          </Link>
        </div>

        <div className="mt-4">
          {storiesLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-sm text-gray-500">Loading stories...</p>
            </div>
          ) : recentStories?.stories.length === 0 ? (
            <div className="text-center py-8">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No high-score stories</h3>
              <p className="mt-1 text-sm text-gray-500">
                Click "Refresh Stories" to fetch the latest AI news.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {recentStories?.stories.slice(0, 5).map((story) => (
                <div key={story.id} className="bg-white shadow rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-sm font-medium text-gray-900">
                        {story.title}
                      </h3>
                      <p className="mt-1 text-sm text-gray-500">
                        {story.source_name} • {new Date(story.published_date).toLocaleDateString()}
                      </p>
                      <p className="mt-2 text-sm text-gray-700 line-clamp-2">
                        {story.description}
                      </p>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        story.score >= 90 ? 'bg-green-100 text-green-800' :
                        story.score >= 80 ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {story.score}/100
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* News Sources Status */}
      <div className="mt-8">
        <div className="sm:flex sm:items-center sm:justify-between">
          <h2 className="text-lg font-medium text-gray-900">
            News Sources Monitor
          </h2>
          <div className="mt-4 sm:mt-0 text-sm text-gray-500">
            {sourcesLoading ? 'Loading...' : `${sourcesData?.active_count || 0} of ${sourcesData?.total_count || 0} sources active`}
          </div>
        </div>

        <div className="mt-4">
          {sourcesLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-sm text-gray-500">Loading sources...</p>
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-sm font-medium text-gray-900">Monitored News Sources</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Sources being actively monitored for AI and marketing news
                </p>
              </div>
              <div className="border-t border-gray-200">
                <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                  {sourcesData?.sources
                    .sort((a, b) => {
                      // Sort by active status first, then by name
                      if (a.is_active !== b.is_active) {
                        return a.is_active ? -1 : 1;
                      }
                      return a.name.localeCompare(b.name);
                    })
                    .map((source) => (
                    <div key={source.domain} className="px-4 py-4 flex items-center justify-between">
                      <div className="flex items-center min-w-0 flex-1">
                        <div className="flex items-center">
                          {source.is_active ? (
                            <CheckCircleIcon className="h-5 w-5 text-green-500" />
                          ) : (
                            <XCircleIcon className="h-5 w-5 text-gray-400" />
                          )}
                          <div className="ml-3">
                            <p className={`text-sm font-medium ${
                              source.is_active ? 'text-gray-900' : 'text-gray-500'
                            }`}>
                              {source.name}
                            </p>
                            <p className="text-sm text-gray-500">{source.domain}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {source.has_rss && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            <RssIcon className="h-3 w-3 mr-1" />
                            RSS
                          </span>
                        )}
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          <GlobeAltIcon className="h-3 w-3 mr-1" />
                          Web
                        </span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          source.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {source.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                <p className="text-xs text-gray-500">
                  Active sources are configured in your environment settings. 
                  Contact your administrator to modify source selection.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Link
            to="/create-newsletter"
            className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
          >
            <div className="flex-shrink-0">
              <NewspaperIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1 min-w-0">
              <span className="absolute inset-0" aria-hidden="true" />
              <p className="text-sm font-medium text-gray-900">Create Newsletter</p>
              <p className="text-sm text-gray-500">Generate a custom newsletter from recent stories</p>
            </div>
          </Link>

          <Link
            to="/stories?min_score=80"
            className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
          >
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1 min-w-0">
              <span className="absolute inset-0" aria-hidden="true" />
              <p className="text-sm font-medium text-gray-900">High Impact Stories</p>
              <p className="text-sm text-gray-500">Browse stories with 80+ marketing relevance score</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;