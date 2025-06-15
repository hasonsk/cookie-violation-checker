import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createDomainRequest } from '../../store/slices/domainRequestSlice';
import { ToastContainer, toast } from 'react-toastify';

// Constants for validation
const COMPANY_NAME_MIN_LENGTH = 2;
const COMPANY_NAME_MAX_LENGTH = 200;
const DOMAIN_MAX_COUNT = 100;
const PURPOSE_MIN_LENGTH = 10;
const PURPOSE_MAX_LENGTH = 1000;
const DOMAIN_REGEX = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;

const DomainRequestForm = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.domainRequests);

  const [formData, setFormData] = useState({
    company_name: '',
    domains: '',
    purpose: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [duplicateWarning, setDuplicateWarning] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear errors when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: '' }));
    }

    // Clear duplicate warning when domains change
    if (name === 'domains' && duplicateWarning) {
      setDuplicateWarning('');
    }
  };

  const validateCompanyName = (name) => {
    if (!name.trim()) {
      return 'Tên công ty là bắt buộc.';
    } else if (name.trim().length < COMPANY_NAME_MIN_LENGTH) {
      return `Tên công ty phải có ít nhất ${COMPANY_NAME_MIN_LENGTH} ký tự.`;
    } else if (name.trim().length > COMPANY_NAME_MAX_LENGTH) {
      return `Tên công ty không được vượt quá ${COMPANY_NAME_MAX_LENGTH} ký tự.`;
    }
    return '';
  };

  const validateDomains = (domainsString, setDuplicateWarning) => {
    const domainList = domainsString
      .split('\n')
      .map(d => d.trim())
      .filter(Boolean);

    if (domainList.length === 0) {
      return 'Vui lòng nhập ít nhất một domain.';
    } else if (domainList.length > DOMAIN_MAX_COUNT) {
      return `Số lượng domain không được vượt quá ${DOMAIN_MAX_COUNT}.`;
    } else {
      const invalidDomains = domainList.filter(domain => !DOMAIN_REGEX.test(domain));
      if (invalidDomains.length > 0) {
        return `Các domain sau không hợp lệ: ${invalidDomains.join(', ')}`;
      }

      const duplicates = domainList.filter((domain, index) => domainList.indexOf(domain) !== index);
      if (duplicates.length > 0) {
        const uniqueDuplicates = [...new Set(duplicates)];
        setDuplicateWarning(`Phát hiện domain trùng lặp: ${uniqueDuplicates.join(', ')}`);
      } else {
        setDuplicateWarning(''); // Clear warning if no duplicates
      }
    }
    return '';
  };

  const validatePurpose = (purpose) => {
    if (!purpose.trim()) {
      return 'Mục đích đăng ký là bắt buộc.';
    } else if (purpose.trim().length < PURPOSE_MIN_LENGTH) {
      return `Mục đích đăng ký phải có ít nhất ${PURPOSE_MIN_LENGTH} ký tự.`;
    } else if (purpose.trim().length > PURPOSE_MAX_LENGTH) {
      return `Mục đích đăng ký không được vượt quá ${PURPOSE_MAX_LENGTH} ký tự.`;
    }
    return '';
  };

  const validateForm = () => {
    const errors = {};

    const companyNameError = validateCompanyName(formData.company_name);
    if (companyNameError) {
      errors.company_name = companyNameError;
    }

    const domainsError = validateDomains(formData.domains, setDuplicateWarning);
    if (domainsError) {
      errors.domains = domainsError;
    }

    const purposeError = validatePurpose(formData.purpose);
    if (purposeError) {
      errors.purpose = purposeError;
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Vui lòng kiểm tra lại thông tin đã nhập.');
      return;
    }

    const domainsArray = formData.domains
      .split('\n')
      .map(d => d.trim())
      .filter(Boolean);

    // Remove duplicates from domains array
    const uniqueDomains = [...new Set(domainsArray)];

    try {
      const result = await dispatch(createDomainRequest({
        company_name: formData.company_name.trim(),
        domains: uniqueDomains,
        purpose: formData.purpose.trim()
      }));

      if (createDomainRequest.fulfilled.match(result)) {
        const { request_id, status, created_date, valid_domains } = result.payload;

        toast.success(
          `Yêu cầu đăng ký domain đã được gửi thành công!
Mã yêu cầu: ${request_id}
Trạng thái: ${status === 'pending' ? 'Chờ duyệt' : status}
${valid_domains.length}/${uniqueDomains.length} domain hợp lệ được chấp nhận.`,
          { autoClose: 8000 }
        );

        // Reset form
        setFormData({ company_name: '', domains: '', purpose: '' });
        setDuplicateWarning('');
      } else {
        const errorMessage = result.payload?.message || result.payload || 'Gửi yêu cầu thất bại. Vui lòng thử lại.';
        toast.error(errorMessage);
      }
    } catch (err) {
      toast.error('Đã xảy ra lỗi khi gửi yêu cầu. Vui lòng thử lại sau.');
      console.error('Domain request submission error:', err);
    }
  };

  const domainCount = formData.domains.split('\n').filter(d => d.trim()).length;
  const characterCount = formData.purpose.length;

  return (
    <div className="domain-request-form-container">
      <ToastContainer position="top-right" />

      <div className="form-header">
        <h2>Gửi yêu cầu đăng ký Domain</h2>
        <p>
          Nhà cung cấp dịch vụ có thể đăng ký các domain để xem thống kê chi tiết.
          Vui lòng điền đầy đủ thông tin bên dưới.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="domain-request-form">
        {error && (
          <div className="error-alert">
            <strong>Lỗi hệ thống:</strong> {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="company_name">
            Tên công ty <span className="required">*</span>
          </label>
          <input
            type="text"
            id="company_name"
            name="company_name"
            value={formData.company_name}
            onChange={handleChange}
            className={formErrors.company_name ? 'error' : ''}
            placeholder="Nhập tên công ty hoặc tổ chức"
            disabled={loading}
            maxLength={200}
          />
          {formErrors.company_name && (
            <span className="error-text">{formErrors.company_name}</span>
          )}
          <span className="char-count">
            {formData.company_name.length}/200 ký tự
          </span>
        </div>

        <div className="form-group">
          <label htmlFor="domains">
            Danh sách Domain <span className="required">*</span>
          </label>
          <div className="domain-info">
            <small>Mỗi domain một dòng (tối đa 100 domain)</small>
            <span className="domain-count">{domainCount}/100 domain</span>
          </div>
          <textarea
            id="domains"
            name="domains"
            value={formData.domains}
            onChange={handleChange}
            className={formErrors.domains ? 'error' : ''}
            rows="6"
            placeholder="Ví dụ:&#10;example.com&#10;subdomain.example.org&#10;test.vn"
            disabled={loading}
          />
          {duplicateWarning && (
            <div className="warning-text">⚠️ {duplicateWarning}</div>
          )}
          {formErrors.domains && (
            <span className="error-text">{formErrors.domains}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="purpose">
            Mục đích/Nguyện vọng đăng ký <span className="required">*</span>
          </label>
          <textarea
            id="purpose"
            name="purpose"
            value={formData.purpose}
            onChange={handleChange}
            className={formErrors.purpose ? 'error' : ''}
            rows="4"
            placeholder="Mô tả chi tiết mục đích đăng ký các domain này (ít nhất 10 ký tự). Ví dụ: Kiểm tra tuân thủ cookie cho khách hàng, cải thiện dịch vụ web..."
            disabled={loading}
            maxLength={1000}
          />
          {formErrors.purpose && (
            <span className="error-text">{formErrors.purpose}</span>
          )}
          <span className="char-count">
            {characterCount}/1000 ký tự {characterCount < 10 && `(còn thiếu ${10 - characterCount})`}
          </span>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="reset-button"
            onClick={() => {
              setFormData({ company_name: '', domains: '', purpose: '' });
              setFormErrors({});
              setDuplicateWarning('');
            }}
            disabled={loading}
          >
            Đặt lại
          </button>
          <button
            className="submit-button"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Đang gửi yêu cầu...
              </>
            ) : (
              'Gửi yêu cầu đăng ký'
            )}
          </button>
        </div>
      </form>

      <style jsx>{`
        .domain-request-form-container {
          background: white;
          padding: 35px;
          border-radius: 12px;
          box-shadow: 0 6px 25px rgba(0, 0, 0, 0.08);
          max-width: 700px;
          margin: 40px auto;
          border: 1px solid #e2e8f0;
        }

        .form-header {
          text-align: center;
          margin-bottom: 35px;
        }

        .form-header h2 {
          color: #2d3748;
          margin-bottom: 12px;
          font-size: 24px;
          font-weight: 700;
        }

        .form-header p {
          color: #718096;
          line-height: 1.6;
          font-size: 15px;
        }

        .domain-request-form {
          display: flex;
          flex-direction: column;
          gap: 25px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .form-group label {
          font-weight: 600;
          color: #2d3748;
          font-size: 15px;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .required {
          color: #e53e3e;
          font-weight: bold;
        }

        .domain-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 5px;
        }

        .domain-info small {
          color: #718096;
          font-size: 13px;
        }

        .domain-count {
          color: #4a5568;
          font-size: 13px;
          font-weight: 500;
        }

        .char-count {
          color: #718096;
          font-size: 12px;
          text-align: right;
          margin-top: 4px;
        }

        .form-group input,
        .form-group textarea {
          padding: 14px 16px;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          font-size: 15px;
          transition: all 0.2s ease;
          width: 100%;
          box-sizing: border-box;
          font-family: inherit;
        }

        .form-group input:focus,
        .form-group textarea:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-group input.error,
        .form-group textarea.error {
          border-color: #e53e3e;
          background-color: #fef5e7;
        }

        .error-text {
          color: #e53e3e;
          font-size: 13px;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .error-text::before {
          content: "⚠️";
        }

        .warning-text {
          color: #d69e2e;
          font-size: 13px;
          background-color: #fef5e7;
          padding: 8px 12px;
          border-radius: 6px;
          border-left: 4px solid #d69e2e;
        }

        .error-alert {
          background-color: #fed7d7;
          color: #c53030;
          padding: 16px;
          border-radius: 8px;
          border: 1px solid #feb2b2;
          font-size: 14px;
          text-align: center;
        }

        .form-actions {
          display: flex;
          gap: 15px;
          margin-top: 10px;
        }

        .reset-button {
          background: #f7fafc;
          color: #4a5568;
          border: 2px solid #e2e8f0;
          padding: 14px 24px;
          border-radius: 8px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          flex: 1;
        }

        .reset-button:hover:not(:disabled) {
          background: #edf2f7;
          border-color: #cbd5e0;
        }

        .submit-button {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 14px 24px;
          border-radius: 8px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          flex: 2;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .submit-button:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }

        .submit-button:disabled,
        .reset-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .domain-request-form-container {
            margin: 20px 16px;
            padding: 25px 20px;
          }

          .form-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default DomainRequestForm;
