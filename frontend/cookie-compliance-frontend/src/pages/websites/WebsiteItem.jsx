import React from 'react';
import { TableCell, TableRow, Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { websiteAPI  } from '../../services/api';
import { deleteWebsite, updateWebsite, fetchWebsiteAnalytics } from '../../store/slices/websiteSlice';

const WebsiteItem = ({ website }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleViewDetail = async () => {
      navigate(`/websites/detail/${website._id}`);
  };

  return (
    <TableRow>
      <TableCell>{website.domain}</TableCell>
      <TableCell>
        {website.policy_url ? <div>Có</div> : (
          <div>Không</div>
        )}
      </TableCell>
      <TableCell>{website.avg_violations.toFixed(2)}</TableCell>
      <TableCell>{website.last_checked_at ? new Date(website.last_checked_at).toLocaleDateString() : 'N/A'}</TableCell>
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
        </Box>
      </TableCell>
    </TableRow>
  );
};

export default WebsiteItem;
