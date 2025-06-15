import React from 'react';
import { useAuth } from '../hooks/useAuth';
import './ApprovalPending.css'; // Import the new CSS file

const ApprovalPending = () => {
  const { user, isAuthenticated, isApproved } = useAuth();

  if (!isAuthenticated || isApproved || user?.role === 'admin') {
    return null; // Don't render if not authenticated, already approved, or is an admin
  }

  let message = "Tài khoản của bạn đang chờ phê duyệt. Vui lòng chờ quản trị viên kích hoạt.";
  if (user?.role === 'manager') {
    message = "Tài khoản của bạn đang chờ phê duyệt. Quản trị viên sẽ phản hồi trong vòng 24 giờ.";
  } else if (user?.role === 'provider') {
    message = "Tài khoản của bạn đang chờ phê duyệt. Sau khi được duyệt, bạn sẽ có thể đăng ký các domain của mình.";
  }

  return (
    <div className="approval-pending-overlay">
      <div className="approval-pending-card">
        <h2>Tài khoản đang chờ phê duyệt</h2>
        <p>{message}</p>
        <p>Cảm ơn bạn đã kiên nhẫn!</p>
      </div>
    </div>
  );
};

export default ApprovalPending;
