import React, { useState } from 'react';
import { Story } from '../types';
import { 
  CalendarIcon, 
  LinkIcon, 
  TagIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

interface StoryCardProps {
  story: Story;
  isSelected?: boolean;
  onSelect?: (storyId: string) => void;
  showCheckbox?: boolean;
}

const StoryCard: React.FC<StoryCardProps> = ({ 
  story, 
  isSelected, 
  onSelect, 
  showCheckbox = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 70) return 'bg-blue-100 text-blue-800';
    if (score >= 50) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1">
            {showCheckbox && (
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onSelect?.(story.id)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            )}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {story.title}
              </h3>
              
              {/* Metadata */}
              <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                <span className="flex items-center">
                  <CalendarIcon className="h-4 w-4 mr-1" />
                  {formatDate(story.published_date)}
                </span>
                <span>{story.source_name}</span>
                <a
                  href={story.canonical_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-blue-600 hover:text-blue-800"
                >
                  <LinkIcon className="h-4 w-4 mr-1" />
                  Read original
                </a>
              </div>
            </div>
          </div>

          {/* Score */}
          {story.score !== undefined && (
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(story.score)}`}>
              {story.score}/100
            </div>
          )}
        </div>

        {/* Description */}
        <p className="text-gray-700 mb-4">
          {story.description}
        </p>

        {/* Marketing Relevance */}
        {story.marketer_relevance.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Marketing Impact:
            </h4>
            <ul className="list-disc list-inside space-y-1">
              {story.marketer_relevance.map((relevance, index) => (
                <li key={index} className="text-sm text-gray-700">
                  {relevance}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Hint */}
        {story.action_hint && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <h4 className="text-sm font-medium text-blue-900 mb-1">
              Suggested Action:
            </h4>
            <p className="text-sm text-blue-800">{story.action_hint}</p>
          </div>
        )}

        {/* Tags */}
        {story.tags.length > 0 && (
          <div className="flex items-center flex-wrap gap-2 mb-4">
            <TagIcon className="h-4 w-4 text-gray-400" />
            {story.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Expand/Collapse Content */}
        {story.content && (
          <div>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center text-sm text-blue-600 hover:text-blue-800 mb-2"
            >
              {isExpanded ? (
                <>
                  <ChevronUpIcon className="h-4 w-4 mr-1" />
                  Hide full content
                </>
              ) : (
                <>
                  <ChevronDownIcon className="h-4 w-4 mr-1" />
                  Show full content
                </>
              )}
            </button>

            {isExpanded && (
              <div className="prose prose-sm max-w-none">
                <div className="text-gray-700 bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                  {story.content.split('\n').map((paragraph, index) => (
                    <p key={index} className="mb-2 last:mb-0">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Score Breakdown */}
        {isExpanded && story.relevance_score !== undefined && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-3">
              Score Breakdown:
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {story.relevance_score}
                </div>
                <div className="text-xs text-gray-500">Relevance</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {story.impact_score}
                </div>
                <div className="text-xs text-gray-500">Impact</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {story.adoption_score}
                </div>
                <div className="text-xs text-gray-500">Adoption</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {story.urgency_score}
                </div>
                <div className="text-xs text-gray-500">Urgency</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {story.credibility_score}
                </div>
                <div className="text-xs text-gray-500">Credibility</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryCard;