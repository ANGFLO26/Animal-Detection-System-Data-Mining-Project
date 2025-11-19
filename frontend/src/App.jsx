import React, { useState, useEffect } from 'react';
import ImageUpload from './components/ImageUpload';
import ImagePreview from './components/ImagePreview';
import ResultsTable from './components/ResultsTable';
import { detectAnimal, detectBatch, getModelInfo } from './services/api';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [originalImage, setOriginalImage] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [detections, setDetections] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [batchFiles, setBatchFiles] = useState([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [batchResults, setBatchResults] = useState(null);
  const [imageStatuses, setImageStatuses] = useState({}); // Track detection status for each image

  useEffect(() => {
    // Load model info on mount
    getModelInfo()
      .then(info => {
        setModelInfo(info);
      })
      .catch(err => {
        console.error('Failed to load model info:', err);
        setError('Cannot connect to backend. Please check the server.');
      });
  }, []);

  // Keyboard shortcuts for navigation
  useEffect(() => {
    if (batchFiles.length <= 1) return;

    const handleKeyPress = (e) => {
      if (!isProcessing && !e.target.matches('input, textarea, select')) {
        if (e.key === 'ArrowLeft' && currentImageIndex > 0) {
          e.preventDefault();
          handlePrevImage();
        } else if (e.key === 'ArrowRight' && currentImageIndex < batchFiles.length - 1) {
          e.preventDefault();
          handleNextImage();
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [batchFiles, currentImageIndex, isProcessing]);

  const handleClearAll = () => {
    setSelectedFile(null);
    setBatchFiles([]);
    setCurrentImageIndex(0);
    setBatchResults(null);
    setOriginalImage(null);
    setResultImage(null);
    setDetections([]);
    setError(null);
    setSuccessMessage(null);
    setImageStatuses({});
  };

  const handleImageSelect = (file) => {
    setSelectedFile(file);
    setBatchFiles([]);
    setCurrentImageIndex(0);
    setBatchResults(null);
    setError(null);
    setResultImage(null);
    setDetections([]);
    setSuccessMessage(null);
    setImageStatuses({});

    // Create preview URL
    const reader = new FileReader();
    reader.onload = (e) => {
      setOriginalImage(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleBatchSelect = (files) => {
    if (files.length > 0) {
      setBatchFiles(files);
      setCurrentImageIndex(0);
      setBatchResults(null);
      setError(null);
      setResultImage(null);
      setDetections([]);
      setSuccessMessage(null);
      setImageStatuses({});
      
      // Load first image preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setOriginalImage(e.target.result);
      };
      reader.readAsDataURL(files[0]);
      setSelectedFile(files[0]);
    }
  };

  // Helper function to load image and results
  const loadImageAndResults = (file, index) => {
    setCurrentImageIndex(index);
    setSelectedFile(file);
    
    // Load image preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setOriginalImage(e.target.result);
    };
    reader.readAsDataURL(file);
    
    // Load results from batchResults if available
    if (batchResults && batchResults.results) {
      const fileName = file.name;
      const result = batchResults.results.find(r => r.filename === fileName);
      if (result) {
        setResultImage(result.image_base64);
        setDetections(result.detections || []);
      } else {
        setResultImage(null);
        setDetections([]);
      }
    } else {
      setResultImage(null);
      setDetections([]);
    }
  };

  const handleNextImage = () => {
    if (batchFiles.length > 0 && currentImageIndex < batchFiles.length - 1) {
      const nextIndex = currentImageIndex + 1;
      loadImageAndResults(batchFiles[nextIndex], nextIndex);
    }
  };

  const handlePrevImage = () => {
    if (batchFiles.length > 0 && currentImageIndex > 0) {
      const prevIndex = currentImageIndex - 1;
      loadImageAndResults(batchFiles[prevIndex], prevIndex);
    }
  };

  const handleThumbnailClick = (index) => {
    if (index !== currentImageIndex && !isProcessing) {
      loadImageAndResults(batchFiles[index], index);
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) {
      setError('Please select an image first!');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResultImage(null);
    setDetections([]);
    setSuccessMessage(null);

    try {
      // Use default thresholds from model info, or fallback to defaults
      const confThreshold = modelInfo?.default_conf_threshold || 0.25;
      const iouThreshold = modelInfo?.default_iou_threshold || 0.45;
      
      // If multiple images selected, detect all at once
      if (batchFiles.length > 1) {
        const batchResult = await detectBatch(batchFiles, confThreshold, iouThreshold);
        setBatchResults(batchResult);
        
        // Update status for all images
        const newStatuses = {};
        batchFiles.forEach((file, idx) => {
          const result = batchResult.results?.find(r => r.filename === file.name);
          newStatuses[file.name] = {
            detected: result ? result.detections?.length > 0 : false,
            count: result ? result.detections?.length || 0 : 0
          };
        });
        setImageStatuses(newStatuses);
        
        // Display results for current image
        if (batchResult.results) {
          const currentFileName = batchFiles[currentImageIndex].name;
          const result = batchResult.results.find(r => r.filename === currentFileName);
          if (result) {
            setResultImage(result.image_base64);
            setDetections(result.detections || []);
          }
        }
        
        if (batchResult.summary && batchResult.summary.total_detections > 0) {
          setSuccessMessage(`Successfully processed ${batchFiles.length} image(s)! Total detections: ${batchResult.summary.total_detections}`);
          setTimeout(() => setSuccessMessage(null), 5000);
        } else {
          setSuccessMessage(`Successfully processed ${batchFiles.length} image(s)!`);
          setTimeout(() => setSuccessMessage(null), 3000);
        }
      } else {
        // Single image detection
        const result = await detectAnimal(selectedFile, confThreshold, iouThreshold);
        setResultImage(result.image_base64);
        setDetections(result.detections || []);
        
        // Update status
        setImageStatuses({
          [selectedFile.name]: {
            detected: result.detections?.length > 0 || false,
            count: result.detections?.length || 0
          }
        });
        
        if (result.detections && result.detections.length > 0) {
          setSuccessMessage(`Detected ${result.detections.length} animal(s)!`);
          setTimeout(() => setSuccessMessage(null), 3000);
        } else {
          setSuccessMessage('No animals detected in this image.');
          setTimeout(() => setSuccessMessage(null), 3000);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during detection. Please try again.');
      console.error('Detection error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const getImageStatus = (fileName) => {
    return imageStatuses[fileName] || { detected: false, count: 0 };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 py-3 sm:py-4 max-w-7xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 sm:gap-3">
                <span className="text-2xl sm:text-3xl flex-shrink-0">🐾</span>
                <div className="min-w-0">
                  <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-800 leading-tight">
                    Animal Detection System
                  </h1>
                  <p className="text-gray-600 mt-0.5 text-xs sm:text-sm font-medium">Upload an image to detect animals</p>
                </div>
              </div>
            </div>
            {modelInfo && (
              <div className="flex items-center flex-shrink-0">
                <div className="text-right">
                  <div className="text-xs text-gray-500 mb-1">Model Status</div>
                  <div className="inline-flex items-center px-3 sm:px-4 py-1.5 sm:py-2 bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-full shadow-sm">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></span>
                    <span className="font-semibold text-xs sm:text-sm">Ready</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 py-6 sm:py-8 max-w-7xl">
        {/* Error Message */}
        {error && (
          <div className="mb-4 sm:mb-6 bg-red-50 border-l-4 border-red-500 text-red-700 px-4 sm:px-6 py-3 sm:py-4 rounded-lg shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center flex-1 min-w-0">
                <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="font-semibold text-sm sm:text-base break-words">{error}</span>
              </div>
              <button
                onClick={() => setError(null)}
                className="ml-3 text-red-700 hover:text-red-900 flex-shrink-0"
                aria-label="Close error message"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="mb-4 sm:mb-6 bg-green-50 border-l-4 border-green-500 text-green-700 px-4 sm:px-6 py-3 sm:py-4 rounded-lg shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center flex-1 min-w-0">
                <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="font-semibold text-sm sm:text-base break-words">{successMessage}</span>
              </div>
              <button
                onClick={() => setSuccessMessage(null)}
                className="ml-3 text-green-700 hover:text-green-900 flex-shrink-0"
                aria-label="Close success message"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Compact Upload Zone - Always visible */}
        <div className="mb-4 sm:mb-6">
          {!originalImage ? (
            <ImageUpload
              onImageSelect={handleImageSelect}
              onBatchSelect={handleBatchSelect}
              isProcessing={isProcessing}
            />
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-700 mb-1">
                    {batchFiles.length > 1 ? `${batchFiles.length} images loaded` : 'Image loaded'}
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    {selectedFile?.name || 'No file selected'}
                  </div>
                </div>
                <button
                  onClick={handleClearAll}
                  disabled={isProcessing}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium text-sm shadow-sm hover:bg-gray-200 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 whitespace-nowrap"
                  title="Upload new images"
                >
                  <span>📤</span>
                  <span className="hidden sm:inline">Upload More</span>
                  <span className="sm:hidden">New</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Thumbnail Strip - Show when multiple images */}
        {batchFiles.length > 1 && originalImage && (
          <div className="mb-4 sm:mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm font-semibold text-gray-700">Image Gallery</span>
              <span className="text-xs text-gray-500">({batchFiles.length} images)</span>
            </div>
            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
              <button
                onClick={handlePrevImage}
                disabled={currentImageIndex === 0 || isProcessing}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0"
                title="Previous"
              >
                ←
              </button>
              {batchFiles.map((file, index) => {
                const status = getImageStatus(file.name);
                const isActive = index === currentImageIndex;
                return (
                  <div
                    key={index}
                    onClick={() => handleThumbnailClick(index)}
                    className={`relative flex-shrink-0 cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                      isActive 
                        ? 'border-blue-500 ring-2 ring-blue-200' 
                        : 'border-gray-200 hover:border-gray-300'
                    } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
                    style={{ width: '80px', height: '80px' }}
                  >
                    <img
                      src={URL.createObjectURL(file)}
                      alt={`Thumbnail ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                    {status.detected && (
                      <div className="absolute top-1 right-1 bg-green-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                        {status.count}
                      </div>
                    )}
                    {isActive && (
                      <div className="absolute inset-0 bg-blue-500 bg-opacity-20"></div>
                    )}
                    <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white text-xs text-center py-0.5">
                      {index + 1}
                    </div>
                  </div>
                );
              })}
              <button
                onClick={handleNextImage}
                disabled={currentImageIndex === batchFiles.length - 1 || isProcessing}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0"
                title="Next"
              >
                →
              </button>
            </div>
          </div>
        )}

        {/* Main Content Area - Two Column Layout */}
        {originalImage && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
            {/* Left Column: Image Preview (2/3 width on large screens) */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4 sm:p-6 relative">
                {/* Status Badge */}
                <div className="absolute top-4 right-4 z-10">
                  {getImageStatus(selectedFile?.name).detected ? (
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                      <span>✓</span>
                      <span>Detected</span>
                    </div>
                  ) : resultImage ? (
                    <div className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-xs font-semibold">
                      No animals
                    </div>
                  ) : null}
                </div>

                {/* Loading Overlay */}
                {isProcessing && (
                  <div className="absolute inset-0 bg-white bg-opacity-90 rounded-lg flex items-center justify-center z-20">
                    <div className="text-center">
                      <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <p className="text-gray-700 font-medium">Processing image...</p>
                      {batchFiles.length > 1 && (
                        <p className="text-sm text-gray-500 mt-1">
                          Image {currentImageIndex + 1} of {batchFiles.length}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                <ImagePreview
                  originalImage={originalImage}
                  resultImage={resultImage}
                  detections={detections}
                />
              </div>
            </div>

            {/* Right Column: Detected Animals & Actions (1/3 width on large screens) */}
            <div className="lg:col-span-1 space-y-4 sm:space-y-6">
              {/* Detect Button - Large and Prominent */}
              <button
                onClick={handleDetect}
                disabled={isProcessing}
                className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg font-bold text-lg shadow-lg hover:bg-blue-700 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-3"
                title="Detect animals in the image"
              >
                {isProcessing ? (
                  <>
                    <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span className="text-2xl">🔍</span>
                    <span>Detect Animals</span>
                  </>
                )}
              </button>

              {/* Detected Animals - Results Table */}
              {detections.length > 0 ? (
                <div className="bg-white rounded-lg shadow-md border border-gray-200">
                  <ResultsTable detections={detections} />
                </div>
              ) : resultImage ? (
                <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 sm:p-8">
                  <div className="text-center text-gray-500">
                    <div className="text-4xl mb-3">🔍</div>
                    <p className="text-sm font-medium">No animals detected</p>
                    <p className="text-xs text-gray-400 mt-1">Try with a different image</p>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 sm:p-8">
                  <div className="text-center text-gray-400">
                    <div className="text-4xl mb-3">⏳</div>
                    <p className="text-sm font-medium">Click Detect to start</p>
                    <p className="text-xs text-gray-400 mt-1">Results will appear here</p>
                  </div>
                </div>
              )}

              {/* Quick Actions */}
              {detections.length > 0 && (
                <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4 sm:p-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Quick Actions</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => {
                        if (resultImage) {
                          const link = document.createElement('a');
                          link.href = resultImage;
                          link.download = `detected_${selectedFile?.name || 'image'}.png`;
                          link.click();
                        }
                      }}
                      className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
                    >
                      <span>💾</span>
                      <span>Download Result</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}


        {/* Info Section - Only show when no image selected */}
        {!originalImage && (
          <div className="max-w-3xl mx-auto mt-8 sm:mt-12 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="mr-2">ℹ️</span>
                How to Use
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex flex-col items-center text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-3xl mb-2">📤</div>
                  <h4 className="font-semibold text-gray-800 mb-1 text-sm">1. Upload Image</h4>
                  <p className="text-xs text-gray-600">Select or drag & drop an image containing animals</p>
                </div>
                <div className="flex flex-col items-center text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-3xl mb-2">🔍</div>
                  <h4 className="font-semibold text-gray-800 mb-1 text-sm">2. Click Detect</h4>
                  <p className="text-xs text-gray-600">Click the "Detect Animals" button to see results</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12 py-6">
        <div className="container mx-auto px-4 sm:px-6 max-w-7xl">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2 text-gray-600 text-sm">
            <span className="font-medium">Animal Detection System</span>
            <span className="hidden sm:inline">•</span>
            <span>Powered by</span>
            <span className="font-semibold text-gray-800">YOLO</span>
            <span>&</span>
            <span className="font-semibold text-gray-800">React</span>
          </div>
          <div className="mt-2 text-xs text-gray-500 text-center">
            © 2024 - AI Powered Animal Detection
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
