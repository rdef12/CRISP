import { Admin, Resource, ListGuesser, EditGuesser } from "react-admin"
import simpleRestProvider from "ra-data-simple-rest";
import { Route } from 'react-router-dom';
import { Camera } from "./Camera"
import { CameraSetupList } from "./CameraSetup";


const dataProvider = simpleRestProvider(`${process.env.NEXT_PUBLIC_BACKEND}`);

const DefinedData = () => (
  <Admin dataProvider={dataProvider}>
    <Resource name="setup_hub" list={ListGuesser} edit={EditGuesser}>
      <Route path=":id/cameras" element={<CameraSetupList />} />
      <Route path=":id/cameras/:cameraId" element={<Camera />} />
    </Resource>
  </Admin>
);

export default DefinedData;