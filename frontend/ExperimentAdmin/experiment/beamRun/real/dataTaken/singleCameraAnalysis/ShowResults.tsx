import { Card } from "@/components/ui/card"

interface ShowResultsProps {
  beamAngle: number;
  beamAngleUncertainty: number;
  braggPeakPixel: number[];
  braggPeakPixelUncertainty: number[];
}

export const ShowResults = ({
  beamAngle,
  beamAngleUncertainty,
  braggPeakPixel,
  braggPeakPixelUncertainty,
} : ShowResultsProps) => {

  return (
    <div className="space-y-4">
        <Card className="p-4">
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">Beam Angle</h3>
              <p className="text-sm">
                {beamAngle?.toFixed(2)} ± {beamAngleUncertainty?.toFixed(2)} degrees
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Bragg Peak Pixel</h3>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-sm font-medium">X Position:</p>
                  <p className="text-sm">
                    {braggPeakPixel[0]} ± {braggPeakPixelUncertainty[0]}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Y Position:</p>
                  <p className="text-sm">
                    {braggPeakPixel[1]} ± {braggPeakPixelUncertainty[1]}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Card>
    </div>
  )
}