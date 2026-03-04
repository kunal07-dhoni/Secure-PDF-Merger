import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import { MAX_FILE_SIZE_MB, MAX_FILES } from '../../utils/constants';

export default function DropZone({ onFilesAccepted, disabled = false }) {
  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        // Handled by react-dropzone
      }
      if (acceptedFiles.length > 0) {
        onFilesAccepted(acceptedFiles);
      }
    },
    [onFilesAccepted]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: MAX_FILE_SIZE_MB * 1024 * 1024,
    maxFiles: MAX_FILES,
    disabled,
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      className={clsx(
        'drop-zone',
        isDragActive && !isDragReject && 'drop-zone-active',
        isDragReject && 'border-red-500 bg-red-50 dark:bg-red-900/20',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />

      <div className="flex flex-col items-center gap-4">
        {isDragReject ? (
          <>
            <AlertCircle className="w-16 h-16 text-red-400" />
            <p className="text-lg font-medium text-red-600">Invalid file type</p>
            <p className="text-sm text-red-500">Only PDF files are accepted</p>
          </>
        ) : isDragActive ? (
          <>
            <Upload className="w-16 h-16 text-primary-500 animate-bounce" />
            <p className="text-lg font-medium text-primary-600">Drop your PDFs here!</p>
          </>
        ) : (
          <>
            <div className="p-4 bg-primary-100 dark:bg-primary-900/50 rounded-full">
              <FileText className="w-12 h-12 text-primary-500" />
            </div>
            <div>
              <p className="text-lg font-medium">
                Drag & drop PDF files here
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                or click to browse files
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-400 dark:text-gray-500">
              <span>Max {MAX_FILE_SIZE_MB}MB per file</span>
              <span>•</span>
              <span>Up to {MAX_FILES} files</span>
              <span>•</span>
              <span>PDF only</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}