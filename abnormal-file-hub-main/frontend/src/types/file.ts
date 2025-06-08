export interface File {
  id: string;
  file: string | null;
  file_path: string;
  original_filename: string;
  file_type: string;
  size: number;
  uploaded_at: string;
  is_duplicate: boolean;
  original_file?: string;
  original_file_details?: {
    id: string;
    original_filename: string;
    file_type: string;
    size: number;
    uploaded_at: string;
  };
  reference_count: number;
  duplicates_count: number;
} 