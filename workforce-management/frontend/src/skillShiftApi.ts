import axios from 'axios';

const API_BASE = 'http://localhost:8080/api';

export const fetchSkills = async () => {
  const res = await axios.get(`${API_BASE}/skills`);
  return res.data;
};

export const fetchShifts = async () => {
  const res = await axios.get(`${API_BASE}/shifts`);
  return res.data;
};
