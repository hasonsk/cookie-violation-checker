import React, { useState } from 'react';
import { Box, Typography, Button, Select, MenuItem, FormControl, InputLabel, Slider, Paper } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useTranslation } from 'react-i18next';
import { ColorModeContext } from '../../contexts/ThemeContext'; // Import ColorModeContext
import { useContext } from 'react'; // Import useContext

const Settings = () => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const colorMode = useContext(ColorModeContext); // Use ColorModeContext
  const [selectedTheme, setSelectedTheme] = useState(theme.palette.mode);
  const [selectedLanguage, setSelectedLanguage] = useState(i18n.language);
  const [fontSize, setFontSize] = useState(parseInt(localStorage.getItem('fontSize') || '16', 10)); // Get font size from local storage

  const handleThemeChange = (event) => {
    const newTheme = event.target.value;
    setSelectedTheme(newTheme);
    colorMode.toggleColorMode(); // Toggle theme using context
  };

  const handleLanguageChange = (event) => {
    const newLang = event.target.value;
    setSelectedLanguage(newLang);
    i18n.changeLanguage(newLang);
  };

  const handleFontSizeChange = (event, newValue) => {
    setFontSize(newValue);
    localStorage.setItem('fontSize', newValue); // Save font size to local storage
    document.documentElement.style.setProperty('--font-size', `${newValue}px`);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {t('settings.title')}
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          {t('settings.themeSettings')}
        </Typography>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="theme-select-label">{t('settings.selectTheme')}</InputLabel>
          <Select
            labelId="theme-select-label"
            id="theme-select"
            value={selectedTheme}
            label={t('settings.selectTheme')}
            onChange={handleThemeChange}
          >
            <MenuItem value="light">{t('settings.lightTheme')}</MenuItem>
            <MenuItem value="dark">{t('settings.darkTheme')}</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" color="primary" onClick={colorMode.toggleColorMode}>
          {t('settings.applyTheme')}
        </Button>
      </Paper>

      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          {t('settings.languageSettings')}
        </Typography>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="language-select-label">{t('settings.selectLanguage')}</InputLabel>
          <Select
            labelId="language-select-label"
            id="language-select"
            value={selectedLanguage}
            label={t('settings.selectLanguage')}
            onChange={handleLanguageChange}
          >
            <MenuItem value="en">{t('settings.english')}</MenuItem>
            <MenuItem value="vi">{t('settings.vietnamese')}</MenuItem>
          </Select>
        </FormControl>
      </Paper>
    </Box>
  );
};

export default Settings;
