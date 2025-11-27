import React from 'react';
import UploadForm from './components/UploadForm';
import DatasetList from './components/DatasetList';
export default function App(){
  return (
    <div className='container'>
      <h1>Chemical Equipment Parameter Visualizer</h1>
      <p>Please wait for up to 1-2 minutes for the backend to fully initialize.</p>
      <UploadForm />
      <DatasetList />
    </div>
  );
}
