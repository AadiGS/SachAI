import React from "react";

interface FileUploadInterfaceProps {
  icon?: React.ReactNode;
  title?: string;
  acceptedFileTypes?: string;
  onFileSelect: (file: File) => void;
}

export const FileUploadInterface: React.FC<FileUploadInterfaceProps> = ({
  icon,
  title = "Upload File",
  acceptedFileTypes = "*",
  onFileSelect,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-blue-400 rounded-lg cursor-pointer hover:bg-blue-50 transition-all">
      {icon && <div className="mb-2">{icon}</div>}
      <span className="font-medium text-blue-500 mb-1">{title}</span>
      <input
        type="file"
        accept={acceptedFileTypes}
        onChange={handleChange}
        className="hidden"
      />
      <span className="text-xs text-muted-foreground">Click or drag file here</span>
    </label>
  );
};
