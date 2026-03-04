import React from 'react';
import HistoryItem from './HistoryItem';

export default function HistoryTable({ items, onDownload, onDelete }) {
  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No merge history yet</p>
        <p className="text-sm text-gray-400 mt-1">
          Your merged PDFs will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <HistoryItem
          key={item.id}
          item={item}
          onDownload={onDownload}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}