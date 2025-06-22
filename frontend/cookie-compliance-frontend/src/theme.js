import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3182ce', // Xanh dương chuyên nghiệp
    },
    secondary: {
      main: '#1e293b', // Xanh đen/Xám
    },
    error: {
      main: '#e53e3e', // Đỏ cho lỗi
    },
    success: {
      main: '#4caf50', // Xanh lá cây cho thành công
    },
    warning: {
      main: '#ff9800', // Cam cho cảnh báo
    },
    info: {
      main: '#2196f3', // Xanh dương cho thông tin (standard MUI info color)
    },
    background: {
      default: '#f5f5f5', // Xám rất nhạt cho nền chính
      paper: '#ffffff', // Trắng cho các bề mặt nổi
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      textTransform: 'none',
    },
    caption: {
      fontSize: '0.75rem',
    },
    overline: {
      fontSize: '0.75rem',
      textTransform: 'uppercase',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Giữ nguyên chữ thường
          borderRadius: '8px', // Bo tròn góc
        },
        containedPrimary: {
          // Styles for primary contained buttons
          '&:hover': {
            backgroundColor: '#2c7bbd', // Darker shade on hover
          },
        },
        outlinedPrimary: {
          // Styles for primary outlined buttons
          borderColor: '#3182ce',
          color: '#3182ce',
          '&:hover': {
            backgroundColor: 'rgba(49, 130, 206, 0.04)', // Light background on hover
            borderColor: '#2c7bbd',
          },
        },
        textPrimary: {
          // Styles for primary text buttons
          color: '#3182ce',
          '&:hover': {
            backgroundColor: 'rgba(49, 130, 206, 0.04)',
          },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-root': {
            fontWeight: 'bold',
            backgroundColor: '#f5f5f5', // grey.50 equivalent
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '8px',
          },
        },
      },
    },
  },
});

export default theme;
