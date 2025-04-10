import { useParams } from "react-router-dom";
import { ShowHomographyCalibrationImage } from "./ShowHomographyCalibrationImage"
import { ShowHomographyCalibrationSuccess } from "./ShowHomographyCalibrationSuccess"
import { useGetOne } from "react-admin";
import { HomographyPlane } from "./HomographyCalibration";
import { useState, useEffect } from "react";

interface ShowHomographyCalibrationResultsProps {
  plane: HomographyPlane;
  imageTaken: boolean;
  onImageLoaded: () => void;
}

export const ShowHomographyCalibrationResults = ({ plane, imageTaken, onImageLoaded }: ShowHomographyCalibrationResultsProps) => {
  const { setupCameraId } = useParams();
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const { data, isPending, error, refetch } = useGetOne(
    `photo/homography-calibration/${plane}`,
    { id: setupCameraId}
  );

  useEffect(() => {
    if (imageTaken) {
      refetch();
    }
  }, [imageTaken, refetch]);

  useEffect(() => {
    if (data?.photo) {
      const url = `data:image/jpeg;base64,${data.photo}`;
      setImageUrl(url);
      onImageLoaded();
    } else {
      setImageUrl(null);
    }
  }, [data?.photo, onImageLoaded]);

  if (isPending) return <div>Loading...</div>;
  if (error) return <div>Error loading calibration results</div>;
  if (!data) return null;
  return (
    <div>
      {imageUrl ? (
        <ShowHomographyCalibrationImage imageUrl={imageUrl} />
      ) : (
        <div>No calibration image available</div>
      )}
      {data.success !== undefined && (
        <ShowHomographyCalibrationSuccess status={data.status} message={data.message} />
      )}
    </div>
  )
}