import client from './client';

export const pdfAPI = {
  upload: (files, onProgress) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));

    return client.post('/pdf/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress,
    });
  },

  merge: (data) => {
    const formData = new FormData();
    formData.append('session_id', data.sessionId);
    formData.append('file_order', JSON.stringify(data.fileOrder));
    formData.append('output_filename', data.outputFilename || 'merged_output.pdf');

    if (data.pageRanges) {
      formData.append('page_ranges', JSON.stringify(data.pageRanges));
    }
    if (data.watermarkText) {
      formData.append('watermark_text', data.watermarkText);
    }
    formData.append('compress', data.compress || false);

    return client.post('/pdf/merge', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  preview: (sessionId, fileIndex) =>
    client.get(`/pdf/preview/${sessionId}/${fileIndex}`),

  cleanupSession: (sessionId) =>
    client.delete(`/pdf/session/${sessionId}`),
};