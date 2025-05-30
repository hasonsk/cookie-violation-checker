// src/services/mockApi.js
// Mock users database
const mockUsers = [
  {
    id: 1,
    name: 'Admin User',
    email: 'admin@example.com',
    password: '123456', // In real app, this would be hashed
    role: 'admin'
  },
  {
    id: 2,
    name: 'John Doe',
    email: 'john@example.com',
    password: '123456',
    role: 'user'
  }
];

// Simulate API delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Mock API functions
export const mockApi = {
  // Login
  login: async (credentials) => {
    await delay(1000); // Simulate network delay

    const user = mockUsers.find(
      u => u.email === credentials.email && u.password === credentials.password
    );

    if (!user) {
      throw new Error('Email hoặc mật khẩu không đúng');
    }

    // Generate mock token
    const token = `mock_token_${user.id}_${Date.now()}`;

    return {
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      }
    };
  },

  // Register
  register: async (userData) => {
    await delay(1500); // Simulate network delay

    // Check if email already exists
    const existingUser = mockUsers.find(u => u.email === userData.email);
    if (existingUser) {
      throw new Error('Email đã được sử dụng');
    }

    // Create new user
    const newUser = {
      id: mockUsers.length + 1,
      name: userData.name,
      email: userData.email,
      password: userData.password,
      role: 'user'
    };

    mockUsers.push(newUser);

    return {
      message: 'Đăng ký thành công',
      user: {
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
        role: newUser.role
      }
    };
  },

  // Verify token
  verify: async (token) => {
    await delay(500);

    // Simple token validation
    if (!token || !token.startsWith('mock_token_')) {
      throw new Error('Invalid token');
    }

    // Extract user ID from token
    const userId = parseInt(token.split('_')[2]);
    const user = mockUsers.find(u => u.id === userId);

    if (!user) {
      throw new Error('User not found');
    }

    return {
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      }
    };
  },

  // Logout
  logout: async () => {
    await delay(300);
    return { message: 'Đăng xuất thành công' };
  }
};
