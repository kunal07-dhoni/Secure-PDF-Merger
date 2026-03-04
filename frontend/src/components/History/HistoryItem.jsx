import React, { useState } from 'react';
import {
  FileText,
  Download,
  Trash2,
  Clock,
  Files,
  FileStack,
  AlertCircle,
} from 'lucide-react';
import { formatDate, formatFileSize } from '../../utils/helpers';
import Button from '../UI/Button';

export default function HistoryItem({ item, onDownload, onDelete }) {
  const [deleting, setDeleting] = useState(false);

  const isExpired = item.status === 'expired';
  const isDeleted = item.status === 'deleted';
  const canDownload = item.status === 'completed' && item.download_token;

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onDelete(item.id);
    } finally {
      setDeleting(false);
    }
  };

  let filenames = [];
  try {
    filenames = JSON.parse(item.original_filenames);
  } catch {
    filenames = [];
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        {/* Icon & info */}
        <div className="flex items-start gap-3 flex-1">
          <div
            className={`p-2.5 rounded-lg shrink-0 ${
              isExpired
                ? 'bg-yellow-50 dark:bg-yellow-900/30'
                : 'bg-green-50 dark:bg-green-900/30'
            }`}
          >
            <FileStack
              className={`w-5 h-5 ${
                isExpired ? 'text-yellow-500' : 'text-green-500'
              }`}
            />
          </div>

          <div className="min-w-0 flex-1">
            <h4 className="font-medium text-sm truncate">{item.output_filename}</h4>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Files className="w-3 h-3" />
                {item.file_count} files
              </span>
              <span className="flex items-center gap-1">
                <FileText className="w-3 h-3" />
                {item.total_pages} pages
              </span>
              <span>{formatFileSize(item.output_size_bytes)}</span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDate(item.created_at)}
              </span>
            </div>

            {item.watermark_applied && (
              <span className="inline-block mt-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-0.5 rounded">
                Watermark: {item.watermark_applied}
              </span>
            )}

            {isExpired && (
              <div className="flex items-center gap-1 mt-1 text-xs text-yellow-600 dark:text-yellow-400">
                <AlertCircle className="w-3 h-3" />
                Download expired
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 sm:shrink-0">
          {canDownload && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => onDownload(item.id)}
            >
              <Download className="w-4 h-4" />
              Download
            </Button>
          )}
          <Button
            variant="danger"
            size="sm"
            onClick={handleDelete}
            loading={deleting}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}