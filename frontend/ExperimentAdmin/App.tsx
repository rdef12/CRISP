import { Admin, Resource } from "react-admin"
import simpleRestProvider from "ra-data-simple-rest";
import { Route } from 'react-router-dom';
import CustomAdminLayout from "./CustomLayout";
import { ExperimentCreate } from "./CreateExperiment";
import { ExperimentList } from "./ListExperiment";
import { ShowExperiment } from "./experiment/ShowExperiment";
import { ShowRealBeamRun } from "./experiment/beamRun/real/ShowRealBeamRun";
import { ShowTestBeamRun } from "./experiment/beamRun/test/ShowTestBeamRun";
import { TakeTestData } from "./experiment/beamRun/test/takeData/TakeTestData";
import { TakeRealData } from "./experiment/beamRun/real/takeData/TakeRealData";

const dataProvider = simpleRestProvider(`${process.env.NEXT_PUBLIC_BACKEND}`);

const AdminApp = () => (
  <Admin
   dataProvider={dataProvider}
    layout={CustomAdminLayout}
    >
    <Resource options={{ label: 'Experiments' }}  name="experiment" 
      create={ExperimentCreate} list={ExperimentList} hasCreate
    >
      <Route path=":experimentId" element={<ShowExperiment />} />
      <Route path=":experimentId/beam-run/test/:beamRunId" element={<ShowTestBeamRun />} />
      <Route path=":experimentId/beam-run/test/:beamRunId/take-data" element={<TakeTestData />} />

      <Route path=":experimentId/beam-run/real/:beamRunId" element={<ShowRealBeamRun />} />
      <Route path=":experimentId/beam-run/real/:beamRunId/take-data" element={<TakeRealData />} />

     </Resource>

  </Admin>
);

export default AdminApp;
