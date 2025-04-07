import { CreateCameraAnalysis } from "./CreateCameraAnalysis"
import { ShowRealRunPhoto } from "./ShowRealRunPhoto"
import { ShowSingleCameraAnalyses } from "./ShowSingleCameraAnalyses"

export const ShowCameraWithData = () => {
  return (
    <div>
      <CreateCameraAnalysis />
      <ShowRealRunPhoto />
      <ShowSingleCameraAnalyses />
    </div>
  )
}