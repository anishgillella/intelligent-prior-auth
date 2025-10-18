export default function Card({ title, children, className = '' }) {
  return (
    <div className={`bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden ${className}`}>
      {title && (
        <div className="bg-gradient-to-r from-primary-50 to-primary-100 border-b border-primary-200 px-6 py-4">
          <h3 className="text-lg font-semibold text-primary-900">{title}</h3>
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  )
}
