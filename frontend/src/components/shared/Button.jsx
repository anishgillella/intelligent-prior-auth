export default function Button({ 
  children, 
  onClick, 
  loading = false, 
  disabled = false,
  variant = 'primary',
  className = ''
}) {
  const baseStyles = 'px-6 py-2 rounded-lg font-medium transition-colors'
  
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 disabled:bg-gray-400',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-400',
    success: 'bg-success text-white hover:bg-green-600 disabled:bg-gray-400',
    error: 'bg-error text-white hover:bg-red-600 disabled:bg-gray-400',
  }

  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className={`${baseStyles} ${variants[variant]} ${className}`}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <span className="animate-spin">⏳</span>
          Processing...
        </span>
      ) : (
        children
      )}
    </button>
  )
}
