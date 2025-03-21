import { Card } from "@/components/ui/card"
import { CreateRealBeamRun } from "./CreateRealBeamRun"
import { ListBeamRun } from "./ListBeamRun"
import { CreateTestBeamRun } from "./CreateTestBeamRun"
import { ShowSetupSummary } from "./ShowSetupSummary"

export const ShowExperiment = () => {
  return (
    <div>
      <Card>
        <CreateRealBeamRun/>
        <CreateTestBeamRun/>
      </Card>
      <ListBeamRun />
      <ShowSetupSummary/>
    </div>
  )
}