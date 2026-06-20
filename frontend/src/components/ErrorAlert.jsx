export default function ErrorAlert({ message, onDismiss }) {
  return (
    <div className="alert alert-error mb-6 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <span className="text-lg">⚠️</span>
        <span>{message}</span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="font-semibold hover:underline whitespace-nowrap"
        >
          Dismiss
        </button>
      )}
    </div>
  );
}
