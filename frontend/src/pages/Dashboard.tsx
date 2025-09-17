import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useQueryClient } from 'react-query';
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
  ExclamationTriangleIcon,
  PlusCircleIcon
} from '@heroicons/react/24/outline';
import { storiesApi, newslettersApi } from '../services/api';
import { NewsSource } from '../types';

const Dashboard: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [refreshSuccessMessage, setRefreshSuccessMessage] = useState<string | null>(null);
  const [sourceActionDomain, setSourceActionDomain] = useState<string | null>(null);
  const [sourceActionError, setSourceActionError] = useState<string | null>(null);
  const [sourceActionMessage, setSourceActionMessage] = useState<string | null>(null);
  const [isAddingSource, setIsAddingSource] = useState(false);
  const [newSource, setNewSource] = useState({
    domain: '',
    name: '',
    rss_urls: '',
    fallback_urls: '',
    activate: true,
  });
  const [showApiKeyForm, setShowApiKeyForm] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [apiKeyError, setApiKeyError] = useState<string | null>(null);
  const [apiKeyMessage, setApiKeyMessage] = useState<string | null>(null);
  const [isSavingApiKey, setIsSavingApiKey] = useState(false);

  const queryClient = useQueryClient();

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

  const { data: openAIConfig, isLoading: openAIConfigLoading } = useQuery(
    'openai-config',
    storiesApi.getOpenAIConfig,
    { refetchOnWindowFocus: false }
  );

  const { data: refreshStatus } = useQuery(
    'refresh-status',
    storiesApi.getRefreshStatus,
    { refetchInterval: 5000 }
  );

  const lastResultRef = useRef<string | null>(null);

  useEffect(() => {
    setIsRefreshing(refreshStatus?.refreshing ?? false);
  }, [refreshStatus?.refreshing]);

  useEffect(() => {
    const result = refreshStatus?.last_result;
    if (!result) {
      return;
    }
    const timestamp = result.timestamp || result?.duration_seconds?.toString();
    if (!timestamp || lastResultRef.current === timestamp) {
      return;
    }
    lastResultRef.current = timestamp;

    if (result.success) {
      const saved = result.stories_saved ?? result.stories_scored ?? 0;
      setRefreshSuccessMessage(`Stories refreshed: ${saved} saved.`);
      setRefreshError(null);
      queryClient.invalidateQueries('stories');
    } else {
      setRefreshError(result.error || 'Stories refresh failed.');
    }
  }, [refreshStatus?.last_result, queryClient]);

  const stats = statsData?.stats;

  const handleToggleSource = async (source: NewsSource) => {
    setSourceActionDomain(source.domain);
    setSourceActionError(null);
    setSourceActionMessage(null);

    try {
      await storiesApi.updateSourceStatus(source.domain, !source.is_active);
      setSourceActionMessage(`${!source.is_active ? 'Activated' : 'Deactivated'} ${source.name}`);
      await queryClient.invalidateQueries('sources');
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Failed to update source status.';
      setSourceActionError(message);
    } finally {
      setSourceActionDomain(null);
    }
  };

  const handleAddSource = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSourceActionError(null);
    setSourceActionMessage(null);
    setIsAddingSource(true);

    try {
      const rssUrls = newSource.rss_urls
        .split(',')
        .map((url) => url.trim())
        .filter((url) => url.length > 0);
      const fallbackUrls = newSource.fallback_urls
        .split(',')
        .map((url) => url.trim())
        .filter((url) => url.length > 0);

      await storiesApi.addSource({
        domain: newSource.domain.trim(),
        name: newSource.name.trim(),
        rss_urls: rssUrls,
        fallback_urls: fallbackUrls,
        activate: newSource.activate,
      });

      setSourceActionMessage(`Added ${newSource.name || newSource.domain}`);
      setNewSource({ domain: '', name: '', rss_urls: '', fallback_urls: '', activate: true });
      await queryClient.invalidateQueries('sources');
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Failed to add source. Please check the details and try again.';
      setSourceActionError(message);
    } finally {
      setIsAddingSource(false);
    }
  };

  const handleSaveApiKey = async () => {
    setApiKeyError(null);
    setApiKeyMessage(null);

    if (!apiKeyInput.trim()) {
      setApiKeyError('Please enter your OpenAI API key.');
      return;
    }

    setIsSavingApiKey(true);
    try {
      await storiesApi.updateOpenAIKey(apiKeyInput.trim());
      setApiKeyMessage('OpenAI API key saved successfully.');
      setApiKeyInput('');
      setShowApiKeyForm(false);
      await queryClient.invalidateQueries('openai-config');
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Failed to save API key. Please double-check and try again.';
      setApiKeyError(message);
    } finally {
      setIsSavingApiKey(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshError(null);
    setRefreshSuccessMessage(null);
    
    try {
      const result = await storiesApi.refreshStories();
      const backgroundRefresh = result?.is_background;
      setRefreshSuccessMessage(
        result?.message || (backgroundRefresh
          ? 'Stories refresh started in the background. New stories will appear automatically when ready.'
          : 'Stories refresh completed successfully!')
      );

      if (!backgroundRefresh) {
        // For synchronous responses, reload after a short delay to show the success message
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        setIsRefreshing(false);
      }
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
                : refreshSuccessMessage 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing...' : refreshSuccessMessage ? 'Success!' : 'Refresh Stories'}
          </button>
        </div>
      </div>

      {/* Notifications */}
      {(refreshError || refreshSuccessMessage || apiKeyMessage || apiKeyError) && (
        <div className={`mt-4 rounded-md p-4 ${
          refreshError || apiKeyError ? 'bg-yellow-50' : 'bg-green-50'
        }`}>
          <div className="flex">
            <div className="flex-shrink-0">
              {refreshError || apiKeyError ? (
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
              ) : (
                <CheckCircleIcon className="h-5 w-5 text-green-400" />
              )}
            </div>
            <div className="ml-3">
              <p className={`text-sm font-medium ${
                refreshError || apiKeyError ? 'text-yellow-800' : 'text-green-800'
              }`}>
                {refreshError || apiKeyError || refreshSuccessMessage || apiKeyMessage}
              </p>
            </div>
            <div className="ml-auto pl-3">
              <div className="-mx-1.5 -my-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setRefreshError(null);
                    setRefreshSuccessMessage(null);
                    setApiKeyError(null);
                    setApiKeyMessage(null);
                  }}
                  className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                    refreshError || apiKeyError
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
                <ExclamationCircleIcon className={`h-6 w-6 ${openAIConfig?.configured ? 'text-green-500' : 'text-red-500'}`} />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    OpenAI API Key
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {openAIConfigLoading ? 'Checking...' : openAIConfig?.configured ? 'Configured' : 'Not Configured'}
                  </dd>
                </dl>
              </div>
            </div>
            <div className="mt-4">
              <button
                onClick={() => {
                  setShowApiKeyForm((prev) => !prev);
                  setApiKeyError(null);
                  setApiKeyMessage(null);
                }}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {showApiKeyForm ? 'Cancel' : openAIConfig?.configured ? 'Update API Key' : 'Set API Key'}
              </button>
            </div>
            {showApiKeyForm && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700">OpenAI API Key</label>
                <input
                  type="text"
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  placeholder="sk-..."
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                <p className="mt-2 text-xs text-gray-500">
                  Paste the key you generated from the OpenAI dashboard. Stored securely on your device.
                </p>
                <div className="mt-3 flex justify-end">
                  <button
                    onClick={handleSaveApiKey}
                    disabled={isSavingApiKey}
                    className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                      isSavingApiKey ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                  >
                    {isSavingApiKey ? 'Saving...' : 'Save Key'}
                  </button>
                </div>
              </div>
            )}
            {openAIConfig?.masked_key && !showApiKeyForm && (
              <p className="mt-4 text-xs text-gray-500">
                Current key: {openAIConfig.masked_key}
              </p>
            )}
          </div>
        </div>

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
                        {source.is_custom && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            Custom
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
                        <button
                          onClick={() => handleToggleSource(source)}
                          disabled={sourceActionDomain === source.domain}
                          className={`inline-flex items-center px-2.5 py-1 border text-xs font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                            source.is_active
                              ? 'border-red-200 text-red-600 hover:bg-red-50 focus:ring-red-500'
                              : 'border-green-200 text-green-600 hover:bg-green-50 focus:ring-green-500'
                          } ${sourceActionDomain === source.domain ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          {sourceActionDomain === source.domain
                            ? 'Updating...'
                            : source.is_active
                              ? 'Deactivate'
                              : 'Activate'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
                {(sourceActionError || sourceActionMessage) && (
                  <div className={`mb-4 rounded-md p-3 text-sm ${
                    sourceActionError ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
                  }`}>
                    {sourceActionError || sourceActionMessage}
                  </div>
                )}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center mb-4">
                    <PlusCircleIcon className="h-5 w-5 text-blue-500 mr-2" />
                    <h4 className="text-sm font-medium text-gray-900">Add New Source</h4>
                  </div>
                  <form className="space-y-4" onSubmit={handleAddSource}>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">Domain</label>
                        <input
                          type="text"
                          value={newSource.domain}
                          onChange={(e) => setNewSource((prev) => ({ ...prev, domain: e.target.value }))}
                          placeholder="example.com"
                          required
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">Display Name</label>
                        <input
                          type="text"
                          value={newSource.name}
                          onChange={(e) => setNewSource((prev) => ({ ...prev, name: e.target.value }))}
                          placeholder="Source Name"
                          required
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">RSS URLs (comma separated)</label>
                      <input
                        type="text"
                        value={newSource.rss_urls}
                        onChange={(e) => setNewSource((prev) => ({ ...prev, rss_urls: e.target.value }))}
                        placeholder="https://example.com/feed"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide">Fallback URLs (comma separated)</label>
                      <input
                        type="text"
                        value={newSource.fallback_urls}
                        onChange={(e) => setNewSource((prev) => ({ ...prev, fallback_urls: e.target.value }))}
                        placeholder="https://example.com/news"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    <div className="flex items-center">
                      <input
                        id="activate-source"
                        type="checkbox"
                        checked={newSource.activate}
                        onChange={(e) => setNewSource((prev) => ({ ...prev, activate: e.target.checked }))}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="activate-source" className="ml-2 text-sm text-gray-700">
                        Activate immediately after adding
                      </label>
                    </div>
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={isAddingSource}
                        className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                          isAddingSource ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                      >
                        {isAddingSource ? 'Adding...' : 'Add Source'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {refreshStatus?.refreshing && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 rounded-full bg-blue-500 animate-pulse"></div>
              <span className="text-sm font-medium text-blue-800">Refreshing stories…</span>
            </div>
            <span className="text-xs text-blue-700 capitalize">
              {(() => {
                const stage = refreshStatus?.progress?.stage || 'starting';
                const meta = refreshStatus?.progress?.meta || {};
                switch (stage) {
                  case 'start':
                    return 'Preparing';
                  case 'crawled':
                    return `Fetched ${meta.count || 0} stories`;
                  case 'scoring':
                    return `Scoring ${meta.current || 0}/${meta.total || '?'}`;
                  case 'scoring_complete':
                    return `Scored ${meta.count || 0} stories`;
                  case 'deduplicating':
                    return 'Deduplicating';
                  case 'saving':
                    return `Saving ${meta.saved_count || 0} stories`;
                  default:
                    return 'Working…';
                }
              })()}
            </span>
          </div>
          <div className="mt-3 h-2 bg-blue-200 rounded">
            <div
              className="h-2 bg-blue-500 rounded"
              style={{
                width: `${(() => {
                  const stages = ['start', 'crawled', 'scoring', 'scoring_complete', 'deduplicating', 'saving'];
                  const stage = refreshStatus?.progress?.stage;
                  const index = stages.indexOf(stage);
                  if (index === -1) return 15;
                  return Math.min(95, Math.max(15, ((index + 1) / (stages.length + 1)) * 100));
                })()}%`,
              }}
            ></div>
          </div>
        </div>
      )}

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
