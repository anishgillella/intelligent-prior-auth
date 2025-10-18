export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 border-4 border-primary-200 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-transparent border-t-primary-600 rounded-full animate-spin"></div>
      </div>
      <p className="text-gray-600 font-medium">Processing workflow...</p>
      <p className="text-sm text-gray-500">This may take a few moments</p>
    </div>
  )
}
