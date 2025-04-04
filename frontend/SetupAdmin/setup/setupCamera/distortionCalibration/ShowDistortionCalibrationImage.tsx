interface ShowDistortionCalibrationImageProps {
  imageUrl: string;
  isPending: boolean;
}

export const ShowDistortionCalibrationImage = ({ imageUrl, isPending }: ShowDistortionCalibrationImageProps) => {
  return (
    <div className="flex items-center justify-center h-[400px] border-4 border-dashed border-gray-200 rounded">
      {isPending ? (
        <div className="text-center text-gray-600">
          Taking picture...
        </div>
      ) : imageUrl ? (
        <img
          src={imageUrl}
          alt="Distortion calibration image"
          className="max-w-full max-h-[400px] object-contain border-4 border-green-400 rounded"
          onError={(e) => console.error("Image failed to load:", e)}
        />
      ) : (
        <div className="text-center text-gray-600">
          No image available yet
        </div>
      )}
    </div>
  );
}