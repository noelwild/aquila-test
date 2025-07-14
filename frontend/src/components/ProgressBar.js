import React from 'react';

const ProgressBar = ({ progress }) => (
  <div className="aquila-progress-bar w-full">
    <div className="aquila-progress-fill" style={{ width: `${progress}%` }} />
  </div>
);

export default ProgressBar;
