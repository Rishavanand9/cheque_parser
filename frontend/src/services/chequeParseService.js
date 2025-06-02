export const parseChequePDF = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
  
  const API_URL = process.env.REACT_APP_API_URL;
    const response = await fetch(`${API_URL}/api/parse-cheque`, {
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