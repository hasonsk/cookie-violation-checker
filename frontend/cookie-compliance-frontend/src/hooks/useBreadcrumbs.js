import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const useBreadcrumbs = () => {
  const location = useLocation();
  const [breadcrumbItems, setBreadcrumbItems] = useState([]);

  useEffect(() => {
    const pathnames = location.pathname.split('/').filter(Boolean);
    if (pathnames.length === 0 || (pathnames.length === 1 && pathnames[0] === 'websites')) {
      setBreadcrumbItems([
        { label: 'Dashboard', href: '/' },
        { label: 'Danh sách website', href: '/websites', active: true }
      ]);
    } else if (pathnames[0] === 'websites' && pathnames[1] === 'detail') {
      // This assumes location.state.websiteName is passed when navigating to website detail
      // If not, it will fall back to the path segment or 'Unknown'
      const websiteName = location.state?.websiteName || pathnames[2] || 'Unknown';
      setBreadcrumbItems([
        { label: 'Dashboard', href: '/' },
        { label: 'Danh sách website', href: '/websites' },
        { label: `Chi tiết: ${websiteName}`, active: true }
      ]);
    } else if (pathnames[0] === 'admin' && pathnames[1] === 'users') {
      setBreadcrumbItems([
        { label: 'Dashboard', href: '/' },
        { label: 'Quản lý người dùng', href: '/admin/users', active: true }
      ]);
    } else if (pathnames[0] === 'admin' && pathnames[1] === 'domain-requests') {
      setBreadcrumbItems([
        { label: 'Dashboard', href: '/' },
        { label: 'Quản lý yêu cầu Domain', href: '/admin/domain-requests', active: true }
      ]);
    } else if (pathnames[0] === 'my-request') {
      setBreadcrumbItems([
        { label: 'Dashboard', href: '/' },
        { label: 'Yêu cầu của tôi', href: '/my-request', active: true }
      ]);
    }
    // Add more conditions for other routes as needed
  }, [location]);

  return breadcrumbItems;
};

export default useBreadcrumbs;
