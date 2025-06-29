import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../../src/App.css'; // Ensure this path is correct for your CSS

const NotFound = () => {
  const { t } = useTranslation();

  return (
    <div className="not-found-container">
      <h1 className="not-found-title">404</h1>
      <p className="not-found-message">{t('pageNotFound')}</p>
      <Link to="/" className="not-found-link">
        {t('goToHomepage')}
      </Link>
    </div>
  );
};

export default NotFound;
