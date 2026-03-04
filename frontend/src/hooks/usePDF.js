import { useState, useCallback } from 'react';
import { pdfAPI } from '../api/pdf';
import { useToast } from './useToast';

export function usePDF() {
  const [files, setFiles] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [merging, setMerging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [mergeResult, setMergeResult] = useState(null);
  const toast = useToast();

  const uploadFiles = useCallback(async (selectedFiles) => {
    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await pdfAPI.upload(selectedFiles, (progressEvent) => {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setUploadProgress(percent);
      });

      const { session_id, files: fileInfos } = response.data;
      setSessionId(session_id);
      setFiles(fileInfos.filter((f) => f.is_valid));

      const invalidFiles = fileInfos.filter((f) => !f.is_valid);
      if (invalidFiles.length > 0) {
        toast.error(
          `${invalidFiles.length} file(s) were invalid and skipped`
        );
      }

      toast.success(`${fileInfos.filter((f) => f.is_valid).length} files uploaded successfully`);
      return response.data;
    } catch (error) {
      const msg = error.response?.data?.detail || 'Upload failed';
      toast.error(msg);
      throw error;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [toast]);

  const mergePDFs = useCallback(
    async (options = {}) => {
      if (!sessionId || files.length < 2) {
        toast.error('Need at least 2 files to merge');
        return;
      }

      setMerging(true);

      try {
        const response = await pdfAPI.merge({
          sessionId,
          fileOrder: files.map((f) => f.index),
          outputFilename: options.outputFilename || 'merged_output.pdf',
          pageRanges: options.pageRanges || null,
          watermarkText: options.watermarkText || null,
          compress: options.compress || false,
        });

        setMergeResult(response.data);
        toast.success(response.data.message);
        return response.data;
      } catch (error) {
        const msg = error.response?.data?.detail || 'Merge failed';
        toast.error(msg);
        throw error;
      } finally {
        setMerging(false);
      }
    },
    [sessionId, files, toast]
  );

  const reorderFiles = useCallback((newOrder) => {
    setFiles(newOrder);
  }, []);

  const removeFile = useCallback((index) => {
    setFiles((prev) => prev.filter((f) => f.index !== index));
  }, []);

  const reset = useCallback(() => {
    if (sessionId) {
      pdfAPI.cleanupSession(sessionId).catch(() => {});
    }
    setFiles([]);
    setSessionId(null);
    setMergeResult(null);
  }, [sessionId]);

  return {
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
  };
}