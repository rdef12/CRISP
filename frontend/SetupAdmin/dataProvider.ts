import simpleRestProvider from 'ra-data-simple-rest';
import { DataProvider } from 'react-admin';
import { fetchUtils } from 'react-admin';

interface CustomDataProvider extends DataProvider {
  getHomographyPhoto: (plane: string, id: string, params: Record<string, string>) => Promise<{ data: any }>;
}

const baseDataProvider = simpleRestProvider(`${process.env.NEXT_PUBLIC_BACKEND}`);

const dataProvider: CustomDataProvider = {
  ...baseDataProvider,
  
  getHomographyPhoto: async (plane, id, params) => {
    const queryString = new URLSearchParams(params).toString();
    const url = `${process.env.NEXT_PUBLIC_BACKEND}/photo/homography-calibration/${plane}/${id}?${queryString}`;
    
    const { json } = await fetchUtils.fetchJson(url);
    return { data: json };
  }
};

export default dataProvider;