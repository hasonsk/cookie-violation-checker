import React from 'react';
import { TableCell, TableRow, LinearProgress, Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const WebsiteItem = ({ website }) => {
  const navigate = useNavigate();

  const handleViewDetail = () => {
    // Navigate to detail page with website data
    navigate(`/websites/detail/${website.id || website.name}`, {
      state: {
        websiteData: website,
        websiteName: website.name
      }
    });
  };

  const handleEdit = () => {
    // Handle edit functionality
    console.log('Edit website:', website);
  };

  const handleDelete = () => {
    // Handle delete functionality
    console.log('Delete website:', website);
  };

  return (
    <TableRow>
      <TableCell>{website.name}</TableCell>
      <TableCell>{website.company}</TableCell>
      <TableCell>{website.city}</TableCell>
      <TableCell>
        <LinearProgress
          variant="determinate"
          value={website.progress}
          sx={{ minWidth: 100 }}
        />
        <Typography variant="caption" sx={{ ml: 1 }}>
          {website.progress}%
        </Typography>
      </TableCell>
      <TableCell>{website.created}</TableCell>
      <TableCell>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            size="small"
            color="primary"
            onClick={handleViewDetail}
          >
            View Detail
          </Button>
          <Button
            variant="outlined"
            size="small"
            color="error"
            onClick={handleDelete}
          >
            Delete
          </Button>
        </Box>
      </TableCell>
    </TableRow>
  );
};

export default WebsiteItem;
