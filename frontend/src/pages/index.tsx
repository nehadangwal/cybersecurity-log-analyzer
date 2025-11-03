import { useEffect } from 'react';
import { useRouter } from 'next/router';

// This is the default page loaded at the root route ('/')
export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect the user from the root '/' to the login page
    router.replace('/login');
  }, [router]);

  // Return a simple loading message while the redirect happens
  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <p className="text-xl">Redirecting to Login...</p>
    </div>
  );
}