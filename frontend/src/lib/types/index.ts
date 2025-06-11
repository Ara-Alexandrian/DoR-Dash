// TypeScript interface definitions for DoR-Dash frontend

// User-related types
export interface User {
  id: number;
  username: string;
  role: 'admin' | 'faculty' | 'student' | 'secretary';
  created_at: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
}

// API Parameter types
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface MeetingParams extends PaginationParams {
  meeting_type?: string;
  start_date?: string;
  end_date?: string;
}

export interface UserParams extends PaginationParams {
  role?: string;
  active?: boolean;
}

// Meeting types
export interface Meeting {
  id: number;
  title: string;
  meeting_type: string;
  start_date: string;
  end_date: string;
  description?: string;
  created_at: string;
}

// Update types
export interface StudentUpdate {
  id: number;
  user_id: number;
  meeting_id: number;
  research_progress: string;
  challenges_issues: string;
  goals_next_meeting: string;
  additional_notes?: string;
  created_at: string;
  files?: FileUpload[];
}

export interface FacultyUpdate {
  id: number;
  user_id: number;
  meeting_id: number;
  announcements: string;
  notes?: string;
  created_at: string;
  files?: FileUpload[];
}

// File upload types
export interface FileUpload {
  id: number;
  filename: string;
  original_filename: string;
  content_type: string;
  file_size: number;
  upload_date: string;
}

// Registration types
export interface RegistrationRequest {
  id: number;
  username: string;
  email: string;
  full_name: string;
  student_id?: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

// Form data types
export interface UserFormData {
  username: string;
  password?: string;
  role: string;
  email?: string;
  full_name?: string;
}

export interface PasswordChangeData {
  oldPassword: string;
  newPassword: string;
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

// Event handler types
export interface FileChangeEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

export interface FormSubmitEvent extends Event {
  target: HTMLFormElement & EventTarget;
}