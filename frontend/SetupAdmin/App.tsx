import { Admin, Resource } from "react-admin"
import simpleRestProvider from "ra-data-simple-rest";
import { Route } from 'react-router-dom';
// import { Camera } from "./Camera";
import { 
  // SetupCameraDetail,
  SetupCameraShow,
  NearFaceTestContent,
  FarFaceTestContent,
  // ScintillatorEdgesTestContent,
  SetupShow
} from "./setup/setupCamera/setupCamera";
import { SetupCreate, SetupList } from "./setup/setup";
import CustomAdminLayout from "./CustomLayout";
// import { CreateSettingsScintillatorEdges } from "./setup/setupCamera/scintillator_edges/CreateSettingsScintillatorEdges";
import { ScintillatorEdges } from "./setup/setupCamera/scintillatorEdges/ScintillatorEdges";
import { DistortionCalibration } from "./setup/setupCamera/distortionCalibration/DistortionCalibration";
import { HomographyCalibration, HomographyPlane } from "./setup/setupCamera/homography/HomographyCalibration";
// import { CameraSetupList } from "./CameraSetup";

const dataProvider = simpleRestProvider(`${process.env.NEXT_PUBLIC_BACKEND}`);

const AdminApp = () => (
  <Admin
   dataProvider={dataProvider}
    layout={CustomAdminLayout}
    >
    <Resource options={{ label: 'Setups' }}  name="setup" create={SetupCreate} list={SetupList} hasCreate> {/* show={SetupShow} edit={SetupEdit} */}
      <Route path=":setupId" element={<SetupShow />} />
      <Route path=":setupId/setup-camera/:setupCameraId" element={<SetupCameraShow />} />

      <Route path=":setupId/setup-camera/:setupCameraId/near-face" element={<HomographyCalibration plane={HomographyPlane.Near} />} /> {/*NearFaceCalibration*/} 
      {/* <Route path=":setupId/setup-camera/:setupCameraId/near-face/settingsId" element={<NearFaceTestContent/>} /> NOT THIS PAGE OBVS  */}
      
      <Route path=":setupId/setup-camera/:setupCameraId/far-face" element={<HomographyCalibration plane={HomographyPlane.Far} />} /> {/*FarFaceCalibration*/}
      {/* <Route path=":setupId/setup-camera/:setupCameraId/far-face/settingsId" element={<FarFaceTestContent/>} /> NOT THIS PAGE OBVS */}

      <Route path=":setupId/setup-camera/:setupCameraId/distortion-calibration" element={<DistortionCalibration />} /> {/*DistortionCalibration*/}
      {/* <Route path=":setupId/setup-camera/:setupCameraId/distortion/settingsId" element={<DistortionTestContent/>} /> NOT THIS PAGE OBVS */}

      <Route path=":setupId/setup-camera/:setupCameraId/scintillator-edges/" element={<ScintillatorEdges/>} /> {/*ScintillatorEdgeCalibration  ScintillatorEdgesTestContent*/}
      {/* <Route path=":setupId/setup-camera/:setupCameraId/scintillator-edges/create" element={<CreateSettingsScintillatorEdges/>} /> ScintillatorEdgeCalibration  ScintillatorEdgesTestContent */}
      {/* <Route path=":setupId/setup-camera/:setupCameraId/scintillator-edges/edit" element={<ScintillatorEdgesTestContent/>} />NOT THIS PAGE OBVS */}
     {/*I think maybe these should be /settingsId cna maybe */}
    </Resource>
    <Resource options={{ label: 'Cameras' }} name="camera"/>
    <Resource options={{ label: 'Camera and Settings' }} name="camera-settings" /> {/*changed from name=camera_settings*/}
    <Resource options={{ label: 'Settings' }} name="settings" />
    <Resource options={{ label: 'Photos' }} name="photo" />
  </Admin>
);

export default AdminApp;