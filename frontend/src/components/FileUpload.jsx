import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, Image, FileText, AlertCircle } from 'lucide-react'

const FileUpload = ({ onFileUpload }) => {
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      alert('Please upload only image files (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP) or PDF files.')
      return
    }
    
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0])
    }
  }, [onFileUpload])

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'],
      'application/pdf': ['.pdf']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  const getDropzoneClass = () => {
    let baseClass = 'dropzone'
    if (isDragActive) baseClass += ' drag-active'
    if (isDragAccept) baseClass += ' drag-accept'
    if (isDragReject) baseClass += ' drag-reject'
    return baseClass
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="file-upload-container"
    >
      <motion.div
        {...getRootProps()}
        className={getDropzoneClass()}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={{ type: "spring", stiffness: 300 }}
      >
        <input {...getInputProps()} />
        
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="dropzone-content"
        >
          <motion.div
            animate={{ 
              y: isDragActive ? -10 : 0,
              scale: isDragActive ? 1.1 : 1
            }}
            transition={{ type: "spring", stiffness: 300 }}
            className="upload-icon"
          >
            {isDragReject ? (
              <AlertCircle size={48} className="icon-error" />
            ) : (
              <Upload size={48} className="icon-upload" />
            )}
          </motion.div>
          
          <h3 className="dropzone-title">
            {isDragActive
              ? isDragReject
                ? 'File type not supported'
                : 'Drop your file here'
              : 'Upload Image or PDF'
            }
          </h3>
          
          <p className="dropzone-subtitle">
            {isDragActive
              ? ''
              : 'Drag & drop your file here, or click to browse'
            }
          </p>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="supported-formats"
          >
            <div className="format-group">
              <Image size={16} />
              <span>Images: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP</span>
            </div>
            <div className="format-group">
              <FileText size={16} />
              <span>Documents: PDF</span>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="file-limits"
          >
            <span>Maximum file size: 10MB</span>
          </motion.div>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}

export default FileUpload 