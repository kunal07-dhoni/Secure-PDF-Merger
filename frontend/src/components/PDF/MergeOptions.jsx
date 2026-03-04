import React, { useState } from 'react';
import { Settings, FileOutput, Droplets, Minimize2 } from 'lucide-react';
import Button from '../UI/Button';

export default function MergeOptions({ onMerge, loading, disabled }) {
  const [outputFilename, setOutputFilename] = useState('merged_output');
  const [watermarkText, setWatermarkText] = useState('');
  const [compress, setCompress] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleMerge = () => {
    onMerge({
      outputFilename: outputFilename ? `${outputFilename}.pdf` : 'merged_output.pdf',
      watermarkText: watermarkText || null,
      compress,
    });
  };

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Settings className="w-5 h-5 text-primary-600" />
        <h3 className="font-semibold">Merge Options</h3>
      </div>

      {/* Output filename */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          <FileOutput className="w-4 h-4 inline mr-1" />
          Output Filename
        </label>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={outputFilename}
            onChange={(e) => setOutputFilename(e.target.value)}
            className="input-field flex-1"
            placeholder="merged_output"
          />
          <span className="text-sm text-gray-400">.pdf</span>
        </div>
      </div>

      {/* Advanced toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-primary-600 hover:text-primary-700 font-medium"
      >
        {showAdvanced ? 'Hide' : 'Show'} Advanced Options
      </button>

      {showAdvanced && (
        <div className="space-y-4 pt-2 border-t border-gray-200 dark:border-gray-700">
          {/* Watermark */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              <Droplets className="w-4 h-4 inline mr-1" />
              Watermark Text (optional)
            </label>
            <input
              type="text"
              value={watermarkText}
              onChange={(e) => setWatermarkText(e.target.value)}
              className="input-field"
              placeholder="e.g., CONFIDENTIAL"
            />
          </div>

          {/* Compress */}
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={compress}
              onChange={(e) => setCompress(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <div>
              <span className="text-sm font-medium flex items-center gap-1">
                <Minimize2 className="w-4 h-4" />
                Compress Output
              </span>
              <span className="text-xs text-gray-500">
                Reduce file size (may slightly affect quality)
              </span>
            </div>
          </label>
        </div>
      )}

      <Button
        onClick={handleMerge}
        loading={loading}
        disabled={disabled}
        className="w-full"
        size="lg"
      >
        🔗 Merge PDFs
      </Button>
    </div>
  );
}