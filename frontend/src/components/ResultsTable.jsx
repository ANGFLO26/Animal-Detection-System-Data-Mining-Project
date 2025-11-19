import React from 'react';

const ResultsTable = ({ detections }) => {
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'bg-green-100 text-green-800 border-green-200';
    if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  if (!detections || detections.length === 0) {
    return null;
  }

  return (
    <div className="p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-bold mb-4 flex items-center text-gray-800">
        <span className="mr-2">📋</span>
        Detected Animals
        <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs sm:text-sm font-medium">
          {detections.length}
        </span>
      </h2>
      
      <div className="space-y-3 max-h-[500px] overflow-y-auto scrollbar-thin">
        {detections.map((detection, index) => (
          <div
            key={detection.id || index}
            className={`border-2 rounded-lg p-3 sm:p-4 transition-all hover:shadow-md ${getConfidenceColor(detection.confidence)}`}
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-base sm:text-lg capitalize">{detection.class}</h3>
              <span className="text-xs font-semibold opacity-75">
                #{index + 1}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs sm:text-sm font-medium opacity-90">Confidence:</span>
              <span className="text-xs sm:text-sm font-bold">
                {(detection.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsTable;
