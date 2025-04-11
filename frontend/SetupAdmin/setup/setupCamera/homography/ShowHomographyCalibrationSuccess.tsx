import { Card } from "@/components/ui/card";

interface ShowHomographyCalibrationSuccessProps {
  status: boolean;
  message: string;
}

export const ShowHomographyCalibrationSuccess = ({ status, message }: ShowHomographyCalibrationSuccessProps) => {
  return (
    <Card className="p-4">
      <p style={{ 
        color: status ? '#059669' : '#dc2626',
        fontWeight: '600'
      }}>
        {message}
      </p>
    </Card>
  )
}