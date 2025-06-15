import React from 'react'; // Import React
import PropTypes from 'prop-types'; // Import PropTypes
import { Breadcrumbs, Typography, Link } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const BreadcrumbsNav = ({ items }) => {
  const navigate = useNavigate();

  return (
    <Breadcrumbs separator="/" sx={{ fontSize: '0.875rem' }}>
      {items.map((item, index) =>
        item.active ? (
          <Typography key={index} color="text.primary" sx={{ fontWeight: 500 }}>
            {item.label}
          </Typography>
        ) : (
          <Link
            key={index}
            color="inherit"
            href="#"
            onClick={(e) => {
              e.preventDefault();
              if (item.href) navigate(item.href);
            }}
            sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
          >
            {item.label}
          </Link>
        )
      )}
    </Breadcrumbs>
  );
};

BreadcrumbsNav.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      href: PropTypes.string,
      active: PropTypes.bool,
    })
  ).isRequired,
};

export default BreadcrumbsNav;
