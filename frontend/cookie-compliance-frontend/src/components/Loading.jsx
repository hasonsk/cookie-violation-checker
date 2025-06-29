import React from 'react';
import PropTypes from 'prop-types';
import { Skeleton } from '@mui/material';
import './Loading.css';

const Loading = ({
  size = 'medium',
  text = 'Đang tải...',
  overlay = false,
  color = '#3182ce'
}) => {
  const sizeMap = {
    small: '24px',
    medium: '40px',
    large: '56px'
  };

  const spinnerSize = sizeMap[size] || sizeMap.medium;
  const textSize = size === 'small' ? '14px' : size === 'large' ? '18px' : '16px';

  const LoadingContent = () => (
    <div className="loading-container">
      <div className="spinner" style={{ width: spinnerSize, height: spinnerSize }}>
        <div className="spinner-ring" style={{ borderTopColor: color }}></div>
      </div>
      {text && <p className="loading-text" style={{ fontSize: textSize }}>{text}</p>}
    </div>
  );

  // Nếu là overlay, hiển thị full screen
  if (overlay) {
    return (
      <div className="loading-overlay">
        <LoadingContent />
      </div>
    );
  }

  // Loading thường
  return <LoadingContent />;
};

Loading.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  text: PropTypes.string,
  overlay: PropTypes.bool,
  color: PropTypes.string,
};

// Loading skeleton cho danh sách hoặc các hình dạng khác
export const LoadingSkeleton = ({
  lines = 3,
  height = '20px',
  variant = 'line', // 'text', 'rectangular', 'circular', or 'line' (custom CSS)
  width, // for rectangular/text variants
  animation = 'wave', // 'pulse' or 'wave'
}) => {
  if (variant === 'line') {
    return (
      <div className="skeleton-container">
        {Array.from({ length: lines }, (_, index) => (
          <div key={index} className="skeleton-line" style={{ height }}></div>
        ))}
      </div>
    );
  }

  return (
    <div className="skeleton-container">
      {Array.from({ length: lines }, (_, index) => (
        <Skeleton
          key={index}
          variant={variant}
          width={width || (variant === 'text' ? '100%' : '50px')} // Default width for text/rectangular
          height={height}
          animation={animation}
          sx={{ borderRadius: variant === 'circular' ? '50%' : '4px' }} // Apply border-radius for consistency
        />
      ))}
    </div>
  );
};

LoadingSkeleton.propTypes = {
  lines: PropTypes.number,
  height: PropTypes.string,
  variant: PropTypes.oneOf(['text', 'rectangular', 'circular', 'line']),
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  animation: PropTypes.oneOf(['pulse', 'wave', false]),
};

// Loading dots
export const LoadingDots = ({ color = '#3182ce' }) => (
  <div className="dots-container">
    <div className="dot" style={{ backgroundColor: color }}></div>
    <div className="dot" style={{ backgroundColor: color }}></div>
    <div className="dot" style={{ backgroundColor: color }}></div>
  </div>
);

LoadingDots.propTypes = {
  color: PropTypes.string,
};

export default Loading;
