import { useState, useCallback } from 'react';

const useFormValidation = (initialState, validationRules) => {
  const [formData, setFormData] = useState(initialState);
  const [errors, setErrors] = useState({});

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
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

      if (rules.required && !value.trim()) {
        newErrors[field] = rules.required;
        isValid = false;
      } else if (rules.pattern && !rules.pattern.value.test(value)) {
        newErrors[field] = rules.pattern.message;
        isValid = false;
      } else if (rules.minLength && value.length < rules.minLength.value) {
        newErrors[field] = rules.minLength.message;
        isValid = false;
      }
      // Add more validation rules as needed (e.g., maxLength, custom validators)
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
