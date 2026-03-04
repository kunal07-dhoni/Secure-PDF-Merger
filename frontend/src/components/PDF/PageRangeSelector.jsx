import React from 'react';

export default function PageRangeSelector({ file, pageRange, onChange }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-gray-500 min-w-[80px] truncate">{file.filename}:</span>
      <input
        type="number"
        min={1}
        max={file.page_count}
        value={pageRange?.start_page || ''}
        onChange={(e) =>
          onChange({
            file_index: file.index,
            start_page: parseInt(e.target.value) || null,
            end_page: pageRange?.end_page || null,
          })
        }
        className="w-16 px-2 py-1 border rounded text-center input-field"
        placeholder="Start"
      />
      <span className="text-gray-400">to</span>
      <input
        type="number"
        min={1}
        max={file.page_count}
        value={pageRange?.end_page || ''}
        onChange={(e) =>
          onChange({
            file_index: file.index,
            start_page: pageRange?.start_page || null,
            end_page: parseInt(e.target.value) || null,
          })
        }
        className="w-16 px-2 py-1 border rounded text-center input-field"
        placeholder="End"
      />
      <span className="text-gray-400">of {file.page_count}</span>
    </div>
  );
}