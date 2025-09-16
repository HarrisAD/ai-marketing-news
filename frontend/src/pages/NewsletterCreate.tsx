import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useSearchParams } from 'react-router-dom';
import { storiesApi, newslettersApi } from '../services/api';
import StoryCard from '../components/StoryCard';
import { CalendarIcon, DocumentIcon } from '@heroicons/react/24/outline';

const NewsletterCreate: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [selectedStories, setSelectedStories] = useState<string[]>([]);
  const [generatedNewsletter, setGeneratedNewsletter] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    date_from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days ago
    date_to: new Date().toISOString().split('T')[0], // today
    min_score: 80,
    editorial_instructions: '',
    max_stories: 10,
  });

  // Load pre-selected stories from URL params
  useEffect(() => {
    const preSelected = searchParams.get('selected_stories');
    if (preSelected) {
      setSelectedStories(preSelected.split(','));
    }
  }, [searchParams]);

  // Fetch stories for the date range
  const { data: storiesData, isLoading } = useQuery(
    ['newsletter-stories', formData.date_from, formData.date_to, formData.min_score],
    () => storiesApi.getStories({
      min_score: formData.min_score,
      date_from: formData.date_from,
      date_to: formData.date_to,
    }),
    { enabled: !!(formData.date_from && formData.date_to) }
  );

  const filteredStories = storiesData?.stories || [];

  useEffect(() => {
    const availableIds = new Set(filteredStories.map(story => story.id));
    setSelectedStories(prev => {
      const next = prev.filter(id => availableIds.has(id));
      return next.length === prev.length ? prev : next;
    });
  }, [filteredStories]);

  // Auto-select high-scoring stories when data loads
  useEffect(() => {
    if (filteredStories.length > 0 && selectedStories.length === 0) {
      const autoSelected = filteredStories
        .filter(story => story.score >= formData.min_score)
        .slice(0, formData.max_stories)
        .map(story => story.id);
      setSelectedStories(autoSelected);
    }
  }, [filteredStories, formData.min_score, formData.max_stories, selectedStories.length]);

  useEffect(() => {
    setSelectedStories(prev => {
      if (prev.length <= formData.max_stories) {
        return prev;
      }
      return prev.slice(0, formData.max_stories);
    });
  }, [formData.max_stories]);

  const selectedStoryObjects = filteredStories.filter(story => selectedStories.includes(story.id));

  const scoreRange = selectedStoryObjects.length > 0
    ? `${Math.min(...selectedStoryObjects.map(story => story.score))}-${Math.max(...selectedStoryObjects.map(story => story.score))}`
    : 'N/A';

  const handleSelectStory = (storyId: string) => {
    setSelectedStories(prev => 
      prev.includes(storyId) 
        ? prev.filter(id => id !== storyId)
        : prev.length >= formData.max_stories
          ? prev
          : [...prev, storyId]
    );
  };

  const handleGenerateNewsletter = async () => {
    if (selectedStories.length === 0) {
      alert('Please select at least one story');
      return;
    }

    setIsGenerating(true);
    try {
      const result = await newslettersApi.generateNewsletter({
        date_from: formData.date_from + 'T00:00:00Z',
        date_to: formData.date_to + 'T23:59:59Z',
        min_score: formData.min_score,
        selected_story_ids: selectedStories,
        editorial_instructions: formData.editorial_instructions,
        max_stories: formData.max_stories,
      });

      setGeneratedNewsletter(result.newsletter.content);
    } catch (error) {
      console.error('Failed to generate newsletter:', error);
      alert('Failed to generate newsletter. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadMarkdown = () => {
    if (!generatedNewsletter) return;

    const blob = new Blob([generatedNewsletter], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `newsletter-${formData.date_from}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">Create Newsletter</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Configuration */}
          <div className="space-y-6">
            {/* Date Range */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <CalendarIcon className="h-5 w-5 mr-2" />
                Date Range
              </h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">From</label>
                  <input
                    type="date"
                    value={formData.date_from}
                    onChange={(e) => setFormData(prev => ({ ...prev, date_from: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">To</label>
                  <input
                    type="date"
                    value={formData.date_to}
                    onChange={(e) => setFormData(prev => ({ ...prev, date_to: e.target.value }))}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Filtering Options */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Story Selection</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Minimum Score
                  </label>
                  <select
                    value={formData.min_score}
                    onChange={(e) => setFormData(prev => ({ ...prev, min_score: parseInt(e.target.value) }))}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  >
                    <option value={90}>90+ (Excellent)</option>
                    <option value={80}>80+ (High)</option>
                    <option value={70}>70+ (Good)</option>
                    <option value={60}>60+ (Moderate)</option>
                    <option value={50}>50+ (Basic)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Max Stories
                  </label>
                  <select
                    value={formData.max_stories}
                    onChange={(e) => setFormData(prev => ({ ...prev, max_stories: parseInt(e.target.value) }))}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  >
                    <option value={5}>5 stories</option>
                    <option value={10}>10 stories</option>
                    <option value={15}>15 stories</option>
                    <option value={20}>20 stories</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Editorial Instructions */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Editorial Instructions</h2>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Tone & Theme (Optional)
                </label>
                <textarea
                  value={formData.editorial_instructions}
                  onChange={(e) => setFormData(prev => ({ ...prev, editorial_instructions: e.target.value }))}
                  rows={4}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="e.g., Focus on practical implications for B2B marketers, use an engaging tone, highlight automation opportunities..."
                />
              </div>
            </div>

            {/* Story Selection Summary */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Selection Summary</h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Available stories:</span>
                  <span className="font-medium">{filteredStories.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Selected stories:</span>
                  <span className="font-medium">{selectedStoryObjects.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Score range:</span>
                  <span className="font-medium">{scoreRange}</span>
                </div>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerateNewsletter}
              disabled={selectedStoryObjects.length === 0 || isGenerating}
              className="w-full inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating Newsletter...
                </>
              ) : (
                <>
                  <DocumentIcon className="h-5 w-5 mr-2" />
                  Generate Newsletter
                </>
              )}
            </button>
          </div>

          {/* Right Column: Story Selection or Newsletter Preview */}
          <div>
            {generatedNewsletter ? (
              /* Newsletter Preview */
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                  <h2 className="text-lg font-medium text-gray-900">Newsletter Preview</h2>
                  <button
                    onClick={handleDownloadMarkdown}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Download Markdown
                  </button>
                </div>
                <div className="p-6">
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap font-sans text-sm text-gray-900">
                      {generatedNewsletter}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              /* Story Selection */
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">
                    Select Stories ({selectedStoryObjects.length} selected)
                  </h2>
                </div>
                <div className="p-6">
                  {isLoading ? (
                    <div className="text-center py-8">
                      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      <p className="mt-2 text-sm text-gray-500">Loading stories...</p>
                    </div>
                  ) : filteredStories.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-sm text-gray-500">
                        No stories found for the selected date range and score threshold.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {filteredStories.map((story) => (
                        <div
                          key={story.id}
                          className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                            selectedStories.includes(story.id) 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => handleSelectStory(story.id)}
                        >
                          <div className="flex items-start space-x-3">
                            <input
                              type="checkbox"
                              checked={selectedStories.includes(story.id)}
                              onChange={() => handleSelectStory(story.id)}
                              className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between">
                                <h3 className="text-sm font-medium text-gray-900 truncate">
                                  {story.title}
                                </h3>
                                <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  story.score >= 90 ? 'bg-green-100 text-green-800' :
                                  story.score >= 80 ? 'bg-blue-100 text-blue-800' :
                                  'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {story.score}/100
                                </span>
                              </div>
                              <p className="mt-1 text-xs text-gray-500">
                                {story.source_name} • {new Date(story.published_date).toLocaleDateString()}
                              </p>
                              <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                                {story.description}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsletterCreate;
