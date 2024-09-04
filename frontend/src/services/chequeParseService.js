export const parseChequePDF = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
  
    const response = await fetch('http://172.105.50.148:5050/api/parse-cheque', {
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