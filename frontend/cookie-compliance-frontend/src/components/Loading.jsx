import React from 'react';

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

  const LoadingContent = () => (
    <div className="loading-container">
      <div className="spinner" style={{ width: spinnerSize, height: spinnerSize }}>
        <div className="spinner-ring"></div>
      </div>
      {text && <p className="loading-text">{text}</p>}

      <style jsx>{`
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 12px;
        }

        .spinner {
          position: relative;
          display: inline-block;
        }

        .spinner-ring {
          width: 100%;
          height: 100%;
          border: 3px solid rgba(49, 130, 206, 0.2);
          border-top: 3px solid ${color};
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .loading-text {
          margin: 0;
          color: #666;
          font-size: ${size === 'small' ? '14px' : size === 'large' ? '18px' : '16px'};
          font-weight: 500;
        }
      `}</style>
    </div>
  );

  // Nếu là overlay, hiển thị full screen
  if (overlay) {
    return (
      <div className="loading-overlay">
        <LoadingContent />
        <style jsx>{`
          .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(2px);
          }
        `}</style>
      </div>
    );
  }

  // Loading thường
  return <LoadingContent />;
};

// Loading skeleton cho danh sách
export const LoadingSkeleton = ({ lines = 3, height = '20px' }) => (
  <div className="skeleton-container">
    {Array.from({ length: lines }, (_, index) => (
      <div key={index} className="skeleton-line" style={{ height }}></div>
    ))}

    <style jsx>{`
      .skeleton-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .skeleton-line {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        border-radius: 4px;
        animation: loading 1.5s infinite;
      }

      .skeleton-line:last-child {
        width: 70%;
      }

      @keyframes loading {
        0% {
          background-position: 200% 0;
        }
        100% {
          background-position: -200% 0;
        }
      }
    `}</style>
  </div>
);

// Loading dots
export const LoadingDots = ({ color = '#3182ce' }) => (
  <div className="dots-container">
    <div className="dot"></div>
    <div className="dot"></div>
    <div className="dot"></div>

    <style jsx>{`
      .dots-container {
        display: flex;
        gap: 4px;
        align-items: center;
        justify-content: center;
      }

      .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: ${color};
        animation: bounce 1.4s infinite ease-in-out;
      }

      .dot:nth-child(1) {
        animation-delay: -0.32s;
      }

      .dot:nth-child(2) {
        animation-delay: -0.16s;
      }

      @keyframes bounce {
        0%, 80%, 100% {
          transform: scale(0);
          opacity: 0.5;
        }
        40% {
          transform: scale(1);
          opacity: 1;
        }
      }
    `}</style>
  </div>
);

export default Loading;
