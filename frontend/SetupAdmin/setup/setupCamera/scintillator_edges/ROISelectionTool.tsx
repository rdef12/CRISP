import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { useParams } from "react-router-dom";
import React, { useEffect, useState } from "react";
import { Form, useEditController, useInput } from "react-admin";
import Plot from "react-plotly.js";

interface ROISelectionToolProps {
  image: string; // Assuming image is a string URL
  width: number;
  height: number;
}

interface ROI {
  hStart: number;
  hEnd: number;
  vStart: number;
  vEnd: number;
}

export const ROISelectionTool: React.FC<ROISelectionToolProps> = ({
  image,
  width,
  height,
}) => {
  
  const { setupCameraId } = useParams();
  const { record, save, isPending} = useEditController({ resource: "setup-camera/calibration", id: setupCameraId, redirect: false});
  console.log("SETUP CAMERA ID: ", setupCameraId)
  console.log("READ ME IM INTERESTING: ", record)
  const [currentLayout, setCurrentLayout] = useState({});
  const [roi, setRoi] = useState<ROI>({
    hStart: record?.horizontal_scintillator_start ?? 0,
    hEnd: record?.horizontal_scintillator_end ?? width,
    vStart: record?.vertical_scintillator_start ?? 0,
    vEnd: record?.vertical_scintillator_end ?? height,
  });
  useEffect(() => {
    if (record) {
      setRoi({
        hStart: record?.horizontal_scintillator_start,
        hEnd: record?.horizontal_scintillator_end,
        vStart: record?.vertical_scintillator_start,
        vEnd: record?.vertical_scintillator_end,
      });
    }
  }, [record]);
  

  const initializeLayout = () => {
    const layout = {
      margin: {
        t: 20, // top margin, reducing the padding (default is usually 80)
        b: 40, // bottom margin
        l: 40, // left margin
        r: 40, // right margin
      },
      images: [
        {
          source: image,
          x: 0,
          y: 0,
          sizex: width,
          sizey: height,
          xref: "x",
          yref: "y",
          layer: "below",
          zorder: 1,
        },
      ],
      xaxis: {
        range: [0, width],
        showgrid: false,
        dtick: 200,
        axiscolor: "red",
        zorder: 2,
        scaleanchor: "y",
        scaleratio: 1,
      },
      yaxis: {
        range: [height, 0],
        showgrid: false,
        dtick: 200,
        axiscolor: "blue",
        zorder: 2,
        scaleanchor: "x",
        scaleratio: 1,
      }, // Reversed y-axis
    };
    setCurrentLayout(layout);
  };

  useEffect(() => {
    if (image && width && height) {
      initializeLayout();
    }
  }, [image, width, height]);

  const updateROI = (newRoi: ROI) => {
    const { hStart, hEnd, vStart, vEnd } = newRoi;
    console.log("UPDATA: hstart, hend, vstart, vend", hStart, hEnd, vStart, vEnd)
    const updatedLayout = {
      ...currentLayout,
      shapes: [
        {
          type: "line",
          x0: hStart,
          x1: hStart,
          y0: height,
          y1: 0,
          line: { color: "red", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: hEnd,
          x1: hEnd,
          y0: height,
          y1: 0,
          line: { color: "red", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: 0,
          x1: width,
          y0: vStart,
          y1: vStart,
          line: { color: "blue", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: 0,
          x1: width,
          y0: vEnd,
          y1: vEnd,
          line: { color: "blue", width: 2, dash: "dash" },
        },
      ],
    };
    setCurrentLayout(updatedLayout); // Update the layout to reflect the changes
  };
  
  const handleROIChange = (name: string, value: number | number[]) => {
    if (Array.isArray(value)) {
      console.log("In Array - Updating", name, "to", value[0]);
      // Handle the array value from slider (e.g., multi-range slider)
      setRoi((prevState) => {
        const newState = { ...prevState, [name]: value[0] };
        updateROI(newState); // Ensure layout is updated after state change
        console.log("In Array post - Updating", name, "to", newState.vStart);
        return newState;
      });
    } else {
      setRoi((prevState) => {
        console.log("In Box - Updating", name, "to", value);
        const newState = { ...prevState, [name]: value };
        updateROI(newState); // Ensure layout is updated after state change
        return newState;
      });
    }
  };

  const RoiInput = ({ inputSource, label, roiParamName }: {inputSource: string, label: string, roiParamName: keyof ROI}) => {
    const { field } = useInput({ source: inputSource });
    return (
      <div>
        <label className="text-sm font-medium mb-1">{label}</label>
        <div className="grid grid-cols-2 gap-2">
          <Slider
            name={inputSource}
            min={0}
            max={roiParamName.startsWith('h') ? width : height}
            value={[roi[roiParamName]]}
            step={1}
            onValueChange={(value) => {
              handleROIChange(roiParamName, value);
              field.onChange(value[0]);
            }}
            className="w-full"
          />
          <Input
            {...field}
            type="number"
            name={inputSource}
            placeholder="0"
            value={roi[roiParamName]}
            onChange={(e) => {
              const value = parseInt(e.target.value);
              handleROIChange(roiParamName, value);
              field.onChange(value);
            }}
            className="w-full border rounded-md px-2 py-1"
          />
        </div>
      </div>
    );
  };

  if (isPending) return null;
  return (
    <div className="flex flex-col items-center min-h-screen py-1">
      {/* Plotly chart container */}
      <div className="flex justify-center mb-4">
        {image && width && height && (
          <Plot
            data={[]}
            layout={{
              ...currentLayout,
              autosize: false,
              width: 600,
              height: (600 * height) / width,
            }}
            useResizeHandler={true}
          />
        )}
      </div>

      {/* Form inputs container */}
      <Form onSubmit={save} sanitizeEmptyValues={true}>
        <div className="grid grid-cols-2 gap-4 mb-2">
          <RoiInput 
            inputSource="horizontal_scintillator_start" 
            label="Horizontal ROI Start" 
            roiParamName="hStart"
          />
          <RoiInput 
            inputSource="horizontal_scintillator_end" 
            label="Horizontal ROI End"
            roiParamName="hEnd"
          />
          <RoiInput 
            inputSource="vertical_scintillator_start" 
            label="Vertical ROI Start"
            roiParamName="vStart"
          />
          <RoiInput 
            inputSource="vertical_scintillator_end" 
            label="Vertical ROI End"
            roiParamName="vEnd"
          />
        </div>

        {/* Save ROI button */}
        <div className="flex justify-center mt-2">
          <button
            className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
            type="submit"
          >
            Save ROI
          </button>
        </div>
      </Form>
    </div>
  );
};

