import { Card } from "@/components/ui/card"
import { CreateRealBeamRun } from "./CreateRealBeamRun"
import { ListBeamRun } from "./ListBeamRun"
import { CreateTestBeamRun } from "./CreateTestBeamRun"
import { ShowSetupSummary } from "./ShowSetupSummary"
import { Breadcrumbs } from "../components/Breadcrumbs"

export const ShowExperiment = () => {
  return (
    <div>
      <Breadcrumbs />
      <Card>
        <CreateRealBeamRun/>
        <CreateTestBeamRun/>
      </Card>
      <ListBeamRun />
      <ShowSetupSummary/>
    </div>
  )
}
