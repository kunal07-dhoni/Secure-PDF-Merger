import React, { useState, useEffect } from 'react';
import { pdfAPI } from '../../api/pdf';
import Modal from '../UI/Modal';
import Spinner from '../UI/Spinner';
import { FileText, Hash, HardDrive } from 'lucide-react';
import { formatFileSize } from '../../utils/helpers';

export default function PDFPreview({ isOpen, onClose, sessionId, file }) {
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && sessionId && file) {
      loadPreview();
    }
  }, [isOpen, sessionId, file]);

  const loadPreview = async () => {
    setLoading(true);
    try {
      const response = await pdfAPI.preview(sessionId, file.index);
      setPreviewData(response.data);
    } catch (err) {
      console.error('Preview error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="PDF Preview" size="lg">
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : previewData ? (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="card text-center">
              <FileText className="w-6 h-6 mx-auto text-primary-500 mb-2" />
              <p className="text-2xl font-bold">{previewData.page_count}</p>
              <p className="text-xs text-gray-500">Pages</p>
            </div>
            <div className="card text-center">
              <HardDrive className="w-6 h-6 mx-auto text-primary-500 mb-2" />
              <p className="text-2xl font-bold">{formatFileSize(previewData.file_size)}</p>
              <p className="text-xs text-gray-500">Size</p>
            </div>
            <div className="card text-center">
              <Hash className="w-6 h-6 mx-auto text-primary-500 mb-2" />
              <p className="text-sm font-medium truncate">{previewData.filename}</p>
              <p className="text-xs text-gray-500">Filename</p>
            </div>
          </div>

          {previewData.first_page_preview && (
            <div>
              <h4 className="font-medium text-sm mb-2">First Page Content Preview:</h4>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 max-h-48 overflow-y-auto">
                <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                  {previewData.first_page_preview}
                </p>
              </div>
            </div>
          )}

          {previewData.metadata && Object.keys(previewData.metadata).length > 0 && (
            <div>
              <h4 className="font-medium text-sm mb-2">Metadata:</h4>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                {Object.entries(previewData.metadata).map(([key, value]) => (
                  <div key={key} className="flex gap-2 text-sm">
                    <span className="font-medium text-gray-500">{key}:</span>
                    <span className="text-gray-700 dark:text-gray-300">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <p className="text-center text-gray-500 py-8">Unable to load preview</p>
      )}
    </Modal>
  );
}