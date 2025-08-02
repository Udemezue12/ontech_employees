import axios from 'axios';

const API_BASE_URL = 'https://country-api-1.onrender.com';

export const fetchCountries = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/country/countries`);
        return response.data;  
    } catch (error) {
        console.error('Error fetching countries:', error);
        return [];
    }
};

export const fetchStates = async (country) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/state/get_states/${country}`);  
       
        return response.data;  
    } catch (error) {
        console.error('Error fetching states:', error);
        return [];
    }
};
