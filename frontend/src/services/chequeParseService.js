export const parseChequePDF = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
  
    const response = await fetch('http://127.0.0.1:5051/api/parse-cheque', {
      method: 'POST',
      body: formData,
    });
  
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
  
    const data = await response.json();
    if (data.status === 'success') {
      return data.data;
    } else {
      throw new Error(data.message || 'Failed to parse cheque.');
    }
  };