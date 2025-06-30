import React, { memo } from 'react';
import { TableCell, TableRow, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth'; // Import useAuth

const WebsiteItem = ({ website }) => {
  const navigate = useNavigate();

  console.log("WebsiteItem received website:", website);

  const handleViewDetail = () => {
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

export default memo(WebsiteItem);
