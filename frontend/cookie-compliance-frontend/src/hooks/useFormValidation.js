import { useState, useCallback } from 'react';

const useFormValidation = (initialState, validationRules) => {
  const [formData, setFormData] = useState(initialState);
  const [errors, setErrors] = useState({});

  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error for the field as user types
    if (errors[name]) {
      setErrors((prevErrors) => ({
        ...prevErrors,
        [name]: '',
      }));
    }
  }, [errors]);

  const validateForm = useCallback(() => {
    let newErrors = {};
    let isValid = true;

    for (const field in validationRules) {
      const value = formData[field];
      const rules = validationRules[field];

      // Handle boolean values for required fields (like checkboxes)
      if (rules.required && typeof value === 'boolean') {
        if (!value) {
          newErrors[field] = rules.required;
          isValid = false;
        }
      } else if (rules.required && (typeof value === 'string' && !value.trim())) {
        newErrors[field] = rules.required;
        isValid = false;
      } else if (rules.pattern && typeof value === 'string' && !rules.pattern.value.test(value)) {
        newErrors[field] = rules.pattern.message;
        isValid = false;
      } else if (rules.minLength && typeof value === 'string' && value.length < rules.minLength.value) {
        newErrors[field] = rules.minLength.message;
        isValid = false;
      } else if (rules.custom) {
        const customError = rules.custom(value, formData);
        if (customError) {
          newErrors[field] = customError;
          isValid = false;
        }
      }
    }

    setErrors(newErrors);
    return isValid;
  }, [formData, validationRules]);

  return {
    formData,
    errors,
    handleChange,
    validateForm,
    setErrors, // Expose setErrors for external control if needed
  };
};

export default useFormValidation;
