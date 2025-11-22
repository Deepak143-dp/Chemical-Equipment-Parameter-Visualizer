import React, {useEffect, useState} from 'react';
import axios from 'axios';
import { API_BASE } from '../config';
import DatasetView from './DatasetView';
export default function DatasetList(){
  const [datasets, setDatasets] = useState([]);
  const [selected, setSelected] = useState(null);
  useEffect(()=>{ fetchList(); }, []);
  async function fetchList(){
    try{ const res = await axios.get(`${API_BASE}/datasets/`);
     setDatasets(res.data);
     }catch(err){ console.error(err); }
  }
  return (
    <div className='card'>
      <h3>Last 5 Datasets</h3>
      <ul>
        {datasets.map(d=>(
          <li key={d.id}>
            <button onClick={()=>setSelected(d)}>{d.name} ({d.row_count} rows)</button>
          </li>
        ))}
      </ul>
      {selected && <DatasetView dataset={selected} />}
    </div>
  );
}



