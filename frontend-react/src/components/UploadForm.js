import React, {useState} from 'react';
import axios from 'axios';
import { API_BASE } from '../config';
export default function UploadForm(){
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const onSubmit = async (e) => {
    e.preventDefault();
    if(!file){ setMessage('Choose a CSV file'); return; }
    const form = new FormData();
    form.append('file', file);
    try{
      const res = await axios.post(`${API_BASE}/upload/`, form, { headers: {'Content-Type':'multipart/form-data'} });
      setMessage('Uploaded: ' + res.data.name);
    }catch(err){
      setMessage('Upload error: ' + (err.response?.data?.error || err.message));
    }
  }
  return (
    <div className='card'>
      <h3>Upload CSV</h3>
      <form onSubmit={onSubmit}>
        <input type='file' accept='.csv' onChange={e=>setFile(e.target.files[0])} />
        <button type='submit'>Upload</button>
      </form>
      <div>{message}</div>
    </div>
  );
}
