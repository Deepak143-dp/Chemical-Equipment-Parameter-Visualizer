import React from 'react';
import UploadForm from './components/UploadForm';
import DatasetList from './components/DatasetList';
export default function App(){
  return (
    <div className='container'>
      <h1>Chemical Equipment Parameter Visualizer</h1>
      <UploadForm />
      <DatasetList />
    </div>
  );
}
