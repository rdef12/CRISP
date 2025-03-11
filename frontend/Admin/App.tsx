import { Admin, Resource } from "react-admin"
import simpleRestProvider from "ra-data-simple-rest";
import { Route } from 'react-router-dom';
// import { Camera } from "./Camera";
import { 
  // SetupCameraDetail,
  SetupCameraShow,
  NearFaceTestContent,
  FarFaceTestContent,
  DistortionTestContent,
  ScintillatorEdgesTestContent,
  SetupShow
} from "./setup/setupCamera/setupCamera";
import { SetupCreate, SetupList } from "./setup/setup";
import CustomAdminLayout from "./CustomLayout";
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
      <Route path=":setupId/setup-camera/:setupCameraId/near-face" element={<NearFaceTestContent/>} /> {/*NearFaceCalibration*/} 
      <Route path=":setupId/setup-camera/:setupCameraId/far-face" element={<FarFaceTestContent/>} /> {/*FarFaceCalibration*/}
      <Route path=":setupId/setup-camera/:setupCameraId/distortion" element={<DistortionTestContent/>} /> {/*DistortionCalibration*/}
      <Route path=":setupId/setup-camera/:setupCameraId/scintillator-edges" element={<ScintillatorEdgesTestContent/>} /> {/*ScintillatorEdgeCalibration*/}
    
    </Resource>
    <Resource options={{ label: 'Cameras'}} name="camera"/>
  </Admin>
);

export default AdminApp;