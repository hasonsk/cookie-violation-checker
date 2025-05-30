import * as yup from 'yup';

export const loginSchema = yup.object({
  email: yup
    .string()
    .email('Email không hợp lệ')
    .required('Email là bắt buộc'),
  password: yup
    .string()
    .min(6, 'Mật khẩu phải có ít nhất 6 ký tự')
    .required('Mật khẩu là bắt buộc'),
});

export const registerSchema = yup.object({
  name: yup
    .string()
    .min(2, 'Tên phải có ít nhất 2 ký tự')
    .required('Tên là bắt buộc'),
  email: yup
    .string()
    .email('Email không hợp lệ')
    .required('Email là bắt buộc'),
  password: yup
    .string()
    .min(6, 'Mật khẩu phải có ít nhất 6 ký tự')
    .required('Mật khẩu là bắt buộc'),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref('password')], 'Mật khẩu xác nhận không khớp')
    .required('Xác nhận mật khẩu là bắt buộc'),
});

export const websiteSchema = yup.object({
  name: yup
    .string()
    .min(3, 'Tên website phải có ít nhất 3 ký tự')
    .required('Tên website là bắt buộc'),
  url: yup
    .string()
    .url('URL không hợp lệ')
    .required('URL là bắt buộc'),
  description: yup
    .string()
    .max(500, 'Mô tả không được quá 500 ký tự'),
  category: yup
    .string()
    .required('Danh mục là bắt buộc'),
});
