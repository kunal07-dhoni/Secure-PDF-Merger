import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePDF } from '../hooks/usePDF';
import { useToast } from '../hooks/useToast';
import { historyAPI } from '../api/history';
import DropZone from '../components/PDF/DropZone';
import FileList from '../components/PDF/FileList';
import MergeOptions from '../components/PDF/MergeOptions';
import PDFPreview from '../components/PDF/PDFPreview';
import Button from '../components/UI/Button';
import Spinner from '../components/UI/Spinner';
import {
  CheckCircle2,
  Download,
  RefreshCw,
  ArrowRight,
  FileText,
} from 'lucide-react';
import { formatFileSize } from '../utils/helpers';

export default function MergePDF() {
  const {
    files,
    sessionId,
    uploading,
    merging,
    uploadProgress,
    mergeResult,
    uploadFiles,
    mergePDFs,
    reorderFiles,
    removeFile,
    reset,
  } = usePDF();

  const toast = useToast();
  const navigate = useNavigate();
  const [previewFile, setPreviewFile] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const handleFilesAccepted = async (acceptedFiles) => {
    try {
      await uploadFiles(acceptedFiles);
    } catch (err) {
      // Handled in hook
    }
  };

  const handleMerge = async (options) => {
    try {
      await mergePDFs(options);
    } catch (err) {
      // Handled in hook
    }
  };

  const handleDownload = async () => {
    if (!mergeResult) return;
    setDownloading(true);

    try {
      // Get the history to find the record for download
      const historyResp = await historyAPI.getHistory(1, 1);
      if (historyResp.data.items.length > 0) {
        const latestRecord = historyResp.data.items[0];
        const response = await historyAPI.downloadFile(latestRecord.id);

        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', mergeResult.filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        toast.success('Download started!');
      }
    } catch (err) {
      toast.error('Download failed. Check your history page.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileText className="w-7 h-7 text-primary-600" />
          Merge PDFs
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Upload, reorder, and merge your PDF files securely
        </p>
      </div>

      {/* Success State */}
      {mergeResult && (
        <div className="card border-2 border-green-300 dark:border-green-700 mb-8">
          <div className="text-center py-6">
            <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-green-700 dark:text-green-400 mb-2">
              PDFs Merged Successfully!
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              {mergeResult.message}
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Output: {mergeResult.filename} ({formatFileSize(mergeResult.file_size_bytes)})
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Button onClick={handleDownload} loading={downloading} size="lg">
                <Download className="w-5 h-5" />
                Download Merged PDF
              </Button>
              <Button variant="secondary" onClick={reset}>
                <RefreshCw className="w-5 h-5" />
                Merge More Files
              </Button>
              <Button
                variant="ghost"
                onClick={() => navigate('/history')}
              >
                View History
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Upload & Merge Flow */}
      {!mergeResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Upload & File List */}
          <div className="lg:col-span-2 space-y-6">
            <DropZone
              onFilesAccepted={handleFilesAccepted}
              disabled={uploading || merging}
            />

            {/* Upload Progress */}
            {uploading && (
              <div className="card">
                <div className="flex items-center gap-3 mb-3">
                  <Spinner size="sm" />
                  <span className="text-sm font-medium">Uploading files...</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{uploadProgress}%</p>
              </div>
            )}

            {/* File List */}
            {files.length > 0 && (
              <div className="card">
                <FileList
                  files={files}
                  onReorder={reorderFiles}
                  onRemove={removeFile}
                  onPreview={(file) => setPreviewFile(file)}
                />
              </div>
            )}

            {/* Merging indicator */}
            {merging && (
              <div className="card text-center py-8">
                <Spinner size="lg" className="mx-auto mb-4" />
                <p className="font-medium">Merging your PDFs...</p>
                <p className="text-sm text-gray-500 mt-1">This may take a moment</p>
              </div>
            )}
          </div>

          {/* Right: Options */}
          <div className="lg:col-span-1">
            {files.length >= 2 && (
              <MergeOptions
                onMerge={handleMerge}
                loading={merging}
                disabled={files.length < 2 || uploading}
              />
            )}

            {files.length === 1 && (
              <div className="card text-center">
                <p className="text-sm text-gray-500">
                  Upload at least one more PDF to merge
                </p>
              </div>
            )}

            {files.length === 0 && !uploading && (
              <div className="card text-center">
                <FileText className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Upload PDF files to get started
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Preview Modal */}
      <PDFPreview
        isOpen={!!previewFile}
        onClose={() => setPreviewFile(null)}
        sessionId={sessionId}
        file={previewFile}
      />
    </div>
  );
}