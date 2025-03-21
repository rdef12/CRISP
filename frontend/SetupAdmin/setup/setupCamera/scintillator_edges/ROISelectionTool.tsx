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
      // Call updateROI when record changes to show the lines
      updateROI({
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
        t: 20,
        b: 40,
        l: 40,
        r: 40,
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
      },
      shapes: [
        {
          type: "line",
          x0: roi.hStart,
          x1: roi.hStart,
          y0: height,
          y1: 0,
          line: { color: "red", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: roi.hEnd,
          x1: roi.hEnd,
          y0: height,
          y1: 0,
          line: { color: "red", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: 0,
          x1: width,
          y0: roi.vStart,
          y1: roi.vStart,
          line: { color: "blue", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: 0,
          x1: width,
          y0: roi.vEnd,
          y1: roi.vEnd,
          line: { color: "blue", width: 2, dash: "dash" },
        },
      ],
    };
    setCurrentLayout(layout);
  };

  useEffect(() => {
    if (image && width && height) {
      initializeLayout();
    }
  }, [image, width, height]);

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

  const updateROI = (newRoi: ROI) => {
    const { hStart, hEnd, vStart, vEnd } = newRoi;
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
    setCurrentLayout(updatedLayout);
  };
  
  const handleROIChange = (name: string, value: number) => {
    setRoi((prevState) => {
      const newState = { ...prevState, [name]: value };
      updateROI(newState);
      return newState;
    });
  };

  const RoiInput = ({ inputSource, label, roiParamName }: {inputSource: string, label: string, roiParamName: keyof ROI}) => {
    const { field } = useInput({ source: inputSource });
    const currentValue = roi[roiParamName];

    return (
      <div>
        <label className="text-sm font-medium mb-1">{label}</label>
        <div className="grid grid-cols-2 gap-2">
          <Slider
            name={inputSource}
            min={0}
            max={roiParamName.startsWith('h') ? width : height}
            value={[currentValue]}
            step={1}
            onValueChange={(value) => {
              const newValue = value[0];
              field.onChange(newValue);
              handleROIChange(roiParamName, newValue);
            }}
            className="w-full"
          />
          <Input
            {...field}
            type="number"
            name={inputSource}
            placeholder="0"
            value={currentValue}
            onChange={(e) => {
              const value = e.target.value === '' ? 0 : parseInt(e.target.value);
              field.onChange(value);
              handleROIChange(roiParamName, value);
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

