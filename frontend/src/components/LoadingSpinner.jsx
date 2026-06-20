export default function LoadingSpinner({ message = "Loading..." }) {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-primary-600" />
        <p className="mt-4 text-sm font-medium text-slate-600">{message}</p>
      </div>
    </div>
  );
}
