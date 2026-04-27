import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/audit/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const runAudit = async (datasetId, config) => {
  const formData = new FormData();
  formData.append('dataset_id', datasetId);
  formData.append('protected_col', config.protected_col);
  formData.append('target_col', config.target_col);
  formData.append('priv_val', config.priv_val);
  formData.append('fav_outcome', config.fav_outcome);
  formData.append('qualification_cols', JSON.stringify(config.qualification_cols || []));

  const response = await axios.post(`${API_BASE_URL}/audit/run`, formData);
  return response.data;
};

export const simulateScenario = async (datasetId, config, featureToDrop) => {
  const formData = new FormData();
  formData.append('dataset_id', datasetId);
  formData.append('protected_col', config.protected_col);
  formData.append('target_col', config.target_col);
  formData.append('priv_val', config.priv_val);
  formData.append('fav_outcome', config.fav_outcome);
  formData.append('feature_to_drop', featureToDrop);

  const response = await axios.post(`${API_BASE_URL}/audit/simulate`, formData);
  return response.data;
};
