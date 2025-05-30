import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Cập nhật state để hiển thị UI fallback
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Lưu thông tin lỗi để debug
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Có thể log lỗi lên service monitoring
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // UI fallback khi có lỗi
      return (
        <div className="error-boundary">
          <div className="error-container">
            <h2>Oops! Có lỗi xảy ra</h2>
            <p>Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau.</p>

            <button
              onClick={() => window.location.reload()}
              className="retry-button"
            >
              Tải lại trang
            </button>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="error-details">
                <summary>Chi tiết lỗi (Development mode)</summary>
                <pre className="error-stack">
                  {this.state.error.toString()}
                  <br />
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>

          <style jsx>{`
            .error-boundary {
              display: flex;
              justify-content: center;
              align-items: center;
              min-height: 400px;
              padding: 20px;
            }

            .error-container {
              text-align: center;
              max-width: 500px;
              padding: 30px;
              border: 2px solid #ff6b6b;
              border-radius: 8px;
              background-color: #fff5f5;
            }

            .error-container h2 {
              color: #e53e3e;
              margin-bottom: 16px;
            }

            .error-container p {
              color: #666;
              margin-bottom: 24px;
              line-height: 1.6;
            }

            .retry-button {
              background-color: #3182ce;
              color: white;
              border: none;
              padding: 12px 24px;
              border-radius: 6px;
              cursor: pointer;
              font-size: 16px;
              transition: background-color 0.2s;
            }

            .retry-button:hover {
              background-color: #2c5aa0;
            }

            .error-details {
              margin-top: 20px;
              text-align: left;
            }

            .error-details summary {
              cursor: pointer;
              color: #666;
              margin-bottom: 10px;
            }

            .error-stack {
              background-color: #f7fafc;
              padding: 15px;
              border-radius: 4px;
              font-size: 12px;
              overflow-x: auto;
              white-space: pre-wrap;
              border: 1px solid #e2e8f0;
            }
          `}</style>
        </div>
      );
    }

    // Render children bình thường khi không có lỗi
    return this.props.children;
  }
}

export default ErrorBoundary;
