export const processImage = async (file: File): Promise<string> => {
  const formData = new FormData();
  formData.append('image', file);

  try {
    const response = await fetch('/api/process', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Failed to process image on the server');
    }
    
    const data = await response.json();
    if (!data.processed) {
      throw new Error('Invalid response from server');
    }
    
    return data.processed;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const downloadImage = (dataUrl: string, filename: string = 'processed-image.png') => {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
