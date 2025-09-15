import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { newslettersApi } from '../services/api';
import { 
  CalendarIcon, 
  DocumentTextIcon, 
  ArrowDownTrayIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const Newsletters: React.FC = () => {
  const { data: newslettersData, isLoading, error } = useQuery(
    'newsletters',
    newslettersApi.getNewsletters
  );

  const handleDownload = async (newsletterId: string) => {
    try {
      const markdown = await newslettersApi.downloadMarkdown(newsletterId);
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${newsletterId}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download newsletter:', error);
      alert('Failed to download newsletter');
    }
  };

  if (error) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="text-center py-12">
          <div className="text-red-500 mb-4">Failed to load newsletters</div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Newsletters</h1>
          <p className="mt-2 text-sm text-gray-700">
            View and download previously generated newsletters
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            to="/create-newsletter"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            Create New Newsletter
          </Link>
        </div>
      </div>

      {/* Newsletters List */}
      <div className="mt-8">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-sm text-gray-500">Loading newsletters...</p>
          </div>
        ) : !newslettersData?.newsletters.length ? (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No newsletters yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Create your first newsletter from AI marketing stories.
            </p>
            <div className="mt-6">
              <Link
                to="/create-newsletter"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <DocumentTextIcon className="h-4 w-4 mr-2" />
                Create Newsletter
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {newslettersData.newsletters.map((newsletter) => (
              <NewsletterCard
                key={newsletter.newsletter_id}
                newsletter={newsletter}
                onDownload={handleDownload}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

interface NewsletterCardProps {
  newsletter: any;
  onDownload: (id: string) => void;
}

const NewsletterCard: React.FC<NewsletterCardProps> = ({ newsletter, onDownload }) => {
  const [showPreview, setShowPreview] = React.useState(false);
  const [previewContent, setPreviewContent] = React.useState<string>('');
  const [isLoadingPreview, setIsLoadingPreview] = React.useState(false);

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  const loadPreview = async () => {
    if (previewContent) {
      setShowPreview(!showPreview);
      return;
    }

    setIsLoadingPreview(true);
    try {
      const result = await newslettersApi.getNewsletter(newsletter.newsletter_id);
      setPreviewContent(result.newsletter.content);
      setShowPreview(true);
    } catch (error) {
      console.error('Failed to load preview:', error);
      alert('Failed to load preview');
    } finally {
      setIsLoadingPreview(false);
    }
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                Newsletter {newsletter.newsletter_id}
              </h3>
              <div className="flex items-center text-sm text-gray-500 mt-1">
                <CalendarIcon className="h-4 w-4 mr-1" />
                {formatDate(newsletter.generated_date)}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4">
          <div className="text-sm text-gray-500">
            <div className="flex justify-between">
              <span>Stories:</span>
              <span className="font-medium">{newsletter.story_count}</span>
            </div>
            {newsletter.metadata?.date_from && newsletter.metadata?.date_to && (
              <div className="flex justify-between mt-1">
                <span>Date range:</span>
                <span className="font-medium">
                  {formatDate(newsletter.metadata.date_from)} - {formatDate(newsletter.metadata.date_to)}
                </span>
              </div>
            )}
            {newsletter.metadata?.min_score && (
              <div className="flex justify-between mt-1">
                <span>Min score:</span>
                <span className="font-medium">{newsletter.metadata.min_score}</span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 flex space-x-3">
          <button
            onClick={loadPreview}
            disabled={isLoadingPreview}
            className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoadingPreview ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
            ) : (
              <>
                <EyeIcon className="h-4 w-4 mr-2" />
                {showPreview ? 'Hide' : 'Preview'}
              </>
            )}
          </button>
          <button
            onClick={() => onDownload(newsletter.newsletter_id)}
            className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Download
          </button>
        </div>

        {showPreview && previewContent && (
          <div className="mt-6 border-t border-gray-200 pt-6">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Preview:</h4>
            <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-xs text-gray-700 font-sans">
                {previewContent.length > 1000 
                  ? previewContent.substring(0, 1000) + '...\n\n[Content truncated - download for full newsletter]'
                  : previewContent
                }
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Newsletters;