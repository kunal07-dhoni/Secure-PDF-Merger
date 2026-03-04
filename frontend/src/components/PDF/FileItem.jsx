import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, FileText, X, Eye } from 'lucide-react';
import { formatFileSize, truncateFilename } from '../../utils/helpers';

export default function FileItem({ file, onRemove, onPreview }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: file.index });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 50 : 'auto',
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg border
                  border-gray-200 dark:border-gray-700 group
                  ${isDragging ? 'shadow-lg ring-2 ring-primary-500' : 'hover:shadow-md'}
                  transition-shadow duration-200`}
    >
      {/* Drag handle */}
      <button
        {...attributes}
        {...listeners}
        className="cursor-grab active:cursor-grabbing p-1 rounded hover:bg-gray-100
                   dark:hover:bg-gray-700 text-gray-400 hover:text-gray-600
                   dark:hover:text-gray-300 transition-colors"
      >
        <GripVertical className="w-5 h-5" />
      </button>

      {/* File icon */}
      <div className="p-2 bg-red-50 dark:bg-red-900/30 rounded-lg shrink-0">
        <FileText className="w-5 h-5 text-red-500" />
      </div>

      {/* File info */}
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm truncate" title={file.filename}>
          {truncateFilename(file.filename, 40)}
        </p>
        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          <span>{formatFileSize(file.size_bytes)}</span>
          <span>•</span>
          <span>{file.page_count} page{file.page_count !== 1 ? 's' : ''}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {onPreview && (
          <button
            onClick={() => onPreview(file)}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
                       text-gray-400 hover:text-primary-600 transition-colors"
            title="Preview"
          >
            <Eye className="w-4 h-4" />
          </button>
        )}
        <button
          onClick={() => onRemove(file.index)}
          className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20
                     text-gray-400 hover:text-red-600 transition-colors"
          title="Remove"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}