import { Admin, Resource } from "react-admin"
import { Route } from 'react-router-dom';
import { 
  SetupCameraShow,
  NearFaceTestContent,
  FarFaceTestContent,
  SetupShow
} from "./setup/setupCamera/setupCamera";
import { SetupCreate, SetupList } from "./setup/setup";
import CustomAdminLayout from "./CustomLayout";
import { ScintillatorEdges } from "./setup/setupCamera/scintillatorEdges/ScintillatorEdges";
import { DistortionCalibration } from "./setup/setupCamera/distortionCalibration/DistortionCalibration";
import { HomographyCalibration, HomographyPlane } from "./setup/setupCamera/homography/HomographyCalibration";
import dataProvider from "./dataProvider";

const AdminApp = () => (
  <Admin
   dataProvider={dataProvider}
    layout={CustomAdminLayout}
    >
    <Resource options={{ label: 'Setups' }}  name="setup" create={SetupCreate} list={SetupList} hasCreate>
      <Route path=":setupId" element={<SetupShow />} />
      <Route path=":setupId/setup-camera/:setupCameraId" element={<SetupCameraShow />} />

      <Route path=":setupId/setup-camera/:setupCameraId/near-face" element={<HomographyCalibration plane={HomographyPlane.Near} />} />
      <Route path=":setupId/setup-camera/:setupCameraId/far-face" element={<HomographyCalibration plane={HomographyPlane.Far} />} />

      <Route path=":setupId/setup-camera/:setupCameraId/distortion-calibration" element={<DistortionCalibration />} />
      <Route path=":setupId/setup-camera/:setupCameraId/scintillator-edges/" element={<ScintillatorEdges/>} />
    </Resource>
    <Resource options={{ label: 'Cameras' }} name="camera"/>
  </Admin>
);

export default AdminApp;