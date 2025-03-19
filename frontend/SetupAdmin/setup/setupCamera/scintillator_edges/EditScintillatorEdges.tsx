import ROISelectionTool from "./ROISelectionTool"

export const EditScintillatorEdges = () => {
  const imageUrl = "hello_url"
  const imageWidth = 500;
  const imageHeight = 1000;
  const imageVisible = true;
  return (
    <div className="p-1 bg-white shadow-lg rounded-lg">
      {imageVisible && imageHeight && imageWidth ? (
        <ROISelectionTool
          image={imageUrl}
          width={imageWidth}
          height={imageHeight}
          // username={username}
          // setupID={id}
        />
      ) : (
        <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Please take an image of the scintillator in position</p>
      )}
    </div>
  )
}
