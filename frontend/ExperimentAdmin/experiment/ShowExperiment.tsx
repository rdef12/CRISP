import { Card } from "@/components/ui/card"
import { CreateRealBeamRun } from "./CreateRealBeamRun"
import { ListBeamRun } from "./ListBeamRun"
import { CreateTestBeamRun } from "./CreateTestBeamRun"

export const ShowExperiment = () => {
  return (
    <div>
      <Card>
        <CreateRealBeamRun/>
        <CreateTestBeamRun/>
      </Card>
      <ListBeamRun />
    </div>
  )
}