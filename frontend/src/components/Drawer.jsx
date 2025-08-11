// src/components/Drawer.jsx
export default function Drawer({ open, onClose, title, children }) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50">
      {/* overlay */}
      <div
        className="absolute inset-0 bg-black/30"
        onClick={onClose}
      />

      {/* panel */}
      <div
        className="absolute right-0 top-0 h-full w-full max-w-xl bg-white shadow-2xl flex flex-col"
        onClick={e => e.stopPropagation()} // prevent overlay click
      >
        {/* header (stays put) */}
        <div className="flex-none border-b bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">{title}</h2>
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border px-3 py-1.5 hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        </div>

        {/* body (scrolls) */}
        <div className="flex-1 overflow-y-auto p-4">
          {children}
        </div>
      </div>
    </div>
  )
}
