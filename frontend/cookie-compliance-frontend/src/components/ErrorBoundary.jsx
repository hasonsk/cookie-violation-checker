import React from 'react';
import { Box, Typography, Button } from '@mui/material'; // Import MUI components

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
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px',
            padding: '20px',
          }}
        >
          <Box
            sx={{
              textAlign: 'center',
              maxWidth: '500px',
              padding: '30px',
              border: '2px solid',
              borderColor: 'error.main', // Use theme error color
              borderRadius: '8px',
              backgroundColor: 'error.light', // A lighter shade of error for background
              color: 'text.primary',
            }}
          >
            <Typography variant="h5" component="h2" sx={{ color: 'error.main', marginBottom: '16px' }}>
              Oops! Có lỗi xảy ra
            </Typography>
            <Typography variant="body1" sx={{ color: 'text.secondary', marginBottom: '24px', lineHeight: 1.6 }}>
              Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau.
            </Typography>

            <Button
              variant="contained"
              color="primary"
              onClick={() => window.location.reload()}
              sx={{
                padding: '12px 24px',
                fontSize: '16px',
                borderRadius: '6px',
              }}
            >
              Tải lại trang
            </Button>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Box sx={{ marginTop: '20px', textAlign: 'left' }}>
                <Typography variant="subtitle1" component="summary" sx={{ cursor: 'pointer', color: 'text.secondary', marginBottom: '10px' }}>
                  Chi tiết lỗi (Development mode)
                </Typography>
                <Box
                  component="pre"
                  sx={{
                    backgroundColor: 'background.default', // Use theme background color
                    padding: '15px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    overflowX: 'auto',
                    whiteSpace: 'pre-wrap',
                    border: '1px solid',
                    borderColor: 'divider', // Use theme divider color
                  }}
                >
                  {this.state.error.toString()}
                  <br />
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </Box>
              </Box>
            )}
          </Box>
        </Box>
      );
    }

    // Render children bình thường khi không có lỗi
    return this.props.children;
  }
}

export default ErrorBoundary;
