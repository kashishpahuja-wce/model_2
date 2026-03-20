export const processImage = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        if (!ctx) {
          reject(new Error('Could not get canvas context'));
          return;
        }
        
        canvas.width = img.width;
        canvas.height = img.height;
        
        // Draw original image
        ctx.drawImage(img, 0, 0);
        
        // Apply some filters to "process" the image
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        // Apply brightness and contrast adjustments
        for (let i = 0; i < data.length; i += 4) {
          // Increase brightness slightly
          data[i] = Math.min(255, data[i] * 1.1);     // R
          data[i + 1] = Math.min(255, data[i + 1] * 1.1); // G
          data[i + 2] = Math.min(255, data[i + 2] * 1.1); // B
          
          // Increase contrast
          const factor = 1.2;
          data[i] = Math.min(255, ((data[i] - 128) * factor) + 128);
          data[i + 1] = Math.min(255, ((data[i + 1] - 128) * factor) + 128);
          data[i + 2] = Math.min(255, ((data[i + 2] - 128) * factor) + 128);
        }
        
        ctx.putImageData(imageData, 0, 0);
        
        // Convert to base64
        resolve(canvas.toDataURL('image/png'));
      };
      
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = e.target?.result as string;
    };
    
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsDataURL(file);
  });
};

export const downloadImage = (dataUrl: string, filename: string = 'processed-image.png') => {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
